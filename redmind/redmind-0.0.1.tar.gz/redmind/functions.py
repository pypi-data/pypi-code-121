import numpy as np

def mse(y, y_pred):
    return np.mean(np.power(y_pred - y, 2))
    
def mse_prime(y, y_pred):
    return 2 * (y_pred - y) / np.size(y)

def binary_cross_entropy(y ,y_pred):
    return np.mean(-y * np.log(y_pred) - (1 - y) * np.log(1 - y_pred))

def binary_cross_entropy_prime(y, y_pred):
    return ((1 - y) / (1 - y_pred) - y / y_pred) / np.size(y)