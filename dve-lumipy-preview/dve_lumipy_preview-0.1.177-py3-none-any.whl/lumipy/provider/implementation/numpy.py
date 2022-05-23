from typing import Iterable, Optional, Dict, Union, List

import numpy as np

from ..base_provider import BaseProvider
from ..metadata import ColumnMeta, ParamMeta, TableParam
from ...query.expression.sql_value_type import SqlValType


class UniformDistProvider(BaseProvider):
    """Provides a collection of values drawn from a uniform probability distribution.

    This provider uses numpy's numpy.random.uniform() function.
    """

    def __init__(self):

        columns = [ColumnMeta("Outcome", SqlValType.Double, "Outcome of draw from uniform distribution.", True)]
        params = [
            ParamMeta("UpperLim", SqlValType.Double, "Upper limit of uniform distribution", 1.0),
            ParamMeta("LowerLim", SqlValType.Double, "Lower limit of uniform distribution", 0.0),
            ParamMeta("NumDraws", SqlValType.Int, "Number of Bernoulli trials to run."),
            ParamMeta("Seed", SqlValType.Int, "Random seed to set in numpy.")
        ]

        super().__init__(
            "Numpy.Random.Uniform",
            columns,
            params,
            self.__doc__
        )

    def _get_data(
            self,
            data_filter: Optional[Dict[str, object]],
            limit: Union[int, None],
            **params
    ) -> Iterable[Dict[str, Union[str, int, float]]]:

        if 'NumDraws' not in params.keys():
            raise ValueError(f"NumDraws parameter value not supplied to {self.name}.")

        upper = params['UpperLim'] if 'UpperLim' in params.keys() else 1
        lower = params['LowerLim'] if 'LowerLim' in params.keys() else 0
        n = params['NumDraws']

        if 'Seed' in params.keys():
            np.random.seed(params['Seed'])

        if limit is not None and limit < n:
            n = limit

        res = np.random.uniform(lower, upper, size=n)

        return map(lambda x: {"Outcome": x}, res)


class BernoulliDistProvider(BaseProvider):
    """Provides a collection of draws from a Bernoulli distribution with a given trial probability p.

    This provider uses numpy's numpy.random.binomial() function with n=1. The Bernoulli distribution is a special case
    of the Binomial distribution where the number of trials (n) is equal to 1.
    """

    def __init__(self):
        """Constructor for BernoulliProvider class.

        """
        columns = [ColumnMeta("Outcome", SqlValType.Boolean, "Outcome of a Bernoulli trial.", True)]
        parameters = [
            ParamMeta("Probability", SqlValType.Double, "Probability of success per-trial."),
            ParamMeta("NumDraws", SqlValType.Int, "Number of Bernoulli trials to run."),
            ParamMeta("Seed", SqlValType.Int, "Random seed to set in numpy.")
        ]

        super().__init__(
            "Numpy.Random.Bernoulli",
            columns,
            parameters,
            self.__doc__
        )

    def _get_data(
            self,
            data_filter: Optional[Dict[str, object]],
            limit: Union[int, None],
            **params
    ) -> Iterable[Dict[str, Union[str, int, float]]]:

        if 'Probability' not in params.keys():
            raise ValueError(f"Probability parameter value not supplied to {self.name}.")

        if 'NumDraws' not in params.keys():
            raise ValueError(f"NumDraws parameter value not supplied to {self.name}.")

        p = params['Probability']
        n = params['NumDraws']

        if 'Seed' in params.keys():
            np.random.seed(params['Seed'])

        if limit is not None and limit < n:
            n = limit

        res = np.random.binomial(1, p, size=n)

        return map(lambda x: {"Outcome": x}, res)


class GaussianDistProvider(BaseProvider):
    """Provides a collection of draws from a multivariate Gaussian distribution for a given covariance matrix and
    set of means.

    """

    def __init__(self, dimensions):

        self.dimensions = dimensions

        columns = [
            ColumnMeta(f"Dim{i}", SqlValType.Double, f"Value of random variable in dimension {i}")
            for i in range(self.dimensions)
        ]
        params = [
            ParamMeta("NumDraws", SqlValType.Int, "Number of draws from the distribution."),
            ParamMeta("Seed", SqlValType.Int, "Random seed to set in numpy.")
        ]
        table_params = [
            TableParam(
                'Covariance',
                description="The covariance matrix of the distribution specified as a table."
            ),
            TableParam(
                'Means',
                columns=[ColumnMeta("Mean", SqlValType.Double)],
                description="The means of the distribution specifieds as a single-column table."
            )
        ]

        super().__init__(
            f"Numpy.Random.Gaussian{self.dimensions}D",
            columns=columns,
            parameters=params,
            table_parameters=table_params,
            description=self.__doc__
        )

    def _get_data(
            self,
            data_filter: Optional[Dict[str, object]],
            limit: Union[int, None],
            **params
    ) -> Iterable[Dict[str, Union[str, int, float]]]:

        covmat = params['Covariance']
        means = params['Means']
        if means.shape[1] != 1:
            raise ValueError("Means parameter must only have one column.")

        n = params['NumDraws']

        if 'Seed' in params.keys():
            np.random.seed(params['Seed'])

        if limit is not None and limit < n:
            n = limit

        res = np.random.multivariate_normal(means.values.flatten(), covmat.values, size=n)

        def row_map(row):
            return {f'Dim{i}': v for i, v in enumerate(row)}

        return map(row_map, res)
