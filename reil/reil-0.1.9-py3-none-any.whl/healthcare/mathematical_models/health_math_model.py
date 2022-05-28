# -*- coding: utf-8 -*-
'''
HealthMathModel class
=====================

The base class of all mathematical models, e.g. ODE, PDE, PK/PD, etc. in
healthcare.
'''
from typing import Any, Dict, Optional
import reil

from reil.datatypes.feature import FeatureGeneratorSet, FeatureSet


class HealthMathModel:
    '''
    The base class of all mathematical models in healthcare.
    '''
    _parameter_generators = FeatureGeneratorSet()

    @classmethod
    def generate(
            cls,
            rnd_generators: reil.RandomGeneratorsType,
            input_features: Optional[FeatureSet] = None,
            **kwargs: Any) -> FeatureSet:
        with reil.random_generator_context(*rnd_generators):
            if input_features:
                temp = input_features.value
                temp.update(kwargs)
                params = cls._parameter_generators(temp)
            else:
                params = cls._parameter_generators(None)

        return params

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        return cls()

    def get_config(self) -> Dict[str, Any]:
        return {}

    def setup(
            self, rnd_generators: reil.RandomGeneratorsType,
            input_features: Optional[FeatureSet] = None) -> None:
        '''
        Set up the model.

        Arguments
        ---------
        arguments:
            Any parameter that the model needs to setup initially.
        '''
        raise NotImplementedError

    def run(self, **inputs: Any) -> Dict[str, Any]:
        '''
        Run the model.

        Arguments
        ---------
        inputs:
            Any input arguments that the model needs for the run.

        Returns
        -------
        :
            A dictionary of model's return values.
        '''
        raise NotImplementedError
