import imageio.v3 as iio
import numpy as np
import matplotlib.pyplot as plt
from skimage import feature
import skimage.transform as transform
import skimage.filters as filters

def gray(image: np.ndarray):
    shape = image.shape
    grey = np.zeros((shape[0], shape[1]))
    for i in range(shape[0]):
        for j in range(shape[1]):
            grey[i, j] = (0.3*image[i, j, 0] + 0.59*image[i, j, 1] + 0.11*image[i, j, 2])
    return grey

def flip(image: np.ndarray):
    return 255 - image

def polar2cartesian(radius, angle):
    return radius * np.array([np.cos(angle), np.sin(angle)])

def hough_transform(image: np.ndarray, show = False):
    acc, angles, d = transform.hough_line(feature.canny(image, sigma=5))
    
    if show:
        plt.matshow(acc, aspect=0.1)
        plt.show()

    acc, angles, d = transform.hough_line_peaks(acc, angles, d, threshold=0.6*np.max(acc))

    return np.vstack([d, angles]).T

def show_lines(image, lines):
    for rho, theta in lines:
        x0 = polar2cartesian(rho, theta)
        direction = np.array([x0[1], -x0[0]])
        pt1 = np.round(x0 + 1000*direction).astype(int)
        pt2 = np.round(x0 - 1000*direction).astype(int)
        plt.axline(pt1, pt2)
    plt.imshow(image, cmap="gist_gray")
    plt.show()

def show_image(image):
    plt.imshow(image, cmap="gist_gray")
    plt.show()

def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else np.zeros(len(d))
    return data[s<m]

def ajust_rotatation(image, show = False):
    lines = hough_transform(image, show)
    if show:
        show_lines(image, lines)
    un_rotated = transform.rotate(image, 270 + np.rad2deg(lines[0, 1]), resize = True, mode = "edge")
    if show: show_image(un_rotated)
    first = np.argmax(feature.canny(un_rotated, sigma=5), axis = 1)
    first = first[first > 0]
    last = np.argmax(np.rot90(np.rot90(feature.canny(un_rotated, sigma=5))), axis = 1)
    last = last[last > 0]
    out_f = reject_outliers(first)
    out_l = reject_outliers(last)
    if abs(max(out_f) - min(out_f)) > abs(max(out_l) - min(out_l)):
        un_rotated = transform.rotate(un_rotated, 180, resize = True, mode = "edge")
        if show: show_image(un_rotated)
    return un_rotated

def crop_in(image):
    trues = np.argwhere(image)
    top_left = trues.min(axis=0)
    bottom_right = trues.max(axis=0)
    out = image[top_left[0]:bottom_right[0]+1,
          top_left[1]:bottom_right[1]+1]
    return np.pad(out, ((40, 40), (40, 40)))

def prepare_image(image, show = False):
    image = gray(image)
    image = flip(image)
    image = ajust_rotatation(image, show)
    image[image < 150] = 0
    image = crop_in(image)
    if show: show_image(image)
    return image
