from scipy.special import expit
import numpy as np

def fill_diagonal3d(arr, x):
    row, col, prof = np.diag_indices_from(arr)
    arr[row, col, prof] = x
    return arr
# 
def fill_diagonal4d(arr, x):
    row, col, prof, cub = np.diag_indices_from(arr)
    arr[row, col, prof, cub] = x
    return arr

def activation_function(func: str):
    def identity(x):
        return x
    def relu(x):
        return x * (x > 0)
    actfunc = {
        'logistic': expit,
        'identity': identity,
        'tanh': np.tanh,
        'relu': relu
        }
    return actfunc[func]

def der_activation_function(func: str):
    def sigmoid(x):
        fx = expit(x)
        return np.diag(fx * (1 - fx))
    def identity(x):
        return np.identity(x.shape[0], dtype=int)
    def tanh(x):
        return np.diag(1 - np.tanh(x) ** 2)
    def relu(x):
        return np.diag(x > 0) 
    deractfunc = {
        'logistic': sigmoid,
        'identity': identity,
        'tanh': tanh,
        'relu': relu
        }
    return deractfunc[func]

def der_2_activation_function(func: str):
    def sigmoid(x):
        zeros_3d = np.zeros((x.shape[0],x.shape[0],x.shape[0]),dtype=float)
        fx = expit(x)
        return fill_diagonal3d(zeros_3d, fx * (1 - fx) * (1 - 2 * fx))
    def identity(x):
        return np.zeros((x.shape[0],x.shape[0],x.shape[0]), dtype=int)
    def tanh(x):
        zeros_3d = np.zeros((x.shape[0],x.shape[0],x.shape[0]),dtype=float)
        fx = tanh(x)
        return fill_diagonal3d(zeros_3d, -2 * fx * (1 - fx^2))
    def relu(x):
        return np.zeros((x.shape[0],x.shape[0],x.shape[0]), dtype=int)
    der2actfunc = {
        'logistic': sigmoid,
        'identity': identity,
        'tanh': tanh,
        'relu': relu
        }
    return der2actfunc[func]

def der_3_activation_function(func: str):
    def sigmoid(x):
        zeros_4d = np.zeros((x.shape[0],x.shape[0],x.shape[0], x.shape[0]),dtype=float)
        fx = expit(x)
        return fill_diagonal4d(zeros_4d, fx * (1 - fx) * (1 - 2 * fx) * (1 - 3 * fx))
    def identity(x):
        return np.zeros((x.shape[0],x.shape[0],x.shape[0],x.shape[0]), dtype=int)
    def tanh(x):
        zeros_4d = np.zeros((x.shape[0],x.shape[0],x.shape[0], x.shape[0]),dtype=float)
        fx = tanh(x)
        return fill_diagonal4d(zeros_4d, -2 * (1 - 4 * fx ** 2 + fx ** 4))
    def relu(x):
        return np.zeros((x.shape[0],x.shape[0],x.shape[0],x.shape[0]), dtype=int)
    der3actfunc = {
        'logistic': sigmoid,
        'identity': identity,
        'tanh': tanh,
        'relu': relu
        }
    return der3actfunc[func]