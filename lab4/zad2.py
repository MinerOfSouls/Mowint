import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections.abc import Callable
import functools
import tqdm

def image_generator(n, chance = 0.5):
    image = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            r = np.random.random()
            if r < chance:
                image[i, j] = 1
            else:
                image[i, j] = -1
    return image

def display_image(image):
    plt.matshow(image, cmap="Greys")
    plt.show()

def animation_form_images(image_list, save = True, i=10):
    print("Prosessing...")
    fig, ax = plt.subplots()
    ims = []
    prev = None
    for i, image in enumerate(image_list):
        im = ax.matshow(image, cmap="Greys", animated=True)
        if i == 0:
            ax.matshow(image, cmap="Greys")
        ims.append([im])
    ani = animation.ArtistAnimation(fig, ims, interval=i, blit=True,
                                    repeat_delay=2000)
    if save:
        print("Saving...")
        ani.save("movie.mp4")
    plt.show()


def nb4(image: np.ndarray, coordinates: tuple):
    neighbours = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    n = image.shape[0]
    return [(coordinates[0] + i[0], coordinates[1] + i[1]) for i in neighbours 
           if 0 <= coordinates[0] + i[0] < n and 0 <= coordinates[1] + i[1] < n]

def nb8(image: np.ndarray, coordinates: tuple):
    neighbours = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    n = image.shape[0]
    return [(coordinates[0] + i[0], coordinates[1] + i[1]) for i in neighbours 
           if 0 <= coordinates[0] + i[0] < n and 0 <= coordinates[1] + i[1] < n]

def nb8_16(image: np.ndarray, coordinates: tuple):
    first = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    second = [(0, 2), (1, 2), (2, 2), (-1, 2), (-2, 2),
                  (-2, 1), (-2, 0), (-2, -1), (-2, -2),
                  (-1, -2), (0, -2), (1, -2), (2, -2),
                  (2, -1), (2, 0), (2, 1)]
    n = image.shape[0]
    a = [(coordinates[0] + i[0], coordinates[1] + i[1]) for i in first 
        if 0 <= coordinates[0] + i[0] < n and 0 <= coordinates[1] + i[1] < n]
    b = [(coordinates[0] + i[0], coordinates[1] + i[1]) for i in second 
        if 0 <= coordinates[0] + i[0] < n and 0 <= coordinates[1] + i[1] < n]
    return a, b

def same_colors_atract(image: np.ndarray, nb_func):
    value = 0
    n = image.shape[0]
    for i in range(n):
        for j in range(n):
            neighbours = nb_func(image, (i, j))
            for x, y in neighbours:
                if image[i, j] != image[x, y]:
                    value += 1
    return value

def atract_and_reppel(image: np.ndarray):
    value = 0
    n = image.shape[0]
    for i in range(n):
        for j in range(n):
            a, b = nb8_16(image, (i, j))
            for x, y in a:
                if image[i, j] != image[x, y]:
                    value += 1
            for x, y in b:
                if image[i, j] == image[x, y]:
                    value += 1
    return value

def ising_model(image: np.ndarray, nb_func, J):
    value = 0
    n = image.shape[0]
    for i in range(n):
        for j in range(n):
            nb = nb_func(image, (i, j))
            for x, y in nb:
                value += image[i, j]*image[x, y]*J
    return value

def acceptance(curr, next, temp):
    if next < curr:
        return True
    else:
        r = np.random.random()
        return r <= np.exp(-(next - curr)/temp)
    
def semi_random_neighbour(image: np.ndarray, temp_precent):
    n = image.shape[0]
    swaps = np.random.randint(0, n, (max(int((n//2)* n * temp_precent), 1), 2))
    for s in swaps:
        image[s[0], s[1]] = image[s[0], s[1]] * -1
    return swaps

def swap_two_points(image: np.ndarray):
    n = image.shape[0]
    one = np.random.randint(0, n, 2)
    two = np.random.randint(0, n, 2)
    while image[one[0], one[1]] == image[two[0], two[1]]:
        one = np.random.randint(0, n, 2)
    image[one[0], one[1]], image[two[0], two[1]] = image[two[0], two[1]], image[one[0], one[1]]
    return one, two


def get_energy_function(energy_mode = 1, nb_mode = 1, modifier = 1):
    if energy_mode == 1:
        if nb_mode == 1:
            return functools.partial(same_colors_atract, nb_func = nb4)
        elif nb_mode == 2:
            return functools.partial(same_colors_atract, nb_func = nb8)
    elif energy_mode == 2:
        return atract_and_reppel
    elif energy_mode == 3:
        if nb_mode == 1:
            return functools.partial(ising_model, nb_func = nb4, J = modifier)
        elif nb_mode == 2:
            return functools.partial(ising_model, nb_func = nb8, J = modifier)
        
def temperature(i, max_iter, L):
    x = 25*(i/max_iter) - 20
    return L/(1 + 1.2*np.exp(-x))

def image_anneal(n, black_conctrention, max_temp, max_iter, energy_mode, nb_mode, J = 1):
    energy = get_energy_function(energy_mode, nb_mode, J)
    current = image_generator(n, black_conctrention)
    values = []
    images = []

    minimum = current
    min_energy = energy(current)

    for i in tqdm.tqdm(range(max_iter, 0,  -1)):
        t = temperature(i, max_iter, max_temp)
        e = energy(current)
        values.append(e)
        images.append(current.copy())

        if e < min_energy:
            min_energy = e
            minimum = current

        o, tw = swap_two_points(current)
        e_prim = energy(current)
        if not acceptance(e, e_prim, t):
            current[o[0], o[1]], current[tw[0], tw[1]] = current[tw[0], tw[1]], current[o[0], o[1]]
    return minimum, min_energy, values, images

def example():
    img, min_e, values, images = image_anneal(50, 0.4, 5230, 5000, 1, 2)

    print(min_e)

    plt.plot(values)
    plt.show()
    display_image(img)
    animation_form_images(images, False)
