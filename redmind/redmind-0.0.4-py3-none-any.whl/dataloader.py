import numpy as np
import random
import math

class Dataloader():
    """
    Dataloader class utilized to create iterable lists of labeled numpy matrices
    
    Each iteration on the dataloader object returns a matrix containing 
    features and labeled outputs for those features

    Warning: Make sure you input both X and Y as column vectors
    """
    def __init__(self, X: np.ndarray, Y: np.ndarray, batch_size: int = 1):
        """
        inputs
        ---
        X: Matrix of features X as column vectors
        Y: Output labels Y as column vectors
        batch_size: number of elements per batch. Defaults to 1
        """
        self.X = X
        self.Y = Y
        self.batch_size = batch_size
        self.validate_data()
        self.n_batches = math.ceil(self.X.shape[1] / self.batch_size)
        self._iter_index = 0

    def __iter__(self):
        return self
    
    def __len__(self):
        return self.n_batches

    def __next__(self):
        position = self._iter_index * self.batch_size
        if self._iter_index >= len(self):
            # reset iter and stop current iteration
            self._iter_index = 0
            raise StopIteration
        x = self.X[:, position:position+self.batch_size]
        y = self.Y[:, position:position+self.batch_size]
        self._iter_index += 1
        return x, y

    def __repr__(self):
        return f"Dataloader(X: {self.X.shape}, Y: {self.Y.shape}, n_batches: {self.n_batches}, batch_size: {self.batch_size})"

    def validate_data(self):
        """
        Runs input data validations
        """
        assert type(self.X) == np.ndarray, "X is not a numpy array"
        assert type(self.Y) == np.ndarray, "Y is not a numpy array"
        assert self.X.shape[1] == self.Y.shape[1], "X and Y do not have the same number of columns/items"
        assert type(self.batch_size) == int, "batch_size should be integer value"
        assert math.floor(self.X.shape[1] / self.batch_size) >= 1, f"X matrix is not divisible by {self.batch_size}. Enter a valid batch size"
    
    def get_random_element(self):
        """
        Returns a single random element with its features and label
        """
        elem = random.randint(0, len(self))
        x = self.X[:, elem].reshape(self.X.shape[0], 1)
        y = self.Y[:, elem]
        return x, y

    def shuffle(self) -> None:
        """
        Shuffles X and Y, with features and labels pairs maintained
        """
        x = self.X.T
        y = self.Y.T
        p = np.random.permutation(len(x))
        self.X = x[p].T
        self.Y = y[p].T