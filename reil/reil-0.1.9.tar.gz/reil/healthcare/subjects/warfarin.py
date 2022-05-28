# -*- coding: utf-8 -*-  pylint: disable=undefined-variable
'''
warfarin class
==============

This `warfarin` class implements a two compartment PK/PD model for warfarin.
'''

import functools
from typing import Any, Callable, Dict, Optional, Tuple

from reil.datatypes.feature import Feature, FeatureGeneratorType, FeatureSet
from reil.healthcare.patient import Patient
from reil.healthcare.subjects.health_subject import HealthSubject
from reil.utils import reil_functions

DefComponents = Tuple[Tuple[str, Dict[str, Any]], ...]

patient_basic: DefComponents = (
    ('age', {}), ('CYP2C9', {}),
    ('VKORC1', {})
)
patient_extra: DefComponents = (
    ('weight', {}), ('height', {}),
    ('gender', {}), ('race', {}), ('tobaco', {}),
    ('amiodarone', {}), ('fluvastatin', {})
)

sensitivity: DefComponents = (('sensitivity', {}),)
patient_w_sensitivity: DefComponents = (
    *patient_basic, *sensitivity, *patient_extra)

state_definitions: Dict[str, DefComponents] = {
    'age': (('age', {}),),
    'patient_basic': patient_basic,
    'patient_w_sensitivity_basic': (*patient_basic, *sensitivity),
    'patient_w_sensitivity': patient_w_sensitivity,
    'patient': (*patient_basic, *patient_extra),
    'patient_w_dosing': (
        *patient_basic, *patient_extra,
        # ('day', {}),
        ('dose_history', {'length': -1}),
        ('INR_history', {'length': -1}),
        ('interval_history', {'length': -1})),
    'patient_for_baseline': (
        *patient_basic, *patient_extra,
        ('day', {}),
        ('dose_history', {'length': 4}),
        ('INR_history', {'length': 4}),
        ('interval_history', {'length': 4})),

    **{
        f'patient_w_dosing_{i:02}': (
            *patient_basic,
            # ('day', {}),
            ('dose_history', {'length': i}),
            ('INR_history', {'length': i + 1}),
            ('interval_history', {'length': i}))
        for i in range(1, 10)},
    **{
        f'old_patient_w_dosing_{i:02}': (
            *patient_basic,
            ('day', {}),
            ('dose_history', {'length': i}),
            ('INR_history', {'length': i}),
            ('interval_history', {'length': i}))
        for i in range(1, 10)},

    'patient_w_full_dosing': (
        *patient_w_sensitivity,
        ('day', {}),
        ('daily_dose_history', {'length': -1}),
        ('daily_INR_history', {'length': -1}),
        ('interval_history', {'length': -1})),

    'daily_INR': (('daily_INR_history', {'length': -1}),),

    'recent_daily_INR': (('INR_within', {'length': 1}),),

    'Measured_INR_2': (
        ('INR_history', {'length': 2}),
        ('interval_history', {'length': 1})),
}

reward_sq_dist = reil_functions.NormalizedSquareDistance(
    name='sq_dist', y_var_name='daily_INR_history',
    length=-1, multiplier=-1.0, retrospective=True, interpolate=False,
    center=2.5, band_width=1.0, exclude_first=True)

reward_dist = reil_functions.NormalizedDistance(
    name='dist', y_var_name='daily_INR_history',
    length=-1, multiplier=-1.0, retrospective=True, interpolate=False,
    center=2.5, band_width=1.0, exclude_first=True)

reward_sq_dist_interpolation = reil_functions.NormalizedSquareDistance(
    name='sq_dist_interpolation',
    y_var_name='INR_history', x_var_name='interval_history',
    length=2, multiplier=-1.0, retrospective=True, interpolate=True,
    center=2.5, band_width=1.0, exclude_first=True)

reward_PTTR = reil_functions.PercentInRange(
    name='PTTR', y_var_name='daily_INR_history',
    length=-1, multiplier=-1.0, retrospective=True, interpolate=False,
    acceptable_range=(2, 3), exclude_first=True)

reward_PTTR_interpolation = reil_functions.PercentInRange(
    name='PTTR',
    y_var_name='INR_history', x_var_name='interval_history',
    length=2, multiplier=-1.0, retrospective=True, interpolate=True,
    acceptable_range=(2, 3), exclude_first=True)

statistic_PTTR = reil_functions.PercentInRange(
    name='PTTR', y_var_name='daily_INR_history',
    length=-1, multiplier=1.0, retrospective=True, interpolate=False,
    acceptable_range=(2, 3), exclude_first=True)


class Warfarin(HealthSubject):
    '''
    A warfarin subject based on Hamberg's two compartment PK/PD model.
    '''

    def __init__(
            self,
            patient: Patient,
            INR_range: Tuple[float, float] = (0.0, 15.0),
            dose_range: Tuple[float, float] = (0.0, 15.0),
            dose_step: float = 0.5,
            interval_range: Tuple[int, int] = (1, 28),
            interval_step: int = 1,
            max_day: int = 90,
            dose_only: bool = False,
            backfill: bool = True,
            **kwargs: Any):
        '''
        Arguments
        ---------
        patient:
            A patient object that generates new patients and models
            interaction between dose and INR.

        INR_range:
            A tuple that specifies min and max INR.

        dose_range:
            A tuple that specifies min and max dose.

        interval_range:
            A tuple that specifies min and max number of days between two
            measurements.

        max_day:
            Maximum duration of each trial.

        '''

        super().__init__(
            patient=patient,
            measurement_name='INR',
            measurement_range=INR_range,
            dose_range=dose_range,
            dose_step=dose_step,
            interval_range=interval_range,
            interval_step=interval_step,
            max_day=max_day,
            **kwargs)

        self._dose_only = dose_only
        self._backfill = backfill
        self.action_gen_set += self.feature_gen_set['dose']
        if not dose_only:
            self.action_gen_set += self.feature_gen_set['interval']

        Warfarin._generate_state_defs(self)
        Warfarin._generate_action_defs(self)
        Warfarin._generate_reward_defs(self)
        Warfarin._generate_statistic_defs(self)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        del config['measurement_name']
        config['INR_range'] = config.pop('measurement_range')

        return config

    def _generate_state_defs(self):
        current_defs = self.state.definitions
        for name, args in state_definitions.items():
            if name not in current_defs:
                self.state.add_definition(name, *args)

    def _generate_reward_defs(self):
        current_defs = self.reward.definitions

        if 'dist_exact' not in current_defs:
            self.reward.add_definition(
                'dist_exact', reward_dist, 'recent_daily_INR')

        if 'sq_dist_exact' not in current_defs:
            self.reward.add_definition(
                'sq_dist_exact', reward_sq_dist, 'recent_daily_INR')

        if 'sq_dist_interpolation' not in current_defs:
            self.reward.add_definition(
                'sq_dist_interpolation', reward_sq_dist_interpolation,
                'Measured_INR_2')

        if 'PTTR_exact' not in current_defs:
            self.reward.add_definition(
                'PTTR_exact', reward_PTTR, 'recent_daily_INR')

        if 'PTTR_interpolation' not in current_defs:
            self.reward.add_definition(
                'PTTR_interpolation', reward_PTTR_interpolation,
                'Measured_INR_2')

    def _generate_statistic_defs(self):
        if 'PTTR_exact_basic' not in self.statistic.definitions:
            self.statistic.add_definition(
                'PTTR_exact_basic', statistic_PTTR,
                'daily_INR', 'patient_w_sensitivity_basic')

        if 'PTTR_exact' not in self.statistic.definitions:
            self.statistic.add_definition(
                'PTTR_exact', statistic_PTTR,
                'daily_INR', 'patient_w_sensitivity')

    def _generate_action_defs(self):  # noqa: C901
        current_action_definitions = self.possible_actions.definitions

        def _generate(
                feature: FeatureSet,
                ops: Tuple[Callable[[FeatureSet], bool], ...],
                dose_masks: Tuple[Dict[float, float], ...],
                interval_masks: Tuple[Dict[int, int], ...]
        ) -> FeatureGeneratorType:
            self.action_gen_set.unmask('dose')
            if self._dose_only:
                for op, d_mask in zip(ops, dose_masks):
                    if op(feature):
                        self.action_gen_set.mask('dose', d_mask)

                        return self.action_gen_set.make_generator()

            else:
                self.action_gen_set.unmask('interval')
                for op, d_mask, i_mask in zip(ops, dose_masks, interval_masks):
                    if op(feature):
                        self.action_gen_set.mask('dose', d_mask)
                        self.action_gen_set.mask('interval', i_mask)

                        return self.action_gen_set.make_generator()

                self.action_gen_set.mask('interval', interval_masks[-1])

            self.action_gen_set.mask('dose', dose_masks[-1])

            return self.action_gen_set.make_generator()

        caps = tuple(
            i for i in (5.0, 10.0, 15.0)
            if self._dose_range[0] <= i <= self._dose_range[1])
        max_cap = min(caps[-1], self._dose_range[1])

        dose = {
            cap: {
                d: cap
                for d in self.generate_dose_values(cap, max_cap, 0.5)
                if d > cap}
            for cap in caps}

        min_interval, max_interval = self._interval_range
        int_fixed = {
            d: {
                i: d
                for i in range(
                    min_interval, max_interval + 1, self._interval_step)
                if i != d}
            for d in (1, 2, 3, 7)}
        int_semi_free = {
            i: min_interval
            for i in range(min_interval, max_interval + 1, self._interval_step)
            if i not in (1, 2, 3, 7, 14, 21, 28)}
        int_weekly = {
            i: min_interval
            for i in range(min_interval, max_interval + 1, self._interval_step)
            if i not in (7, 14, 21, 28)}

        for cap in caps[:-1]:
            name = f'237_{int(cap):02}'
            if name not in current_action_definitions:
                self.possible_actions.add_definition(
                    name, functools.partial(
                        _generate,
                        ops=(
                            lambda f: f['day'].value >= 5,
                            lambda f: f['day'].value == 2,
                            lambda f: f['day'].value == 0),
                        dose_masks=(
                            dose[max_cap], dose[max_cap], dose[cap]
                        ),
                        interval_masks=(
                            int_fixed[7], int_fixed[3], int_fixed[2])),
                    'day')

            name = f'daily_{int(cap):02}'
            if name not in current_action_definitions:
                self.possible_actions.add_definition(
                    name, functools.partial(
                        _generate,
                        ops=(lambda f: f['day'].value > 0,),
                        dose_masks=(dose[max_cap], dose[cap]),
                        interval_masks=(int_fixed[1], int_fixed[1])),
                    'day')

            name = f'free_{int(cap):02}'
            if name not in current_action_definitions:
                self.possible_actions.add_definition(
                    name, functools.partial(
                        _generate,
                        ops=(lambda f: f['day'].value > 0,),
                        dose_masks=(dose[max_cap], dose[cap]),
                        interval_masks=({}, {})),
                    'day')

            name = f'semi_{int(cap):02}'
            if name not in current_action_definitions:
                self.possible_actions.add_definition(
                    name, functools.partial(
                        _generate,
                        ops=(lambda f: f['day'].value > 0,),
                        dose_masks=(dose[max_cap], dose[cap]),
                        interval_masks=(int_semi_free, int_semi_free)),
                    'day')

            name = f'weekly_{int(cap):02}'
            if name not in current_action_definitions:
                self.possible_actions.add_definition(
                    name, functools.partial(
                        _generate,
                        ops=(lambda f: f['day'].value > 0,),
                        dose_masks=(dose[max_cap], dose[cap]),
                        interval_masks=(int_weekly, int_weekly)),
                    'day')

        name = '237_15'
        if name not in current_action_definitions:
            self.possible_actions.add_definition(
                name, functools.partial(
                    _generate,
                    ops=(
                        lambda f: f['day'].value >= 5,
                        lambda f: f['day'].value == 2,
                        lambda f: f['day'].value == 0),
                    dose_masks=(
                        dose[max_cap], dose[max_cap], dose[max_cap]
                    ),
                    interval_masks=(
                        int_fixed[7], int_fixed[3], int_fixed[2])),
                'day')

        name = 'daily_15'
        if name not in current_action_definitions:
            self.possible_actions.add_definition(
                name, functools.partial(
                    _generate,
                    ops=(),
                    dose_masks=(dose[max_cap],),
                    interval_masks=(int_fixed[1],)),
                'day')

        name = 'free_15'
        if name not in current_action_definitions:
            self.possible_actions.add_definition(
                name, functools.partial(
                    _generate,
                    ops=(),
                    dose_masks=(dose[max_cap],),
                    interval_masks=({},)),
                'day')

        name = 'semi_15'
        if name not in current_action_definitions:
            self.possible_actions.add_definition(
                name, functools.partial(
                    _generate,
                    ops=(),
                    dose_masks=(dose[max_cap],),
                    interval_masks=(int_semi_free,)),
                'day')

        name = 'weekly_15'
        if name not in current_action_definitions:
            self.possible_actions.add_definition(
                name, functools.partial(
                    _generate,
                    ops=(lambda f: f['day'].value > 0,),
                    dose_masks=(dose[max_cap],),
                    interval_masks=(int_weekly,)),
                'day')

    def _default_state_definition(
            self, _id: Optional[int] = None) -> FeatureSet:
        patient_features = self._patient.feature_set
        return FeatureSet([
            patient_features['age'],
            patient_features['CYP2C9'],
            patient_features['VKORC1']])

    def _sub_comp_age(self, _id: int, **kwargs: Any) -> Feature:
        return super()._numerical_sub_comp('age')

    def _sub_comp_weight(self, _id: int, **kwargs: Any) -> Feature:
        return self._numerical_sub_comp('weight')

    def _sub_comp_height(self, _id: int, **kwargs: Any) -> Feature:
        return self._numerical_sub_comp('height')

    def _sub_comp_gender(self, _id: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('gender')

    def _sub_comp_race(self, _id: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('race')

    def _sub_comp_tobaco(self, _id: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('tobaco')

    def _sub_comp_amiodarone(self, _id: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('amiodarone')

    def _sub_comp_fluvastatin(self, _id: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('fluvastatin')

    def _sub_comp_CYP2C9(self, _id: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('CYP2C9')

    def _sub_comp_CYP2C9_masked(
            self, _id: int, days: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('CYP2C9', self._day < days)

    def _sub_comp_VKORC1(self, _id: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('VKORC1')

    def _sub_comp_VKORC1_masked(
            self, _id: int, days: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('VKORC1', self._day < days)

    def _sub_comp_sensitivity(self, _id: int, **kwargs: Any) -> Feature:
        return self._categorical_sub_comp('sensitivity')

    def _sub_comp_INR_history(
            self, _id: int, length: int = 1, **kwargs: Any
    ) -> Feature:
        return self._sub_comp_measurement_history(
            _id, length, backfill=self._backfill, **kwargs)

    def _sub_comp_daily_INR_history(
            self, _id: int, length: int = 1, **kwargs: Any
    ) -> Feature:
        return self._sub_comp_daily_measurement_history(
            _id, length, backfill=self._backfill, **kwargs)

    def _sub_comp_INR_within(
            self, _id: int, length: int = 1, **kwargs: Any
    ) -> Feature:
        intervals = self._get_history('interval_history', length).value
        return self._get_history(
            'daily_INR_history', sum(intervals))  # type: ignore
