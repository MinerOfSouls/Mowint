import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as image

def draw_path(points, path):
    for i in range(len(path)-1):
        first = points[path[i]]
        second = points[path[i+1]]
        line_x = [first[0], second[0]]
        line_y = [first[1], second[1]]
        plt.plot(line_x, line_y, 'b')
    first = points[path[-1]]
    second = points[path[0]]
    line_x = [first[0], second[0]]
    line_y = [first[1], second[1]]
    plt.plot(line_x, line_y, 'b')
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    plt.scatter(x, y)
    plt.show()

def anim_help(points, path, ax):
    for i in range(len(path)-1):
        first = points[i]
        second = points[i+1]
        line_x = [first[0], second[0]]
        line_y = [first[1], second[1]]
        ax.plot(line_x, line_y)
    first = points[path[-1]]
    second = points[path[0]]
    line_x = [first[0], second[0]]
    line_y = [first[1], second[1]]
    plt.plot(line_x, line_y)
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    ax.scatter(x, y)

def animate_path(points, paths):
    fig, ax = plt.subplots()
    ims = []
    for i, path in enumerate(paths):
        anim_help(points, path, ax)
        ims.append([image.AxesImage(ax)])
        ax.clear()
    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True,
                                    repeat_delay=1000)
    plt.show()


def generate_uniform_points(n, l, h):
    return np.random.uniform(l, h, (n, 2))

def generate_normal_points(n, a, b, c ,d):
    sigma = np.array([[a, b], [c, d]])
    return np.random.multivariate_normal((0, 0), sigma, n)

def generate_9_groups(n, r, l, h):
    group_centers = np.random.uniform(l, h, (9, 2))
    vectored_points = [[(np.random.uniform(0, r), np.random.uniform(0, 2*np.pi)) for i in range(n//9)] for j in range(9)]
    return np.array([group_centers[i]+np.array([v[0]*np.cos(v[1]), v[0]*np.sin(v[1])]) for i in range(9) for v in vectored_points[i]])

def distance(x, y):
    return np.pow(x[0]-y[0], 2) + np.pow(x[1]-y[1], 2)

def tsp_f(x, points):
    sum = 0
    for i in range(len(x)-1):
        sum += distance(points[x[i]], points[x[i+1]])
    sum += distance(points[x[0]], points[x[-1]])
    return sum

def e_f(curr, next, temp):
    r = np.random.random()
    min_high = np.exp(-(next-curr)/temp)
    if r < min_high:
        return True
    else: 
        return False

def temperature(i, max_iter, L):
    x = 12*(i/max_iter) - 6
    return L/(1 + np.exp(-x))

def anealing_rand(n, max_temp, max_iter, points):
    space = np.array([i for i in range(n)])
    np.random.shuffle(space)
    min_state = np.copy(space)
    values = []
    states = []
    for i in range(max_iter, 0, -1):
        t = temperature(i, max_iter, max_temp)
        states.append(space)
        values.append(tsp_f(space, points))
        i = np.random.randint(0, n)
        j = np.random.randint(0, n)
        curr = tsp_f(space, points)
        space[i], space[j] = space[j], space[i]
        nekst = tsp_f(space, points)
        accept = e_f(curr, nekst, t)
        if curr < nekst and accept:
            pass
        elif curr < nekst and not accept:
            space[i], space[j] = space[j], space[i]
        elif nekst < curr:
            min_state = np.copy(space)
        t = t-1
    plt.plot(values)
    plt.show()
    return min_state, tsp_f(min_state, points)

def anealing_succ(n, max_temp, max_iter, points):
    space = np.array([i for i in range(n)])
    np.random.shuffle(space)
    min_state = np.copy(space)
    t = max_temp
    values = []
    states = []
    for i in range(max_iter, 0, -1):
        t = temperature(i, max_iter, max_temp)
        states.append(space)
        values.append(tsp_f(space, points))
        i = np.random.randint(0, n-1)
        curr = tsp_f(space, points)
        space[i], space[i+1] = space[i+1], space[i]
        nekst = tsp_f(space, points)
        accept = e_f(curr, nekst, t)
        if curr < nekst and accept:
            pass
        elif curr < nekst and not accept:
            space[i], space[i+1] = space[i+1], space[i]
        elif nekst < curr:
            min_state = np.copy(space)
    plt.plot(values)
    plt.show()
    return min_state, tsp_f(min_state, points)
