import numpy as np

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
        A[i,i:] = A[i, i:] / A[i,i]
        for j in range(i+1,N):
            m = A[j, i]*A[i,i]
            A[j, i:] = A[j, i:] - (A[i, i:]*A[j, i])
            A[j, i] = m
    return A

print(lu_factor(np.array([
    [1.0,2.0,3.0],
    [4.0,5.0,7.0],
    [7.0,8.0,9.0]
])))
