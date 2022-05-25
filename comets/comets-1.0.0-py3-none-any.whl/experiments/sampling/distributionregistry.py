# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.
from scipy import stats

from ...utilities.registry import Registry
from ...utilities import get_logger


logger = get_logger(__name__)
DistributionRegistry = Registry()


continuous_distributions = {
    "alpha": {"parameters": ["a", "loc", "scale"], "Scipy name": "alpha"},
    "arcsine": {"parameters": ["loc", "scale"], "Scipy name": "arcsine"},
    "beta": {"parameters": ["a", "b", "loc", "scale"], "Scipy name": "beta"},
    "betaprime": {"parameters": ["a", "b", "loc", "scale"], "Scipy name": "betaprime"},
    "burr": {"parameters": ["c", "d", "loc", "scale"], "Scipy name": "burr"},
    "burr12": {"parameters": ["c", "d", "loc", "scale"], "Scipy name": "burr12"},
    "cauchy": {"parameters": ["loc", "scale"], "Scipy name": "cauchy"},
    "chi": {"parameters": ["df", "loc", "scale"], "Scipy name": "chi"},
    "chi2": {"parameters": ["df", "loc", "scale"], "Scipy name": "chi2"},
    "cosine": {"parameters": ["loc", "scale"], "Scipy name": "cosine"},
    "dgamma": {"parameters": ["a", "loc", "scale"], "Scipy name": "dgamma"},
    "dweibull": {"parameters": ["c", "loc", "scale"], "Scipy name": "dweibull"},
    "exponential": {"parameters": ["loc", "scale"], "Scipy name": "expon"},
    "exponnorm": {"parameters": ["K", "loc", "scale"], "Scipy name": "exponnorm"},
    "exponweib": {"parameters": ["a", "c", "loc", "scale"], "Scipy name": "exponweib"},
    "f": {"parameters": ["dfn", "dfd", "loc", "scale"], "Scipy name": "f"},
    "fatiguelife": {"parameters": ["c", "loc", "scale"], "Scipy name": "fatiguelife"},
    "fisk": {"parameters": ["c", "loc", "scale"], "Scipy name": "fisk"},
    "foldnorm": {"parameters": ["c", "loc", "scale"], "Scipy name": "foldnorm"},
    "gamma": {"parameters": ["a", "loc", "scale"], "Scipy name": "gamma"},
    "gengamma": {"parameters": ["a", "c", "loc", "scale"], "Scipy name": "gengamma"},
    "genlogistic": {"parameters": ["c", "loc", "scale"], "Scipy name": "genlogistic"},
    "gennorm": {"parameters": ["beta", "loc", "scale"], "Scipy name": "gennorm"},
    "genexpon": {
        "parameters": ["a", "b", "c", "loc", "scale"],
        "Scipy name": "genexpon",
    },
    "genextreme": {"parameters": ["c", "loc", "scale"], "Scipy name": "genextreme"},
    "gilbrat": {"parameters": ["loc", "scale"], "Scipy name": "gilbrat"},
    "gompertz": {"parameters": ["c", "loc", "scale"], "Scipy name": "gompertz"},
    "halfcauchy": {"parameters": ["loc", "scale"], "Scipy name": "halfcauchy"},
    "halfnorm": {"parameters": ["loc", "scale"], "Scipy name": "halfnorm"},
    "invgamma": {"parameters": ["a", "loc", "scale"], "Scipy name": "invgamma"},
    "invgauss": {"parameters": ["mu", "loc", "scale"], "Scipy name": "invgauss"},
    "invweibull": {"parameters": ["c", "loc", "scale"], "Scipy name": "invweibull"},
    "laplace": {"parameters": ["loc", "scale"], "Scipy name": "laplace"},
    "logistic": {"parameters": ["loc", "scale"], "Scipy name": "logistic"},
    "loggamma": {"parameters": ["c", "loc", "scale"], "Scipy name": "loggamma"},
    "lognormal": {"parameters": ["s", "loc", "scale"], "Scipy name": "lognorm"},
    "loguniform": {
        "parameters": ["a", "b", "loc", "scale"],
        "Scipy name": "loguniform",
    },
    "lomax": {"parameters": ["c", "loc", "scale"], "Scipy name": "lomax"},
    "normal": {"parameters": ["loc", "scale"], "Scipy name": "norm"},
    "pareto": {"parameters": ["b", "loc", "scale"], "Scipy name": "pareto"},
    "powerlaw": {"parameters": ["a", "loc", "scale"], "Scipy name": "powerlaw"},
    "skewnorm": {"parameters": ["a", "loc", "scale"], "Scipy name": "skewnorm"},
    "t": {"parameters": ["df", "loc", "scale"], "Scipy name": "t"},
    "trapezoid": {"parameters": ["c", "d", "loc", "scale"], "Scipy name": "trapezoid"},
    "triangular": {"parameters": ["c", "loc", "scale"], "Scipy name": "triang"},
    "truncexpon": {"parameters": ["b", "loc", "scale"], "Scipy name": "truncexpon"},
    "truncnorm": {"parameters": ["a", "b", "loc", "scale"], "Scipy name": "truncnorm"},
    "uniform": {"parameters": ["loc", "scale"], "Scipy name": "uniform"},
    "vonmises": {"parameters": ["kappa", "loc", "scale"], "Scipy name": "vonmises"},
    "weibull": {"parameters": ["c", "loc", "scale"], "Scipy name": "weibull_min"},
}


discrete_distributions = {
    "bernoulli": {"parameters": ["p"], "Scipy name": "bernoulli"},
    "betabinom": {"parameters": ["n", "a", "b", "loc"], "Scipy name": "betabinom"},
    "binomial": {"parameters": ["n", "p", "loc"], "Scipy name": "binom"},
    "dlaplace": {"parameters": ["a", "loc"], "Scipy name": "dlaplace"},
    "discreteuniform": {"parameters": ["low", "high"], "Scipy name": "randint"},
    "geom": {"parameters": ["p", "loc"], "Scipy name": "geom"},
    "hypergeom": {"parameters": ["M", "n", "N", "loc"], "Scipy name": "hypergeom"},
    "logser": {"parameters": ["p", "loc"], "Scipy name": "logser"},
    "poisson": {"parameters": ["mu", "loc"], "Scipy name": "poisson"},
}


for name, params in continuous_distributions.items():
    try:
        dist = getattr(stats, params["Scipy name"])
        params["Type"] = "Continuous1D"
        DistributionRegistry.register(dist, name=name, info=params)
    except AttributeError:  # pragma: no cover
        logger.warning(
            "Could not add distribution {} to the registry. Please update your version of Scipy.".format(
                name
            )
        )
for name, params in discrete_distributions.items():
    try:
        dist = getattr(stats, params["Scipy name"])
        params["Type"] = "Discrete1D"
        DistributionRegistry.register(dist, name=name, info=params)
    except AttributeError:  # pragma: no cover
        logger.warning(
            "Could not add distribution {} to the registry. Please update your version of Scipy.".format(
                name
            )
        )
