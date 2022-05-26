"""Class definition for SurrogateModel, the base class for all surrogate models.
"""
import abc


class SurrogateModel(abc.ABC):
    """Abstract interface for surrogate models.
    """

    @abc.abstractmethod
    def train(self, x, y):
        """
        Train the surrogate model with the given set of inputs and outputs.

        Parameters
        ----------
        x : array-like
            Training input locations
        y : array-like
            Model responses at given inputs.
        """
        pass

    @abc.abstractmethod
    def predict(self, x):
        """
        Calculate a predicted value of the response based on the current trained model.

        Parameters
        ----------
        x : array-like
            Point(s) at which the surrogate is evaluated.
        """
        pass


class MultiFiSurrogateModel(SurrogateModel):
    """
    Base class for surrogate models using multi-fidelity training data.
    """

    def train(self, x, y):
        """
        Calculate a predicted value of the response based on the current trained model.

        Parameters
        ----------
        x : array-like
            Point(s) at which the surrogate is evaluated.
        y : array-like
            Model responses at given inputs.
        """
        self.train_multifi([x], [y])

    @abc.abstractmethod
    def train_multifi(self, x, y):
        """
        Train the surrogate model, based on the given multi-fidelity training data.

        Parameters
        ----------
        x : list of (m samples, n inputs) ndarrays
            Values representing the multi-fidelity training case inputs.
        y : list of ndarray
            output training values which corresponds to the multi-fidelity
            training case input given by x.
        """
        pass
