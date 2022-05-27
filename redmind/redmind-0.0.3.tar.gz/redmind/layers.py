from abc import ABC, abstractmethod
import numpy as np

class Layer(ABC):
    """
    Base layer class.

    All layers must inherit from this class
    because the NN works with Layer objects
    """

    def __init__(self) -> None:
        self.forward_inputs = None
        self.forward_outputs = None
        self.backward_inputs = None
        self.backward_outputs = None
        self._train = False

    def __repr__(self, extra_fields = {}):
        return str({'Type:': type(self).__name__, 
                'forward_inputs': self.forward_inputs,
                'forward_outputs': self.forward_outputs,
                'backward_inputs': self.backward_inputs,
                'backward_outputs': self.backward_outputs, 
                **extra_fields})
    
    @abstractmethod
    def forward(self, x: np.ndarray = None, **kwargs):
        pass

    @abstractmethod
    def backward(self, output_gradient: float = None, **kwargs):
        pass

    def get_train(self):
        return self._train

    def set_train(self, state):
        assert type(state) == bool
        self._train = state

    @abstractmethod
    def get_gradients():
        """
        This should return all the gradients as dictionary
        """
        pass
    
class Dense(Layer):
    def __init__(self, n_rows: int = None, n_columns: int = None, weight_init_scale = 0.1) -> None:
        self.weights = np.random.randn(n_rows, n_columns) * weight_init_scale
        self.bias = np.random.randn(n_rows, 1)
        self.bias_prime = None
        self.weights_prime = None
        super().__init__()

    def __repr__(self):
        fields = {'weights': self.weights, 'bias': self.bias}
        return super().__repr__(extra_fields = fields)

    def forward(self, x: np.ndarray = None, **kwargs) -> np.ndarray:
        self.forward_inputs = x
        self.forward_outputs = np.dot(self.weights, self.forward_inputs) + self.bias
        return self.forward_outputs

    def backward(self, output_gradient: float = None, **kwargs) -> np.ndarray:
        self.backward_inputs = output_gradient
        self.backward_outputs = np.dot(self.weights.T, self.backward_inputs)
        self.update_params(learning_rate=kwargs['learning_rate'])
        return self.backward_outputs

    def update_params(self, learning_rate: float = 0.1) -> None:
        # compute gradients
        self.weights_prime = np.dot(self.backward_inputs, self.forward_inputs.T)
        self.bias_prime = np.sum(self.backward_inputs, axis=1, keepdims=True)
        # update w and b
        self.weights = self.weights - (self.weights_prime * learning_rate)
        self.bias = self.bias - (self.bias_prime * learning_rate)
        return None

    def get_gradients(self):
        return {'dW': self.weights_prime, 'db': self.bias_prime, 'dZ': self.backward_outputs}

    def modify_weights_and_biases(self, val=0):
        self.weights += val
        self.bias += val

class Dropout(Layer):
    def __init__(self, drop_prob: float = 0) -> None:
        assert 0 <= drop_prob < 1, "Drop probability rate should be between 0 and 0.9"
        self.drop_prob = drop_prob
        self.keep_prob = 1 - self.drop_prob
        super().__init__()

    def forward(self, x: np.ndarray = None, **kwargs) -> np.ndarray:
        self.forward_inputs = x
        matrix_probs = [self.drop_prob, 1 - self.drop_prob]
        if self._train:
            matrix_probs = [self.drop_prob, 1 - self.drop_prob]
            self.drop_matrix = np.random.choice([0, 1], size=x.shape, p=matrix_probs)
            self.forward_outputs = np.multiply(self.drop_matrix, self.forward_inputs) / self.keep_prob
        else:
            self.forward_outputs = self.forward_inputs
        return self.forward_outputs

    def backward(self, output_gradient: float = None, **kwargs) -> np.ndarray:
        self.backward_inputs = output_gradient
        self.backward_outputs = np.multiply(self.drop_matrix, output_gradient) / self.keep_prob
        return self.backward_outputs

    # not implementing this methods in dropout
    def get_gradients(self):
        pass

###################
# Activation Layers
###################

class ActivationLayer(Layer):
    def __init__(self, activation, activation_prime) -> None:
        self.activation = activation
        self.activation_prime = activation_prime
        super().__init__()

    def forward(self, x, **kwargs) -> np.ndarray:
        self.forward_inputs = x
        self.forward_outputs = self.activation(self.forward_inputs)
        return self.forward_outputs

    def backward(self, output_gradient: float = None, **kwargs) -> np.ndarray:
        self.backward_inputs = output_gradient
        self.backward_outputs = self.backward_inputs * self.activation_prime(self.forward_inputs)
        return self.backward_outputs

    def get_gradients(self):
        return {'dA': self.backward_outputs}

class Sigmoid(ActivationLayer):
    def __init__(self) -> None:
        sigmoid = lambda x: 1 / (1 + np.exp(-x))
        sigmoid_prime = lambda x: sigmoid(x) * (1 - sigmoid(x))
        super().__init__(sigmoid, sigmoid_prime)

class ReLU(ActivationLayer):
    def __init__(self) -> None:
        relu = lambda x: np.maximum(0, x)
        relu_prime = lambda x: (x>0).astype(x.dtype)
        super().__init__(relu, relu_prime)