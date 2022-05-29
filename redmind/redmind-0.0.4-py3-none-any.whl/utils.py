import numpy as np
import dill
from redmind.network import NeuralNetwork

def one_hot_encode(position: int, num_classes: int):
    """
    One hot encodes a given class into a (1, num_classes) row vector
    """
    zero_vector = np.zeros((1, num_classes), dtype=int) 
    zero_vector[0][position] = 1
    # return 1d row vector
    return zero_vector.reshape(-1)

def save_model(nn: NeuralNetwork, filename: str = 'nn.dill') -> None:
    if isinstance(nn, NeuralNetwork):
        print(f"Saving Neural Network into {filename}")
        with open(filename, 'wb') as f:
            dill.dump(nn, f)
    else:
        print("Please provide a valid Neural Network")
    return None

def load_model(filename: str = 'nn.dill') -> NeuralNetwork:
    print(f"Loading NN {filename}")
    with open(filename, 'rb') as f:
        nn = dill.load(f)
    return nn