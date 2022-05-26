import functools

import numpy as np


def ignore_unhashable(func):
    uncached = func.__wrapped__
    attributes = functools.WRAPPER_ASSIGNMENTS + ("cache_info", "cache_clear")

    @functools.wraps(func, assigned=attributes)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as error:
            if "unhashable type" in str(error):
                return uncached(*args, **kwargs)
            raise

    wrapper.__uncached__ = uncached
    return wrapper


def make_array(arg):
    if isinstance(arg, int):
        arr = np.array([arg])
    elif isinstance(arg, list):
        arr = np.array(arg)
    else:
        arr = arg

    return arr


class Posterior(object):
    """
    Caches a posterior.
    :param posterior: the posterior distribution
    """

    def __init__(self, posterior: dict, to_numpy: bool = True):
        self.data = posterior

        if to_numpy:
            self.data = self._to_numpy(posterior)

    def _to_numpy(self, posterior):
        return {k: v.detach().cpu().numpy() for k, v in posterior.items()}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def indices(self, shape, *args):
        """
        Creates indices for easier access to variables.
        """
        indices = [np.arange(shape[0])]
        for i, arg in enumerate(args):
            if arg is None:
                indices.append(np.arange(shape[i + 1]))
            else:
                indices.append(make_array(arg))
        return np.ix_(*indices)

    def dist(self, param, *args, **kwargs):
        indices = self.indices(self[param].shape, *args)
        return self[param][indices]

    @ignore_unhashable
    @functools.lru_cache(maxsize=128)
    def median(self, param, *args):
        """Returns the median of param."""
        return np.median(self.dist(param, *args), axis=0)

    @ignore_unhashable
    @functools.lru_cache(maxsize=128)
    def mean(self, param, *args):
        """Returns the mean of param."""
        return np.mean(self.dist(param, *args), axis=0)

    @ignore_unhashable
    @functools.lru_cache(maxsize=128)
    def quantiles(self, param, *args, **kwargs):
        """Returns the quantiles of param."""
        q = kwargs.pop("q", [0.025, 0.975])
        return np.quantile(
            self.dist(param, *args),
            q,
            axis=0,
        )

    def qlower(self, param, *args, **kwargs):
        """Returns the quantile lower bound of param."""
        return self.quantiles(param, *args, **kwargs)[0]

    def qupper(self, param, *args, **kwargs):
        """Returns the quantile upper bound of param."""
        return self.quantiles(param, *args, **kwargs)[1]

    def ci(self, param, *args, **kwargs):
        return np.abs(self.mean(param, *args) - self.hpdi(param, *args, **kwargs))
