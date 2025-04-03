import numpy as np
import matplotlib.pyplot as plt
import scipy as sci

def generate_uniform_points(n, l, h):
    return np.random.uniform(l, h, (n, 2))

def generate_normal_points(n, a, b, c ,d):
    sigma = np.array([[a, b], [c, d]])
    return np.random.multivariate_normal(0, sigma, (n, 2))

def generate_9_groups(n, r, l, h):
    group_centers = np.random.uniform(l, h, 9)
    vectored_points = [np.array([(np.random.uniform(0, r, 1), np.random.uniform(0, np.pi)) for i in range(n//9)]) for j in range(9)]
    return np.array([group_centers[i]+np.array([v[0]*np.cos(v[1]), v[0]*np.sin(v[1])]) for v in vectored_points[i] for i in range(9)])

def distance(x, y):
    return np.pow(x[0]-y[0], 2) + np.pow(x[1]-y[1], 2)

def tsp_f(x, points):
    sum = 0
    for i in range(len(x)-1):
        sum += distance(points[x[i]], points[x[i+1]])
    sum += distance(points[x[0]], points[x[-1]])
    return sum

def e_f(maxtmp, currtmp, k):
    r = np.random.random()
    min_high = 0.5/(1+np.pow(np.e, -k*(currtmp - 2*maxtmp//3)))
    if r < min_high:
        return 1
    else: 
        return 0

def anealing_rand(func, n, max_temp, k, points):
    space = np.array([i for i in range(n)])
    np.random.shuffle(space)
    min_state = np.copy(space)
    t = max_temp
    values = []
    while t > 0:
        values.append(func(space, points))
        i = np.random.randint(0, n)
        j = np.random.randint(0, n)
        curr = func(space, points)
        space[i], space[j] = space[j], space[i]
        nekst = func(space, points)
        c = e_f(max_temp, t, k)
        if curr < nekst and c == 1:
            pass
        elif curr < nekst and c == 0:
            space[i], space[j] = space[j], space[i]
        elif nekst < curr and c == 1:
            min_state = np.copy(space)
            space[i], space[j] = space[j], space[i]
        elif nekst < curr and c == 0:
            min_state = np.copy(space)
        t = t-1
    plt.plot(values)
    plt.show()
    return min_state, func(min_state, points)

def anealing_succ(func, n, max_temp, k, points):
    space = np.array([i for i in range(n)])
    np.random.shuffle(space)
    min_state = np.copy(space)
    t = max_temp
    values = []
    while t > 0:
        values.append(func(space, points))
        i = np.random.randint(0, n-1)
        curr = func(space, points)
        space[i], space[i+1] = space[i+1], space[i]
        nekst = func(space, points)
        c = e_f(max_temp, t, k)
        if curr < nekst and c == 1:
            pass
        elif curr < nekst and c == 0:
            space[i], space[i+1] = space[i+1], space[i]
        elif nekst < curr and c == 1:
            min_state = np.copy(space)
            space[i], space[i+1] = space[i+1], space[i]
        elif nekst < curr and c == 0:
            min_state = np.copy(space)
        t = t-1
    plt.plot(values)
    plt.show()
    return min_state, func(min_state, points)


anealing_succ(tsp_f, 50, 1000, 0.1, generate_uniform_points(50, 0, 100))