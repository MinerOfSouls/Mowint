import numpy as np
import matplotlib.pyplot as plt
import random

def read_sudoku(filename):
    sudoku = np.zeros((9, 9))
    counts = [9 for _ in range(9)]
    fixed = set()
    f = open(filename)
    for i, line in enumerate(f):
        for j, c in enumerate(line):
            if c != 'x' and c != '\n':
                no = int(c)
                sudoku[i, j] = no
                counts[no-1] -= 1
                fixed.add((i, j))
    for i in range(9):
        for j in range(9):
            if (i, j) not in fixed:
                no = random.choice([i+1 for i in range(9) if counts[i] > 0])
                counts[no - 1] -= 1
                sudoku[i, j] = no
    return sudoku, fixed

def energy(sudoku: np.ndarray):
    s = (9 - len(np.unique(sudoku[0:3, 0:3])) +
            9 - len(np.unique(sudoku[3:6, 3:6])) + 
            9 - len(np.unique(sudoku[6:9, 6:9])))
    for i in range(9):
        s += 9 - len(np.unique(sudoku[0:9, i]))
        s += 9 - len(np.unique(sudoku[i, 0:9]))
    return s

def acceptance(curr, next, temp):
    if next < curr:
        return True
    else:
        r = np.random.random()
        return r <= np.exp(-(next - curr)/temp)
    
def temperature(i, max_iter, L):
    x = 25*(i/max_iter) - 25
    return L/(1 + np.exp(-x))
    
def anneal_sudoku(sudoku, fixed, max_iter, max_temp):
    min_value = energy(sudoku)
    values = []
    for i in range(max_iter):
        t = temperature(max_iter-i, max_iter, max_temp)
        curr = energy(sudoku)
        if curr < min_value:
            min_value = curr
        if curr == 0:
            break
        values.append(curr)
        one = (random.randint(0, 8), random.randint(0, 8))
        two = (random.randint(0, 8), random.randint(0, 8))
        while one == two or one in fixed or two in fixed:
            if one == two or one in fixed:
                one = (random.randint(0, 8), random.randint(0, 8))
            if two in fixed:
                two = (random.randint(0, 8), random.randint(0, 8))
        sudoku[one[0], one[1]], sudoku[two[0], two[1]] = sudoku[two[0], two[1]], sudoku[one[0], one[1]]
        new = energy(sudoku)
        if not acceptance(curr, new, t):
            sudoku[one[0], one[1]], sudoku[two[0], two[1]] = sudoku[two[0], two[1]], sudoku[one[0], one[1]]
    return min_value, values

sudoku, fixed = read_sudoku("sudoku.txt")
m, values = anneal_sudoku(sudoku, fixed, 5000, 5000)
print(m)
plt.plot(values)
plt.show()