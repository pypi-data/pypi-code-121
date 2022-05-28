# -*- coding: utf-8 -*-
'''
Patient class
=============

This class is the base class to model patients with different characteristics.
#TODO: Serialization and configs do not include random generators.
'''

from copy import deepcopy
from typing import Any, Dict, Optional
import reil

from reil.datatypes.feature import FeatureGeneratorSet
from reil.healthcare.mathematical_models import HealthMathModel
from reil.serialization import deserialize, serialize


class Patient:
    '''
    Base class for patients in healthcare.
    '''
    def __init__(
            self, model: HealthMathModel, random_seed: Optional[int] = None,
            **feature_values: Any) -> None:
        '''
        Parameters
        ----------
        model:
            A `HealthMathModel` to be used to model patient's behavior.

        feature_values:
            Keyword arguments by which some of the `features` of the patient
            can be determined. For example, if "age" is one of the features,
            age=40.0 will set the initial age to 40.0.
        '''
        if not hasattr(self, 'feature_gen_set'):
            self.feature_gen_set = FeatureGeneratorSet()

        self._model = model
        self._random_seed = random_seed
        self._rnd_generators = reil.random_generators_from_seed(random_seed)

        with reil.random_generator_context(*self._rnd_generators):
            self.feature_set = self.feature_gen_set(feature_values)

        self.feature_set.update(
            self._model.generate(
                self._rnd_generators, self.feature_set, **feature_values))
        self._model.setup(self._rnd_generators, self.feature_set)

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        # Created a model first to initiate the Patient. Then here replace
        # it with the loaded model.
        internal_states = config.pop('internal_states', {})

        model_config = config.pop('model')

        model_init: HealthMathModel = deserialize(model_config)  # type: ignore
        model_copy = deepcopy(model_init)
        config['model'] = model_init
        instance = cls(**config)

        for key, value in internal_states.items():
            instance.__dict__[key] = deserialize(value)

        instance._model = model_copy

        return instance

    def get_config(self) -> Dict[str, Any]:
        config = dict(
            model=serialize(self._model),
            internal_states={
                'feature_gen_set': serialize(self.feature_gen_set),
                'feature_set': serialize(self.feature_set)},
            random_seed=self._random_seed)

        return config

    def generate(self) -> None:
        '''
        Generate a new patient.

        This method calls every `feature`, and then sets
        up to `model` using the new values.
        '''

        with reil.random_generator_context(*self._rnd_generators):
            self.feature_set = self.feature_gen_set()

        self.feature_set.update(
            self._model.generate(self._rnd_generators, self.feature_set))
        self._model.setup(self._rnd_generators, self.feature_set)

    def model(self, **inputs: Any) -> Dict[str, Any]:
        '''Model patient's behavior.

        Arguments
        ---------
        inputs:
            Keyword arguments that specify inputs to the model. For example, if
            `dose` is a necessary input, `model(dose=10.0)` will provide the
            model with dose of 10.0.

        Returns
        -------
        :
            All the outputs of running the mathematical model, given the input.
        '''
        return self._model.run(**inputs)

    def __setstate__(self, state):
        self.__dict__ = self.from_config(dict(
            feature_gen_set=state['feature_gen_set'],
            sensitivity_gen=state['_sensitivity_gen'],
            randomized=state['_randomized'],
            feature_set=state['feature_set'],
            model=state['_model']
        )).__dict__
