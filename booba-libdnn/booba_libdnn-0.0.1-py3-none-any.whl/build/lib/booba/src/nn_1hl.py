import copy
from tests.public_tests_nn1hl import *
from booba.utils.planar_utils import sigmoid


class NN1HiddenLayer:
    def __init__(self, X, Y, hidden_layer_size):
        """
        Arguments:
        X -- input dataset of shape (input size, number of examples1)
        Y -- labels of shape (output size, number of examples1)
        Instance Variables:
        n_x -- the size of the input layer
        n_h -- the size of the hidden layer
        n_y -- the size of the output layer
        params -- python dictionary containing your parameters:
            W1 -- weight matrix of shape (n_h, n_x)
            b1 -- bias vector of shape (n_h, 1)
            W2 -- weight matrix of shape (n_y, n_h)
            b2 -- bias vector of shape (n_y, 1)
        """
        self.n_x = X.shape[0]
        self.n_h = hidden_layer_size
        self.n_y = Y.shape[0]
        self.parameters = {}
        self.initialize_parameters()
        self.cache = {}
        self.cost = -1
        self.grads = {}

    def set_layer_sizes(self, new_n_x, new_n_h, new_n_y):
        self.n_x = new_n_x
        self.n_h = new_n_h
        self.n_y = new_n_y

    def set_parameters(self, new_parameters):
        """
        helper function for overwriting the parameters
        """
        self.parameters["W1"] = new_parameters["W1"]
        self.parameters["b1"] = new_parameters["b1"]
        self.parameters["W2"] = new_parameters["W2"]
        self.parameters["b2"] = new_parameters["b2"]

    def initialize_parameters(self):
        W1 = np.random.randn(self.n_h, self.n_x) * 0.01
        b1 = np.zeros((self.n_h, 1))
        W2 = np.random.randn(self.n_y, self.n_h) * 0.01
        b2 = np.zeros((self.n_y, 1))
        self.parameters = {"W1": W1,
                           "b1": b1,
                           "W2": W2,
                           "b2": b2}

    def forward_propagation(self, X):
        """
        Argument:
        X -- input data of size (n_x, m)
        parameters -- python dictionary containing your parameters (output of initialization function)

        Returns:
        A2 -- The sigmoid output of the second activation
        cache -- a dictionary containing "Z1", "A1", "Z2" and "A2"
        """
        # Retrieve each parameter from the dictionary "parameters"
        W1 = self.parameters["W1"]
        b1 = self.parameters["b1"]
        W2 = self.parameters["W2"]
        b2 = self.parameters["b2"]

        # Implement Forward Propagation to calculate A2 (probabilities)
        Z1 = np.dot(W1, X) + b1
        A1 = np.tanh(Z1)
        Z2 = np.dot(W2, A1) + b2
        A2 = sigmoid(Z2)
        assert (A2.shape == (1, X.shape[1]))
        self.cache = {"Z1": Z1,
                      "A1": A1,
                      "Z2": Z2,
                      "A2": A2}

    def compute_cost(self, Y):
        """
        Computes the cross-entropy cost given
        Arguments:
        A2 -- The sigmoid output of the second activation, of shape (1, number of examples1)
        Y -- "true" labels vector of shape (1, number of examples1)
        Returns:
        cost -- cross-entropy cost given equation (13)
        """
        A2 = self.cache["A2"]
        m = Y.shape[1]  # number of examples1
        # Compute the cross-entropy cost
        cost_raw = (-1 / m) * np.sum(np.dot(np.log(A2), Y.T) + np.dot(np.log(1 - A2), (1 - Y.T)))
        # OR
        # logprobs = np.multiply(np.log(A2),Y) + np.multiply((1-Y),np.log(1-A2))
        # cost_raw = (-1/m) * np.sum(logprobs)

        cost = float(np.squeeze(cost_raw))  # E.g., turns [[17]] into 17
        return cost

    def backward_propagation(self, X, Y):
        """
        Implement the backward propagation using the instructions above.

        parameters -- python dictionary containing our parameters
        cache -- a dictionary containing "Z1", "A1", "Z2" and "A2".
        X -- input data of shape (2, number of examples1)
        Y -- "true" labels vector of shape (1, number of examples1)
        grads -- python dictionary containing your gradients with respect to different parameters
        """
        m = X.shape[1]

        # First, retrieve W1 and W2 from the dictionary "parameters".
        W1 = self.parameters["W1"]
        W2 = self.parameters["W2"]
        # Retrieve also A1 and A2 from dictionary "cache".
        A1 = self.cache["A1"]
        A2 = self.cache["A2"]

        # Backward propagation: calculate dW1, db1, dW2, db2.
        dZ2 = A2 - Y
        dW2 = (1 / m) * np.dot(dZ2, A1.T)
        db2 = (1 / m) * np.sum(dZ2, axis=1, keepdims=True)
        dZ1 = np.dot(W2.T, dZ2) * (1 - np.power(A1, 2))
        dW1 = (1 / m) * np.dot(dZ1, X.T)
        db1 = (1 / m) * np.sum(dZ1, axis=1, keepdims=True)

        self.grads = {"dW1": dW1,
                      "db1": db1,
                      "dW2": dW2,
                      "db2": db2}

    def update_parameters(self, learning_rate=1.2):
        """
        Updates parameters using the gradient descent update rule given above
        parameters -- python dictionary containing your parameters
        grads -- python dictionary containing your gradients
        """
        # Retrieve a copy of each parameter from the dictionary "parameters". Use copy.deepcopy(...) for W1 and W2
        W1 = copy.deepcopy(self.parameters["W1"])
        b1 = self.parameters["b1"]
        W2 = copy.deepcopy(self.parameters["W2"])
        b2 = self.parameters["b2"]
        # Retrieve each gradient from the dictionary "grads"
        dW1 = self.grads["dW1"]
        db1 = self.grads["db1"]
        dW2 = self.grads["dW2"]
        db2 = self.grads["db2"]

        # Update rule for each parameter
        W1 = W1 - learning_rate * dW1
        b1 = b1 - learning_rate * db1
        W2 = W2 - learning_rate * dW2
        b2 = b2 - learning_rate * db2

        self.parameters = {"W1": W1,
                           "b1": b1,
                           "W2": W2,
                           "b2": b2}

    def train(self, X, Y, n_h, num_iterations=10000, print_cost=False):
        """
        X -- dataset of shape (2, number of examples1)
        Y -- labels of shape (1, number of examples1)
        num_iterations -- Number of iterations in gradient descent loop
        print_cost -- if True, print the cost every 1000 iterations
        parameters -- parameters learnt by the model. They can then be used to predict.
        """
        self.set_layer_sizes(X.shape[0], n_h, Y.shape[0])
        self.initialize_parameters()

        # Loop (gradient descent)
        for i in range(0, num_iterations):

            # Forward propagation. Inputs: "X, parameters". Updates: "A2, cache".
            self.forward_propagation(X)
            # Cost function. Inputs: "A2, Y". Outputs: "cost".
            cost = self.compute_cost(Y)
            # Backpropagation. Inputs: "parameters, cache, X, Y". Updates: "grads".
            self.backward_propagation(X, Y)
            # Gradient descent parameter update. Inputs: "parameters, grads". Updates: "parameters".
            self.update_parameters(learning_rate=1.2)

            # Print the cost every 1000 iterations
            if print_cost and i % 1000 == 0:
                print("Cost after iteration %i: %f" % (i, cost))

    def predict(self, X):
        """
        Using the learned parameters, predicts a class for each example in X
        parameters -- python dictionary containing your parameters
        X -- input data of size (n_x, m)
        predictions -- vector of predictions of our model (red: 0 / blue: 1)
        """

        # Computes probabilities using forward propagation, and classifies to 0/1 using 0.5 as the threshold.
        self.forward_propagation(X)
        predictions = (self.cache["A2"] > 0.5)

        return predictions
