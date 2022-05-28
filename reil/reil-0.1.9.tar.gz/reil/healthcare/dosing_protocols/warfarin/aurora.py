# -*- coding: utf-8 -*-
'''
Aurora class
============

Aurora Dosing Protocol, based on `Ravvaz et al. (2017)
<https://doi.org/10.1161/circgenetics.117.001804>`_
'''

from typing import Any, Dict, List, Tuple

import reil.healthcare.dosing_protocols.dosing_protocol as dp


class Aurora(dp.DosingProtocol):
    '''
    Aurora Dosing Protocol, based on `Ravvaz et al. (2017)
    <https://doi.org/10.1161/circgenetics.117.001804>`_
    '''

    def prescribe(self,  # noqa: C901
                  patient: Dict[str, Any],
                  additional_info: dp.AdditionalInfo
                  ) -> Tuple[dp.DosingDecision, dp.AdditionalInfo]:
        '''
        Prescribe a dose for the given `patient` and `additional_info`.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - day
            - INR_history
            - dose_history
            - interval_history

        additional_info:
            A dictionary of information being communicated between protocols at
            each call to `prescribe`. These additional information are
            protocol-dependent.

        Returns
        -------
        :
            A `DosingDecision` along with updated `additional_info`.
        '''
        today: int = patient['day']
        INRs: List[float] = patient['INR_history']
        previous_INR = INRs[-1]

        # to suppress Pylance's unbound variable error.
        previous_dose = 0.0
        previous_interval: int = 1
        next_interval: int

        if today > 1:
            previous_dose: float = patient['dose_history'][-1]
            previous_interval: int = patient['interval_history'][-1]

        red_flag: bool = additional_info.get('red_flag', False)
        skip_dose: int = additional_info.get('skip_dose', 0)
        new_dose: float = additional_info.get('new_dose', 0.0)
        number_of_stable_days: int = additional_info.get(
            'number_of_stable_days', 0)

        if red_flag:
            if previous_INR > 3.0:
                next_dose = 0.0
                next_interval = 2
            else:
                red_flag = False
                next_dose = new_dose
                next_interval = 7
        elif skip_dose:
            skip_dose = 0
            next_dose = new_dose
            next_interval = 7
        elif today <= 2:  # initial dosing
            # Note: in the actual described protocol, INR>1.1 and some other
            # conditions should get 5.0, but in their simulation, Ravvaz et al,
            # assumed all <65 get 10.0. (Footnote on page 10 of paper's
            # appendix)
            next_dose = 10.0 if patient['age'] < 65.0 else 5.0
            next_interval = 3 - today
        elif today == 3:  # adjustment dosing
            # Note: the paper is a bit vague on interval, since it has provided
            # the whole dosing table for days 3 and 4 (which says retest in 7
            # and 28 days), but at the same time says dose for days 3 and 4 are
            # based on the table. Here I assume that the interval is not
            # determined by the table, and only the dose is adjusted.
            next_interval = 2

            if previous_INR >= 2.0:
                next_dose = 5.0
                if previous_INR <= 3.0:
                    if 2.0 <= INRs[-2] <= 3.0:
                        number_of_stable_days = previous_interval
                    else:
                        number_of_stable_days = 1
                    # number_of_stable_days = self._stable_days(
                    #     INRs[-2], previous_INR, previous_interval)
            else:
                next_dose, _, _, _ = self.aurora_dosing_table(
                    previous_INR, previous_dose)
        elif today == 4:
            raise ValueError(
                'Cannot use Aurora on day 4. '
                'Dose on day 4 equals dose on day 3.')
        else:  # maintenance dosing
            if 2.0 <= previous_INR <= 3.0:
                if (previous_dose == patient['dose_history'][-2]) and (
                        2.0 <= INRs[-2] <= 3.0):
                    # stable dose and therapeutic INR
                    number_of_stable_days += previous_interval
                    # number_of_stable_days += self._stable_days(
                    #     INRs[-2], previous_INR, previous_interval)
                else:
                    number_of_stable_days = 1

                next_dose = previous_dose
                next_interval = self.aurora_retesting_table(
                    number_of_stable_days)
            else:
                number_of_stable_days = 0
                new_dose, next_interval, skip_dose, red_flag = \
                    self.aurora_dosing_table(previous_INR, previous_dose)
                if red_flag:
                    next_dose = 0.0
                    next_interval = 2
                elif skip_dose:
                    next_dose = 0.0
                    next_interval = skip_dose
                else:
                    next_dose = new_dose

        additional_info.update({
            'red_flag': red_flag,
            'skip_dose': skip_dose,
            'new_dose': new_dose,
            'number_of_stable_days': number_of_stable_days})

        return dp.DosingDecision(next_dose, next_interval), additional_info

    @staticmethod
    def _stable_days(INR_start: float, INR_end: float, interval: int) -> int:
        '''
        Compute the number of stable days.

        Arguments
        ---------
        INR_start:
            INR at the beginning of the period.

        INR_end:
            INR at the end of the period.

        interval:
            The number of days from start to end.

        Returns
        -------
        :
            The number of days in therapeuric range (TTR).

        Notes
        -----
        The paper is a bit vague! Initially I assumed we interpolate INRs to
        get the number of stable days, but it does not seem to be the case.
        So, in the updated implementation, if INR_end is not in the range,
        it returns 0, if it is in the range, but INR_start is not in the range,
        it returns 1, otherwise, it returns `interval`.

        '''
        # return sum(2 <= INR_end + (INR_start - INR_end) * i / interval <= 3
        #            for i in range(1, interval+1))
        if 2.0 <= INR_end <= 3.0:
            if 2.0 <= INR_start <= 3.0:
                return interval
            else:
                return 1

        return 0

    @staticmethod
    def aurora_dosing_table(
            current_INR: float, dose: float) -> Tuple[float, int, int, bool]:
        '''
        Determine the dosing information, based on Aurora dosing table.

        Arguments
        ---------
        current_INR:
            The latest value of INR.

        dose:
            The latest dose prescribed.

        Returns
        -------
        :
            * The next dose
            * The time of the next test (in days).
            * The number of doses to skip.
            * Red flag for too high INR values.
        '''
        skip_dose: int = 0
        red_flag = False
        _current_INR = round(current_INR, 2)
        next_test: int = 7

        if _current_INR < 1.50:
            dose = dose * 1.15
        elif _current_INR < 1.80:
            dose = dose * 1.10
        elif _current_INR < 2.00:
            dose = dose * 1.075
        elif _current_INR <= 3.00:
            next_test = 28
        elif _current_INR < 3.40:
            dose = dose * 0.925
        elif _current_INR < 4.00:
            dose = dose * 0.9
        elif _current_INR <= 5.00:
            skip_dose = 2
            dose = dose * 0.875
        else:
            red_flag = True
            next_test = 2
            dose = dose * 0.85

        return dose, next_test, skip_dose, red_flag

    @staticmethod
    def aurora_retesting_table(number_of_stable_days: int) -> int:
        '''
        Determine when the next test should be based on current number of
        stable days.

        Arguments
        ---------
        number_of_stable_days:
            Number of consecutive stable days.

        Returns
        -------
        :
            The time of the next test (in days).
        '''
        retesting_table = {1: 1, 2: 5, 7: 7, 14: 14, 28: 28}
        return retesting_table[max(
            map(lambda x: x if x <= number_of_stable_days else 1,
                retesting_table))]
