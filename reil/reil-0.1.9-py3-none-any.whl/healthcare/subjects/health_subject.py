# -*- coding: utf-8 -*-  pylint: disable=undefined-variable
'''
HealthSubject class
===================

This `HealthSubject` class implements interaction with patients.
'''

from typing import Any, Dict, List, Optional, Tuple, Union

from reil.datatypes.feature import (MISSING, Feature, FeatureGenerator,
                                    FeatureGeneratorSet, FeatureSet)
from reil.healthcare.patient import Patient
from reil.serialization import deserialize, serialize
from reil.subjects.subject import Subject


class HealthSubject(Subject):
    '''
    A HealthSubject subject class with a patient.
    '''

    def __init__(
            self,
            patient: Patient,
            measurement_name: str,
            measurement_range: Tuple[float, float],
            dose_range: Tuple[float, float],
            dose_step: float,
            interval_range: Tuple[int, int],
            interval_step: int,
            max_day: int,
            **kwargs: Any):
        '''
        Arguments
        ---------
        patient:
            A patient object that generates new patients and models
            interaction between dose and INR.

        measurement_name:
            Name of the measured value after dose administration, e.g. BGL,
            INR, etc.

        dose_range:
            A tuple that shows the minimum and maximum amount of dose of
            the medication.

        interval_range:
            A tuple that shows the minimum and maximum duration of each dosing
            decision.

        measurement_range:
            A tuple that shows the minimum and maximum possible values of each
            measurement.

        max_day:
            Maximum duration of each trial.
        '''

        super().__init__(max_entity_count=1, **kwargs)

        self._patient = patient
        if not self._patient:
            return

        self._dose_range = dose_range
        self._dose_step = dose_step
        self._interval_range = interval_range
        self._interval_step = interval_step
        self._measurement_range = measurement_range
        self._measurement_name = measurement_name
        self._actions_taken: List[FeatureSet] = []

        self._max_day = max_day

        self.feature_gen_set = FeatureGeneratorSet(
            FeatureGenerator.continuous(
                name=name, lower=lower, upper=upper)
            for name, lower, upper in (
                (f'{self._measurement_name}_history',
                 *self._measurement_range),
                (f'daily_{self._measurement_name}_history',
                 *self._measurement_range))
        ) + FeatureGeneratorSet(
            FeatureGenerator.discrete(
                name=name, lower=lower, upper=upper, step=step)
            for name, lower, upper, step in (
                ('dose_history', *self._dose_range, self._dose_step),
                ('daily_dose_history', *self._dose_range, self._dose_step),
                ('interval_history', *self._interval_range,
                    self._interval_step),
                ('dose', *self._dose_range, self._dose_step),
                ('interval', *self._interval_range, self._interval_step),
            )
        ) + FeatureGenerator.discrete(
            name='day', lower=0, upper=self._max_day - 1,
            generator=lambda _: None)

        self.action_gen_set = FeatureGeneratorSet()

        HealthSubject._generate_state_defs(self)

        self._day: int = 0
        self._full_measurement_history = [0.0] * self._max_day
        self._full_dose_history = [0.0] * self._max_day
        self._decision_points_measurement_history = [0.0] * (self._max_day + 1)
        self._decision_points_dose_history = [0.0] * self._max_day
        self._decision_points_interval_history: List[int] = [1] * self._max_day
        self._decision_points_index: int = 0
        self._actions_taken = []

        self._full_measurement_history[0] = self._patient.model(
            measurement_days=[0])[self._measurement_name][-1]
        self._decision_points_measurement_history[0] = \
            self._full_measurement_history[0]

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        patient_info = config['patient']
        if patient_info is not None:
            config['patient'] = deserialize(patient_info)

        actions_taken = config['internal_states'].pop(
            '_actions_taken', [])

        instance = super().from_config(config)
        for action in actions_taken:
            a: FeatureSet = deserialize(action)  # type: ignore
            instance.take_effect(a)

        return instance

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        if self._patient is None:
            config.update({'patient': None})
        else:
            config.update({'patient': serialize(self._patient)})
        config.update(dict(
            measurement_name=self._measurement_name,
            measurement_range=self._measurement_range,
            dose_range=self._dose_range,
            dose_step=self._dose_step,
            interval_range=self._interval_range,
            interval_step=self._interval_step,
            max_day=self._max_day
        ))
        # Since we need to take actions again, dose list of the model should
        # be cleared.
        if config['patient']:
            config['patient']['config']['model']['config']['dose'] = {}
        config['internal_states']['_actions_taken'] = [
            serialize(action) for action in self._actions_taken]

        return config

    def _generate_state_defs(self):
        if 'day' not in self.state.definitions:
            self.state.add_definition(
                'day', ('day', {}))

    @classmethod
    def _empty_instance(cls):
        return cls(None, None)  # type: ignore

    @staticmethod
    def generate_dose_values(
            min_dose: float = 0.0,
            max_dose: float = 15.0,
            dose_increment: float = 0.5) -> List[float]:

        return list(min_dose + x * dose_increment
                    for x in range(
                        int((max_dose - min_dose) / dose_increment) + 1))

    @staticmethod
    def generate_interval_values(
            min_interval: int = 1,
            max_interval: int = 28,
            interval_increment: int = 1) -> List[int]:

        return list(range(min_interval, max_interval, interval_increment))

    def is_terminated(self, _id: Optional[int] = None) -> bool:
        return self._day >= self._max_day

    def _take_effect(
            self, action: FeatureSet, _id: int = 0
    ) -> FeatureSet:
        self._actions_taken.append(action)

        action_temp = action.value
        current_dose = float(action_temp['dose'])  # type: ignore
        current_interval = min(int(action_temp['interval']),  # type: ignore
                               self._max_day - self._day)

        measurements_temp = self._patient.model(
            dose={
                i: current_dose
                for i in range(self._day, self._day + current_interval)
            },
            measurement_days=list(
                range(self._day + 1, self._day + current_interval + 1)
            )
        )[self._measurement_name]

        self._decision_points_dose_history[self._decision_points_index] = \
            current_dose
        self._decision_points_interval_history[self._decision_points_index] = \
            current_interval
        self._decision_points_index += 1

        day_temp = self._day
        self._day += current_interval

        self._full_dose_history[day_temp:self._day] = \
            [current_dose] * current_interval
        self._full_measurement_history[day_temp +
                                       1:self._day + 1] = measurements_temp

        self._decision_points_measurement_history[
            self._decision_points_index] = \
            self._full_measurement_history[self._day]

        return action

    def reset(self) -> None:
        Subject.reset(self)
        self._patient.generate()

        self._day: int = 0
        self._full_measurement_history = [0.0] * self._max_day
        self._full_dose_history = [0.0] * self._max_day
        self._decision_points_measurement_history = [0.0] * (self._max_day + 1)
        self._decision_points_dose_history = [0.0] * self._max_day
        self._decision_points_interval_history: List[int] = [1] * self._max_day
        self._decision_points_index: int = 0
        self._actions_taken = []

        self._full_measurement_history[0] = self._patient.model(
            measurement_days=[0])[self._measurement_name][-1]
        self._decision_points_measurement_history[0] = \
            self._full_measurement_history[0]

    def _numerical_sub_comp(self, name: str):
        return self._patient.feature_set[name]

    def _categorical_sub_comp(self, name: str, missing: bool = False):
        if missing:
            self._patient.feature_gen_set[name](MISSING)

        return self._patient.feature_set[name]

    def _get_history(
            self, list_name: str, length: int, backfill: bool = False
    ) -> Feature:
        if length == 0:
            raise ValueError(
                'length should be a positive integer, or '
                '-1 for full length output.')

        filler: Union[float, int]
        _list: Union[List[float], List[int]]
        if list_name == f'{self._measurement_name}_history':
            _list = self._decision_points_measurement_history
            index = self._decision_points_index + 1
            filler = 0.0
        elif list_name == f'daily_{self._measurement_name}_history':
            _list = self._full_measurement_history
            index = self._day + 1
            filler = 0.0
        elif list_name == 'dose_history':
            _list = self._decision_points_dose_history
            index = self._decision_points_index
            filler = 0.0
        elif list_name == 'daily_dose_history':
            _list = self._full_dose_history
            index = self._day
            filler = 0.0
        elif list_name == 'interval_history':
            _list = self._decision_points_interval_history
            index = self._decision_points_index
            filler = int(1)
        else:
            raise ValueError(f'Unknown list_name: {list_name}.')

        if length == -1:
            result = _list[:index]
        else:
            if length > index:
                i1, i2 = length - index, 0
            else:
                i1, i2 = 0, index - length
            if backfill:
                filler = _list[i2]
            result = [filler] * i1 + _list[i2:index]  # type: ignore

        return self.feature_gen_set[list_name](tuple(result))  # type: ignore

    def _sub_comp_dose_history(
            self, _id: int, length: int = 1, backfill: bool = False,
            **kwargs: Any
    ) -> Feature:
        return self._get_history(  # type: ignore
            'dose_history', length, backfill)

    def _sub_comp_measurement_history(
            self, _id: int, length: int = 1, backfill: bool = True,
            **kwargs: Any
    ) -> Feature:
        return self._get_history(  # type: ignore
            f'{self._measurement_name}_history', length, backfill)

    def _sub_comp_interval_history(
            self, _id: int, length: int = 1, backfill: bool = False,
            **kwargs: Any
    ) -> Feature:
        return self._get_history(  # type: ignore
            'interval_history', length, backfill)

    def _sub_comp_day(self, _id: int, **kwargs: Any) -> Feature:
        return self.feature_gen_set['day'](  # type: ignore
            value=self._day if 0 <= self._day < self._max_day else None)

    def _sub_comp_daily_dose_history(
            self, _id: int, length: int = 1, backfill: bool = False,
            **kwargs: Any
    ) -> Feature:
        return self._get_history(  # type: ignore
            'daily_dose_history', length, backfill)

    def _sub_comp_daily_measurement_history(
            self, _id: int, length: int = 1, backfill: bool = False,
            **kwargs: Any
    ) -> Feature:
        return self._get_history(  # type: ignore
            f'daily_{self._measurement_name}_history', length, backfill)

    def __repr__(self) -> str:
        try:
            temp = ', '.join(''.join(
                (v.name, ': ',
                 ('{:4.2f}' if v.is_numerical else '{}').format(v.value)))
                for v in self._patient.feature_set)
        except (AttributeError, ValueError, KeyError):
            temp = ''

        return (f'{self.__class__.__qualname__} [{temp}]')
