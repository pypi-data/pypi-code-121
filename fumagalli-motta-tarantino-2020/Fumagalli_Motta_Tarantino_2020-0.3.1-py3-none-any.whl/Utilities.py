import scipy.stats


class NormalDistributionFunction:
    """
    Represents a normal distribution function.

    Parameters for the distribution:
    - loc: mean of the normal  distribution
    - scale: standard deviation of the normal distribution
    """

    @staticmethod
    def cumulative(x: float, **kwargs) -> float:
        """
        Returns the value of the cumulative distribution function.

        Parameters
        ----------
        x: float
            Value to get the corresponding value of the cumulative distribution function.
        kwargs
            Parameters for the distribution (-> see class documentation)

        Returns
        -------
        float
            Value of the cumulative distribution function.
        """
        return scipy.stats.norm.cdf(x, **kwargs)

    @staticmethod
    def inverse_cumulative(q: float, **kwargs) -> float:
        """
        Returns the value of the inverse cumulative distribution function (percent point function).

        Parameters
        ----------
        q: float
            Value to get the corresponding value of the inverse cumulative distribution function.
        kwargs
            Parameters for the distribution (-> see class documentation)

        Returns
        -------
        float
            Value of the inverse cumulative distribution function.
        """
        return scipy.stats.norm.ppf(q, **kwargs)


class UniformDistributionFunction:
    """
    Represents a uniform distribution function ($U_{[loc, loc+scale]}$).

    Parameters for the distribution:
    - loc: start of distribution
    - scale: difference added to the start of the beginning of the distribution (-> defining the end of the distribution)
    """

    @staticmethod
    def cumulative(x: float, **kwargs) -> float:
        return scipy.stats.uniform.cdf(x, **kwargs)

    @staticmethod
    def inverse_cumulative(q: float, **kwargs) -> float:
        return scipy.stats.uniform.ppf(q, **kwargs)
