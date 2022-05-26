"""
Surrogate model based on the N-Dimensional Interpolation library by Stephen Marone.

https://github.com/SMarone/NDInterp
"""

import numpy
from typing import Dict, Type
from .base import SurrogateModel
from .nn_interpolators.nn_base import NNBase
from .nn_interpolators.linear_interpolator import LinearInterpolator
from .nn_interpolators.weighted_interpolator import WeightedInterpolator
from .nn_interpolators.rbf_interpolator import RBFInterpolator


class NearestNeighbor(SurrogateModel):
    """
    Surrogate model that approximates values using a nearest neighbor approximation.

    Attributes
    ----------
    interpolant : object
        Interpolator object
    options : dict
        Input keyword arguments for the interpolator.
    interpolant_type : NNBase
        Type of interpolator from NearestNeighbor.interpolators()
    """

    def __init__(self, interpolant_type="rbf", **options):
        """
        Initialize all attributes.

        Parameters
        ----------
        interpolant_type : str
            must be one of 'linear', 'weighted', or 'rbf'.
        **options :
            Options as keyword arguments
        """
        interpolators = self.interpolators()
        try:
            self.interpolant_type = interpolators[interpolant_type]
        except KeyError:
            raise ValueError(
                f"interpolant_type '{interpolant_type}' not supported"
                f"; must be one of {list(interpolators)}."
            )
        self.options = options
        self.interpolant = None

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
        self.interpolant = self.interpolant_type(
            numpy.asarray(x),
            numpy.asarray(y),
            **self.options,
        )

    def predict(self, x, **kwargs):
        """
        Calculate a predicted value of the response based on the current trained model.

        Parameters
        ----------
        x : array-like
            Point(s) at which the surrogate is evaluated.
        **kwargs : dict
            Additional keyword arguments passed to the interpolant.

        Returns
        -------
        float
            Predicted value.
        """
        return self.interpolant(numpy.asarray(x), **kwargs)

    def linearize(self, x, **kwargs):
        """
        Calculate the jacobian of the interpolant at the requested point.

        Parameters
        ----------
        x : array-like
            Point at which the surrogate Jacobian is evaluated.
        **kwargs : dict
            Additional keyword arguments passed to the interpolant.

        Returns
        -------
        ndarray
            Jacobian of surrogate output wrt inputs.
        """
        jac = self.interpolant.gradient(numpy.asarray(x), **kwargs)
        if jac.shape[0] == 1 and len(jac.shape) > 2:
            return jac[0, ...]
        return jac

    @staticmethod
    def interpolators() -> Dict[str, Type[SurrogateModel]]:
        return {
            "linear": LinearInterpolator,
            "weighted": WeightedInterpolator,
            "rbf": RBFInterpolator,
        }


class LinearNearestNeighbor(NearestNeighbor):  # pragma: no cover
    """
    Surrogate model that approximates values using a linear interpolator.

    Attributes
    ----------
    interpolant : object
        Interpolator object
    options : dict
        Input keyword arguments for the interpolator.
    interpolant_type : Type[NNBase]
        Type of interpolator; here `LinearInterpolator`

    """

    def __init__(self, **options):
        """
        Initialize all attributes.

        Parameters
        ----------
        **options :
            Options, as keyword arguments
        """
        super().__init__("linear", **options)


class WeightedNearestNeighbor(NearestNeighbor):  # pragma: no cover
    """
    Surrogate model that approximates values using a weighted interpolator.

    Attributes
    ----------
    interpolant : object
        Interpolator object
    options : dict
        Input keyword arguments for the interpolator.
    interpolant_type : Type[NNBase]
        Type of interpolator; here `WeightedInterpolator`

    """

    def __init__(self, **options):
        """
        Initialize all attributes.

        Parameters
        ----------
        **options :
            Options, as keyword arguments
        """
        super().__init__("weighted", **options)


class RBFNearestNeighbor(NearestNeighbor):  # pragma: no cover
    """
    Surrogate model that approximates values using a RBF interpolator.

    Attributes
    ----------
    interpolant : object
        Interpolator object
    options : dict
        Input keyword arguments for the interpolator.
    interpolant_type : Type[NNBase]
        Type of interpolator; here `RBFInterpolator`

    """

    def __init__(self, **options):
        """
        Initialize all attributes.

        Parameters
        ----------
        **options :
            Options, as keyword arguments
        """
        super().__init__("rbf", **options)
