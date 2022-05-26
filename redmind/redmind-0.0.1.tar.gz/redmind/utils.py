import numpy as np

def one_hot_encode(position: int, num_classes: int):
    """
    One hot encodes a given class into a (1, num_classes) row vector
    """
    zero_vector = np.zeros((1, num_classes), dtype=int) 
    zero_vector[0][position] = 1
    # return 1d row vector
    return zero_vector.reshape(-1)