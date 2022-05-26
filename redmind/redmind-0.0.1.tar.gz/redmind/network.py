from redmind.layers import Layer, Dense
import numpy as np
import redmind.functions as fn
import matplotlib.pyplot as plt
from typing import List
from redmind.dataloader import Dataloader

class NeuralNetwork:
    def __init__(self, layers: List[Layer], verbose=False, cost_function = fn.mse, grad_function = fn.mse_prime) -> None:
        self.layers = layers
        self.costs = {}
        self._verbose = verbose
        self.cost_function = cost_function
        self.grad_function = grad_function
        if self._verbose:
            print(f"Neural Network initialized with {len(self.layers)} layers")

    def details(self) -> None:
        for index, layer in enumerate(self.layers):
            print(f"Layer {index + 1} {layer}")

    def forward(self, x: np.ndarray = None) -> np.ndarray:
        out = x
        for layer in self.layers:
            out = layer.forward(x = out)
        return out

    def backward(self, gradient: float = None, learning_rate: float = None) -> None:
        grad = gradient
        for layer in reversed(self.layers):
            grad = layer.backward(output_gradient=grad, learning_rate=learning_rate)
        return None

    def predict(self, x: np.ndarray = None):
        return self.forward(x)

    def set_train(self, state=False):
        if self._verbose:
            print(f"updating NN layers training to: {state}")
        for layer in self.layers:
            layer.set_train(state=state)

    def set_verbose(self, state):
        assert type(state) == bool
        self._verbose = state

    def train(self, X=None, Y=None, epochs=20, n_batches=1, learning_rate=0.1):
        data = Dataloader(X=X, Y=Y, n_batches=n_batches)
        #print(data)
        self.set_train(state=True)
        if self._verbose:
            if n_batches > 1:
                print(f"Starting train with {n_batches} batches of size {data} ")
        for epoch in range(epochs):
            for x, y in data:
                # forward
                y_pred = self.forward(x=x)
                # calculate error and cost
                cost = self.cost_function(y, y_pred)
                self.costs[epoch] = cost
                error_gradient = self.grad_function(y, y_pred)
                # backward
                self.backward(gradient=error_gradient, learning_rate=learning_rate)
            # print cost to console
            if self._verbose:
                print(f"epoch: {epoch + 1}/{epochs}, cost: {round(self.costs[epoch], 4)}, accuracy: {round(100 - (self.costs[epoch] * 100), 2)}%")
        self.set_train(state=False)

    def graph_costs(self) -> None:
        plt.plot(list(self.costs.keys()), list(self.costs.values()))
        plt.xlabel("Epoch")
        plt.ylabel("Cost")
        plt.show()

    
    # PENDING CORRECT IMPLEMENTATION
    # def grad_check(self, X=None, Y=None, epsilon=1e-7):
    #     """
    #     Performs gradient checking and returns the norm of difference / norm of the sum (scalar)
    #     """
    #     # get weights and biases on Dense layers only
    #     dense_weights = np.empty(0)
    #     dense_bias = np.empty(0)

    #     for layer in self.layers:
    #         if isinstance(layer, Dense):
    #             dense_weights = np.append(dense_weights, layer.weights.ravel())
    #             dense_bias = np.append(dense_bias, layer.bias.ravel())
    #     parameters = np.concatenate((dense_weights, dense_bias))
    #     if self._verbose:
    #         print(parameters)

    #     # Get gradients for all layers
    #     network_grads = np.empty(0)
        
    #     for layer in self.layers:
    #         layer_grad = layer.get_gradients()
    #         for k, v in layer_grad.items():
    #             assert type(v) == np.ndarray, "Element must be a numpy array"
    #             network_grads = np.append(network_grads, v.ravel())
    #     if self._verbose:
    #         print(network_grads)

    #     num_parameters = parameters.shape[0]
    #     J_plus = np.zeros((num_parameters, 1))
    #     J_minus = np.zeros((num_parameters, 1))
    #     gradapprox = np.zeros((num_parameters, 1))

    #     for i in range(num_parameters):
    #         # Thetaplus
    #         # add epsilon to weights and biases in dense layers
    #         for layer in self.layers:
    #             if isinstance(layer, Dense):
    #                 layer.modify_weights_and_biases(val=epsilon)
    #         J_plus[i] = self.cost_function(Y, self.predict(x=X))

    #         for layer in self.layers:
    #             if isinstance(layer, Dense):
    #                 layer.modify_weights_and_biases(val=-epsilon)

    #         # Thetaminus
    #         # subtract epsilon to weights and biases in dense layers
    #         for layer in self.layers:
    #             if isinstance(layer, Dense):
    #                 layer.modify_weights_and_biases(val=-epsilon)

    #         J_minus[i] = self.cost_function(Y, self.predict(x=X))
    #         for layer in self.layers:
    #             if isinstance(layer, Dense):
    #                 layer.modify_weights_and_biases(val=epsilon)

    #         gradapprox[i] = (J_plus[i] - J_minus[i]) / (2 * epsilon)

    #     print(J_plus)
    #     print("---")
    #     print(J_minus)
        
    #     print(gradapprox)
    #     numerator = np.linalg.norm(network_grads - gradapprox)
    #     denominator = np.linalg.norm(network_grads) + np.linalg.norm(gradapprox)
    #     difference = numerator / denominator
        
    #     # YOUR CODE ENDS HERE
    #     if self._verbose:
    #         if difference > 2e-7:
    #             print ("\033[93m" + "There is a mistake in the backward propagation! difference = " + str(difference) + "\033[0m")
    #         else:
    #             print ("\033[92m" + "Your backward propagation works perfectly fine! difference = " + str(difference) + "\033[0m")

    #     return difference


