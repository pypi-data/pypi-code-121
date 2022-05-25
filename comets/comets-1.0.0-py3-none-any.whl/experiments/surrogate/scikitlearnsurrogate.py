# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from .surrogate import (
    BaseSurrogateModel,
    SurrogateRegistry,
)
from sklearn.utils import all_estimators
import numpy as np
from ...utilities.registry import partialclass


class ScikitLearnSurrogate(BaseSurrogateModel):
    """
    Scikit-learn surrogate models (prototype)
    """

    def __init__(self, estimator, objective='NoObjective'):
        estimators = all_estimators(type_filter='regressor')
        self.scikitlearnmodel = dict(estimators)[estimator]()
        self.objective = objective

    def evaluate(self, input_parameter_set):
        return self.decoder(
            self.scikitlearnmodel.predict(self.encoder(input_parameter_set))
        )

    def fit(self, inputs, observations):
        X, y = self.encoder_inputs_obs(inputs, observations)
        self.scikitlearnmodel.fit(X, y)

    def encoder(self, inputs):
        return np.array(list(inputs.values())).reshape(1, -1)

    def encoder_inputs_obs(self, inputs, obs):
        fieldnames = inputs[0].keys()
        X = np.array([[item.get(key) for key in fieldnames] for item in inputs])
        y = np.array(obs)
        return X, y

    def decoder(self, outputs):
        return {self.objective: outputs[0]}


# Register scikitlearn regressors in SurrogateRegistry,
for regressor_name in [i[0] for i in all_estimators(type_filter='regressor')]:
    SurrogateRegistry[regressor_name] = partialclass(
        ScikitLearnSurrogate, estimator=regressor_name
    )
