import imageio.v3 as iio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
import image_processing
from tqdm import tqdm

def get_font(name):
    font = {filename.split(".")[0]: image_processing.flip(image_processing.gray(iio.imread(os.path.join(name, filename)))) for filename in os.listdir(name)}
    special = {"comma":",", "period":".", "zero":"0", "one":"1", "two":"2", "three":"3", "four":"4", "five":"5", "six":"6", "seven":"7", "eight":"8", "nine":"9", "question":"?", "exclam":"!"}
    for name, proper in special.items():
        val = font.pop(name)
        font[proper] = val
    return font


def calculate_correlation(image: np.ndarray, pattern: np.ndarray):
    return np.real(
        np.fft.ifft2(
            np.multiply(
                np.fft.fft2(image),
                np.fft.fft2(
                    np.rot90(pattern, 2),
                    image.shape
                ))
            )
    )

def get_letter_locations(image, pattern, thershold = 0.95):
    shape = image.shape
    d = (pattern.shape[0]//2, pattern.shape[1]//2)
    correlation = calculate_correlation(image, pattern)
    idxs = np.argpartition(correlation.flatten(), int(shape[0]*shape[1]*(thershold)))[int(-shape[0]*shape[1]*(1-thershold)):]
    rows, collumns = np.unravel_index(idxs, shape)
    locations = []
    for i in range(len(rows)):
        correlation[rows[i], collumns[i]]
        locations.append((correlation[rows[i], collumns[i]], rows[i]-d[0]+1, collumns[i]-d[1]+1))
    return locations

def find_blank_lines(projection):
    lines = []
    top = 0
    for i in range(1, len(projection)):
        if projection[i-1] == 0 and projection[i]>0:
            top = i-1
        elif projection[i-1] > 0 and projection[i] == 0:
            lines.append((top, i))
    return lines

def bouding_boxes(image):
    vertical = np.sum(image, axis = 1)
    boxes = []
    for top, bottom in find_blank_lines(vertical):
        line_img = image[top:bottom, :]
        horizontal = np.sum(line_img, axis = 0)
        for left, right in find_blank_lines(horizontal):
            x, y = left, bottom
            w = right - left
            h = top - bottom
            boxes.append((x, y, w, h))
    return boxes

def identify(image: np.ndarray, alphabet, thershold = 0.95, show = False):
    locations = {}
    for letter, letter_img in alphabet.items():
        locations[letter] = get_letter_locations(image, letter_img, thershold)
    boxes = bouding_boxes(image)
    curr_y = None
    last_right = None
    avg_dy = 0
    text = ""
    i = 0
    for x, y, w, h in tqdm(boxes):
        #Line recognition
        if curr_y == None:
            curr_y = y
        elif curr_y != y:
            text += "\n"
            curr_y = y
            last_right = None

        #Space recognition
        if last_right == None:
            last_right = x + w
        else:
            if avg_dy != 0 and x - last_right > avg_dy + 10:
                text += " "
            else:
                avg_dy = (avg_dy*i + last_right - x)/(i+1)
            last_right = x + w
        
        i += 1
        
        letter_detections = []

        bx, tx = min(x, x+w), max(x, x+w)
        by, ty = min(y, y + h), max(y, y + h)
        for letter, ll in locations.items():
            for score, cx, cy in ll:
            
                if bx <= cy <= tx and by <= cx <= ty:
                    letter_detections.append((score, letter))
        if not letter_detections:
            text += "#"
            continue
        text += max(letter_detections, key=lambda d: d[0])[1]
    return text
        