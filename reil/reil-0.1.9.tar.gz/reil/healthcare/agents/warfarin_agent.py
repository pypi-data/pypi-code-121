# -*- coding: utf-8 -*-
'''
WarfarinAgent class
===================

An agent for warfarin modeling based on the protocols defined
in Ravvaz et al (2017).
'''

from typing import Any, Literal, Optional, Tuple

from reil.agents.agent_base import AgentBase
from reil.datatypes.feature import (FeatureGenerator, FeatureGeneratorType,
                                    FeatureSet)
from reil.healthcare.dosing_protocols.warfarin import (AAA, CAA, PGAA, PGPGA,
                                                       PGPGI)


class WarfarinAgent(AgentBase):
    '''
    An `agent` that prescribes dose for a warfarin `subject`,
    based on the dosing protocols defined in Ravvaz et al (2017).
    '''

    def __init__(self,
                 study_arm: Literal['aaa', 'caa', 'pgaa',
                                    'pgpgi', 'pgpga'] = 'aaa',
                 dose_range: Tuple[float, float] = (0.0, 15.0),
                 interval_range: Tuple[int, int] = (1, 28),
                 **kwargs: Any):
        '''
        Arguments
        ---------
        study_arm:
            One of available study arms: aaa, caa, pgaa, pgpgi, pgpga
        '''
        super().__init__(**kwargs)

        if study_arm.lower() in ['aaa', 'ravvaz aaa', 'ravvaz_aaa']:
            self._protocol = AAA()
        elif study_arm.lower() in ['caa', 'ravvaz caa', 'ravvaz_caa']:
            self._protocol = CAA()
        elif study_arm.lower() in ['pgaa', 'ravvaz pgaa', 'ravvaz_pgaa']:
            self._protocol = PGAA()
        elif study_arm.lower() in ['pgpgi', 'ravvaz pgpgi', 'ravvaz_pgpgi']:
            self._protocol = PGPGI()
        elif study_arm.lower() in ['pgpga', 'ravvaz pgpga', 'ravvaz_pgpga']:
            self._protocol = PGPGA()

        self._dose_gen = FeatureGenerator.continuous(
            name='dose', lower=dose_range[0], upper=dose_range[1])
        self._interval_gen = FeatureGenerator.discrete(
            name='interval', lower=interval_range[0], upper=interval_range[1])

    def act(self,
            state: FeatureSet,
            subject_id: int,
            actions: FeatureGeneratorType,
            iteration: Optional[int] = 0) -> FeatureSet:
        '''
        Generate the dosing `action` based on the `state` and current dosing
        protocol.

        Arguments
        ---------
        state:
            The state for which the action should be returned.

        actions:
            The set of possible actions to choose from.

        iteration:
            The iteration in which the agent is acting.

        Returns
        -------
        :
            The action
        '''
        patient = state.value
        patient['day'] += 1  # type: ignore

        decision = self._protocol.prescribe(patient)
        dose = decision.dose
        interval = decision.duration

        if interval is None:
            raise ValueError(f'None duration received from {self._protocol}.')

        return FeatureSet([
            self._dose_gen(min(dose, self._dose_gen.upper or dose)),
            self._interval_gen(
                min(interval, self._interval_gen.upper or interval))
        ])

    def reset(self):
        '''Resets the agent at the end of a learning iteration.'''
        self._protocol.reset()

    def __repr__(self) -> str:
        try:
            return super().__repr__() + f' arm: {self._protocol}'
        except NameError:
            return super().__repr__()

# Implementation that matches RAVVAZ dataset.
# -------------------------------------------
#
# def aurora(self, patient: Dict[str, Any]) -> float:
#     if self._red_flag:
#         if self._retest_day > patient['day']:
#             return_value = 0.0
#         elif patient['INR_history'][-1] > 3.0:
#             self._retest_day = patient['day'] + 2
#             return_value = 0.0
#         else:
#             self._red_flag = False
#             self._retest_day = patient['day'] + 7
#             return_value = self._dose
#         return return_value

#     next_test = 2
#     if patient['day'] <= 2:
#         self._dose = 10.0 if patient['age'] < 65.0 else 5.0
#     elif patient['day'] <= 4:
#         day_2_INR = (patient['INR_history'][-1] if patient['day'] == 3
#                      else patient['INR_history'][-2])
#         if day_2_INR >= 2.0:
#             self._dose = 5.0
#             if day_2_INR <= 3.0:
#                 self._early_therapeutic = True

#             self._number_of_stable_days, next_test = \
#                 self._aurora_retesting_table(patient['INR_history'][-1],
#                                              self._number_of_stable_days,
#                                              self._early_therapeutic)
#         else:
#             self._dose, next_test, _, _ = self._aurora_dosing_table(
#                 day_2_INR, self._dose)
#     else:
#         self._number_of_stable_days, next_test = \
#             self._aurora_retesting_table(
#               patient['INR_history'][-1],
#               self._number_of_stable_days,
#               self._early_therapeutic)

#     if next_test == -1:
# #         self._early_therapeutic = False
#         self._number_of_stable_days = 0
#         self._dose, next_test, self._skip_dose, self._red_flag = \
#           self._aurora_dosing_table(patient['INR_history'][-1], self._dose)

#     self._retest_day = patient['day'] + next_test

#     return self._dose if self._skip_dose == 0 else 0.0

# def _aurora_dosing_table(self,
#     current_INR: float, dose: float) -> Tuple[float, int, int, bool]:
#     skip_dose = 0
#     red_flag = False
#     if current_INR < 1.50:
#         dose = dose * 1.15
#         next_test = 7
#     elif current_INR < 1.80:
#         dose = dose * 1.10
#         next_test = 7
#     elif current_INR < 2.00:
#         dose = dose * 1.075
#         next_test = 7
#     elif current_INR <= 3.00:
#         next_test = 28
#     elif current_INR < 3.40:
#         dose = dose * 0.925
#         next_test = 7
#     elif current_INR < 4.00:
#         dose = dose * 0.9
#         next_test = 7
#     elif current_INR <= 5.00:
#         skip_dose = 1  # 2
#         dose = dose * 0.875
#         next_test = 7
#     else:
#         red_flag = True
#         next_test = 2
#         dose = dose * 0.85

#     return dose, next_test, skip_dose, red_flag

# def _aurora_retesting_table(self,
#   current_INR: float, number_of_stable_days: int,
#   early_therapeutic: bool = False) -> Tuple[int, int]:
#     # next_test = {0: 1, 1: 1, 2: 5, 7: 7, 14: 14, 28: 28}
#     # NOTE: When patient gets into the range early on
#     #      (before the maintenance period), we have 1: 2,
#     # but when patient is in maintenance,\
#     # we have 1: 6. I track the former in the main aurora method.

#     if early_therapeutic:
#         next_test = {0: 1, 1: 2, 3: 4, 7: 6, 13: 6, 19: 13, 32: 27}
#         max_gap = 32
#     else:
#         next_test = {0: 1, 1: 6, 7: 6, 13: 13, 26: 27}
#         max_gap = 26
#     if 2.0 <= current_INR <= 3.0:
#         number_of_stable_days = min(
#             number_of_stable_days + next_test[number_of_stable_days],
#             max_gap)
#     else:
#         return -1, -1

#     return number_of_stable_days, next_test[number_of_stable_days]
