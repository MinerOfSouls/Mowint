import numpy as np
import time as time

def gauss_solve(equation: np.array, A: np.array):
    assert equation.shape[0] ==  equation.shape[1]
    assert A.shape[0] == equation.shape[0]

    N = equation.shape[0]

    equation = np.column_stack((equation, A))
    for i in range(N):
        a_max = i
        for j in range(i+1, N):
            if abs(equation[j,i]) > abs(equation[a_max, i]):
                a_max = j
        equation[i], equation[a_max] = equation[a_max], equation[i]
        equation[i] = equation[i] / equation[i,i]
        for j in range(N):
            if j == i:
                continue
            equation[j] = equation[j] - (equation[i]*equation[j, i])
    
    solution = equation[:, -1]
    
    return solution

def lu_factor(A: np.array):

    assert A.shape[0] ==  A.shape[1]

    N = A.shape[0]
    for i in range(N):
        for j in range(i+1,N):
            m = A[j, i]/A[i,i]
            A[j, i:] = A[j, i:] - (A[i, i:]*m)
            A[j, i] = m
    return A

def test_LU():
    random_matrix = [
    np.random.rand(6, 6),
    np.random.rand(500, 500),
    np.random.rand(750, 750),
    np.random.rand(1000, 1000),
    np.random.rand(2000, 2000)]

    for A in random_matrix:
        copy = A.copy()
        LU = lu_factor(A)
        L = np.zeros(shape=LU.shape)
        U = np.zeros(shape=LU.shape)
        for i in range(LU.shape[0]):
            L[i,:i] = LU[i,:i]
            L[i,i] = 1
            U[i, i:] = LU[i, i:]
        print(np.linalg.matrix_norm(copy - np.matmul(L, U)))

def test_solve():
    random_matrix = [
    np.random.rand(6, 6),
    np.random.rand(500, 500),
    np.random.rand(750, 750),
    np.random.rand(1000, 1000),
    np.random.rand(2000, 2000)]
    random_spaces = [
        np.random.rand(500),
        np.random.rand(500),
        np.random.rand(750),
        np.random.rand(1000),
        np.random.rand(2000)]

    for i in range(5):
        start = time.process_time()
        sol_A = gauss_solve(random_matrix[i], random_spaces[i])
        end1 = time.process_time()
        sol_B = np.linalg.solve(random_matrix[i], random_spaces[i])
        end2 = time.process_time()
        print(random_matrix[i].shape, end1-start, end2-end1)
