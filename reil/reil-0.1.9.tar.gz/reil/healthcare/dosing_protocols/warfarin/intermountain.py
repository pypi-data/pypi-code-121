# -*- coding: utf-8 -*-
'''
Intermountain class
===================

Intermountain warfarin dosing protocol based on `Anderson et al. (2007)
supplements Appendix B
<https://www.ahajournals.org/doi/10.1161/circulationaha.107.737312>`_
'''
# TODO: The current implementation assumes the same patient is being treated
# on future days. The correct implementation should be fully "functional", with
# no memory keeping! (no `additional_info`)
import functools
from typing import Any, Dict, List, Literal, Optional, Tuple

import reil.healthcare.dosing_protocols.dosing_protocol as dp


Zone = Literal['action point low',
               'red zone low',
               'yellow zone low',
               'green zone',
               'yellow zone high',
               'red zone high',
               'action point high']


class Intermountain(dp.DosingProtocol):
    '''
    Intermountain warfarin dosing protocol based on `Anderson et al. (2007)
    supplements Appendix B
    <https://www.ahajournals.org/doi/10.1161/circulationaha.107.737312>`_
    '''

    def __init__(self, enforce_day_ge_8: bool = True) -> None:
        super().__init__()
        self._enforce_day_ge_8 = enforce_day_ge_8

    def prescribe(self,
                  patient: Dict[str, Any],
                  additional_info: dp.AdditionalInfo
                  ) -> Tuple[dp.DosingDecision, dp.AdditionalInfo]:
        '''
        Prescribe a dose for the given `patient` and `additional_info`.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - day
            - dose_history
            - interval_history (only for day 8)

        additional_info:
            A dictionary of information being communicated between protocols,
            including:
            - dosing_decisions_list
            - last_zone

        Returns
        -------
        :
            A `DosingDecision` along with updated `additional_info`.
        '''
        dosing_decisions_list: List[dp.DosingDecision] = additional_info.get(
            'dosing_decisions_list', [])
        last_zone: Zone = additional_info.get('last_zone', '')
        previous_INR = patient['INR_history'][-1]

        if not dosing_decisions_list:
            today = patient['day']

            if self._enforce_day_ge_8 and today < 8:
                raise ValueError('Intermountain is only valid for day>=8.')

            if self._enforce_day_ge_8 and today == 8:
                dose_history = patient['dose_history']
                interval_history = patient['interval_history']
                all_doses = functools.reduce(
                    lambda x, y: x+y,
                    ([dose_history[-i]]*interval_history[-i]
                     for i in range(len(interval_history), 0, -1)))

                if len(all_doses) < 3:
                    raise ValueError(
                        'Intermountain requires doses for days 5 to 7 '
                        'for dosing on day 8.')

                previous_dose = sum(all_doses[-3:])/3
            else:
                previous_dose = patient['dose_history'][-1]

            dosing_decisions_list, last_zone = self.intermountain_dosing_table(
                previous_INR, last_zone, previous_dose)

        else:
            if dosing_decisions_list[0].duration is None:
                dosing_decisions_list, last_zone = \
                    self.intermountain_dosing_table(
                        previous_INR, last_zone, dosing_decisions_list[0].dose)

        additional_info['last_zone'] = last_zone
        additional_info['dosing_decisions_list'] = dosing_decisions_list[1:]

        return dosing_decisions_list[0], additional_info

    @staticmethod
    def intermountain_dosing_table(  # noqa: C901
            INR: float,
            last_zone: Zone,
            daily_dose: float) -> Tuple[List[dp.DosingDecision], Zone]:
        '''
        Determine the dosing information, based on Intermountain dosing table.

        Arguments
        ---------
        current_INR:
            The latest value of INR.

        last_zone:
            The last zone the patient was in.
            * action point low
            * red zone low
            * yellow zone low
            * green zone
            * yellow zone high
            * red zone high
            * action point high

        daily_dose:
            The latest daily dose prescribed.

        Returns
        -------
        :
            * A list of `DoseInterval`s. It always includes the new daily dose
              and the new next test (in days). If an immediate dose is
              necessary, the first item will be the immediate dose and the next
              test day.
            * The new zone that patient's INR falls into.
        '''
        zone = Intermountain.zone(INR)

        weekly_dose = daily_dose * 7

        immediate_dose: float = -1.0
        immediate_duration: Optional[int] = None
        same_zone = zone == last_zone

        # -1s below are added to compensate for immediate_duration = 1
        next_duration: Optional[int] = {
            'action point low': (5-1, 14-1),
            'red zone low': (7-1, 14-1),
            'yellow zone low': (14, 14),
            'green zone': (14, 28),
            'yellow zone high': (14, 14),
            'red zone high': (7-1, 14-1),
            'action point high': (7, 14)
        }[zone][same_zone]

        if last_zone == 'action point high':
            if zone.startswith(('yellow', 'green')):
                weekly_dose *= 0.85
                next_duration = 7
            else:
                zone = 'action point high'
                immediate_dose = 0.0
                immediate_duration = 2
                next_duration = None

        elif zone == 'green zone':
            pass
        elif zone == 'action point low':
            # (immediate extra dose) average 5-7 for day 8
            immediate_dose = daily_dose * 2
            immediate_duration = 1
            weekly_dose *= 1.10
        elif zone == 'red zone low':
            # (extra half dose) average 5-7 for day 8
            immediate_dose = daily_dose * 1.5
            immediate_duration = 1
            weekly_dose *= 1.05
        elif zone == 'yellow zone low':
            if same_zone:
                weekly_dose *= 1.05
        elif zone == 'yellow zone high':
            if same_zone:
                weekly_dose *= 0.95
        elif zone == 'red zone high':
            immediate_dose = daily_dose * 0.5 if INR < 4.0 else 0.0
            immediate_duration = 1
            weekly_dose *= 0.90
        elif zone == 'action point high':
            immediate_dose = 0.0
            immediate_duration = 2
            next_duration = None

        dosing_decisions = list(
            (dp.DosingDecision(immediate_dose, immediate_duration),)
            if (immediate_dose >= 0.0 and immediate_duration is not None)
            else []
        ) + [dp.DosingDecision(weekly_dose / 7, next_duration)]

        return dosing_decisions, zone

    @staticmethod
    def zone(INR: float) -> Zone:
        '''
        Determine the zone based on patient's INR.

        Arguments
        ---------
        INR:
            the value of a patient's INR.

        Returns
        -------
        :
            Name of the dose, one of:
            * action point low
            * red zone low
            * yellow zone low
            * green zone
            * yellow zone high
            * red zone high
            * action point high
        '''
        if INR < 1.60:
            z = 'action point low'
        elif INR < 1.80:
            z = 'red zone low'
        elif INR < 2.00:
            z = 'yellow zone low'
        elif INR <= 3.00:
            z = 'green zone'
        elif INR < 3.40:
            z = 'yellow zone high'
        elif INR < 5.00:
            z = 'red zone high'
        else:
            z = 'action point high'

        return z
