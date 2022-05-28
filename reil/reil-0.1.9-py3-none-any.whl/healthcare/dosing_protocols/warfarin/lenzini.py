# -*- coding: utf-8 -*-
'''
Lenzini class
=============

Lenzini warfarin dosing protocol based on `Lenzini et al. (2010)
<https://doi.org/10.1038/clpt.2010.13>`_
'''

import functools
from math import exp, log, sqrt
from typing import Any, Dict, Literal, Tuple

import reil.healthcare.dosing_protocols.dosing_protocol as dp


class Lenzini(dp.DosingProtocol):
    '''
    Lenzini warfarin dosing protocol based on `Lenzini et al. (2010)
    <https://doi.org/10.1038/clpt.2010.13>`_
    '''

    def __init__(self,
                 method: Literal['pharmacogenetic',
                                 'clinical'] = 'pharmacogenetic') -> None:
        '''
        Arguments
        ---------
        method:
            One of 'pharmacogenetic', 'clinical'.
        '''
        if method.lower() == 'clinical':
            self._method = self.clinical
        elif method.lower() in ['pg', 'pharmacogenetic', 'default']:
            self._method = self.pg
        else:
            raise ValueError(
                f'Unknown method {method}.\n'
                'Acceptable methods are clinical and pharmacogenetic.')

    def prescribe(self,  # noqa: C901
                  patient: Dict[str, Any],
                  additional_info: dp.AdditionalInfo
                  ) -> Tuple[dp.DosingDecision, dp.AdditionalInfo]:
        dose = self._method(patient)

        return dp.DosingDecision(dose), additional_info

    @staticmethod
    def clinical(patient: Dict[str, Any]) -> float:
        '''
        Determine warfarin dose using clinical Lenzini formula.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - BSA (m^2)
            - INR_history (The most recent value will be used.)
            - target_INR
            - race (Only 'Black' changes the dose.)
            - stroke ('Yes', 'No')
            - diabetes ('Yes', 'No')
            - amiodarone ('Yes', 'No')
            - fluvastatin ('Yes', 'No')
            - dose_history (A list of previous doses at decision points)
            - interval_history (A list of previous intervals between decision
                points)
        Returns
        -------
        :
            The adjusted dose

        Notes
        -----
        If BSA is not provided, weight (lb) and height (in) is used to
        calculate BSA using Mosteller method.

        target_INR is assumed 2.5 if not provided.
        '''
        if not 4 <= patient['day'] <= 5:
            raise ValueError('Lenzini can only be used on days 4 and 5.')

        if (bsa := patient.get('BSA')) is None:
            try:
                bsa = sqrt(patient['height'] * 2.54 *
                           patient['weight'] * 0.454 / 3600)
            except KeyError:
                raise KeyError(
                    'Either `BSA` in m^2, or `weight` in lb and `height` in in'
                    'should be provided.')

        age = patient['age']
        ln_INR = log(patient['INR_history'][-1])  # Natural log

        target_INR = patient.get('target_INR', 2.5)

        african_american = patient.get('race') == 'Black'
        stroke = patient.get('stroke') == 'Yes'
        diabetes = patient.get('diabetes') == 'Yes'
        amiodarone = patient.get('amiodarone') == 'Yes'
        fluvastatin = patient.get('fluvastatin') == 'Yes'

        dose_history = patient['dose_history']
        interval_history = patient['interval_history']
        all_doses = functools.reduce(
            lambda x, y: x+y,
            ([dose_history[-i]]*interval_history[-i]
             for i in range(len(interval_history), 0, -1)))

        # Since on day 4, we don't have dose-4, a zero is padded to avoid
        # producing error in the run time.
        dose_4, dose_3, dose_2 = ([0] + all_doses)[-4:-1]

        dose = exp(2.81602
                   - 0.76679 * ln_INR
                   - 0.00590 * age
                   + 0.27815 * target_INR
                   - 0.16759 * diabetes
                   + 0.17675 * bsa
                   - 0.22844 * stroke
                   - 0.25487 * fluvastatin
                   + 0.07123 * african_american
                   - 0.11137 * amiodarone
                   + 0.03471 * dose_2
                   + 0.03047 * dose_3
                   + 0.01929 * dose_4
                   ) / 7

        return dose

    @staticmethod
    def pg(patient: Dict[str, Any]) -> float:
        '''
        Determine warfarin dose using pharmacogenetic Lenzini formula.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - BSA (m^2)
            - INR_history (The most recent value will be used.)
            - VKORC1
            - CYP2C9
            - target_INR
            - race (Only 'Black' changes the dose.)
            - stroke ('Yes', 'No')
            - diabetes ('Yes', 'No')
            - amiodarone ('Yes', 'No')
            - fluvastatin ('Yes', 'No')
            - dose_history (All previous doses administered.)
        Returns
        -------
        :
            The adjusted dose

        Notes
        -----
        If BSA is not provided, weight (lb) and height (in) is used to
        calculate BSA using Mosteller method.

        target_INR is assumed 2.5 if not provided.
        '''
        if not 4 <= patient['day'] <= 5:
            raise ValueError('Lenzini can only be used on days 4 and 5.')

        if (bsa := patient.get('BSA')) is None:
            try:
                bsa = sqrt(patient['height'] * 2.54 *
                           patient['weight'] * 0.454 / 3600)
            except KeyError:
                raise KeyError(
                    'Either `BSA` in m^2, or `weight` in lb and `height` in in'
                    'should be provided.')

        age = patient['age']
        ln_INR = log(patient['INR_history'][-1])  # Natural log

        # Both Lenzini et al. and Ravvaz et al. have VKORC1 G/A, in the formula
        # but Lenzini mentions that it is coded based on the number of "A"s
        # A/A -> 2, G/A -> 1, G/G -> 0
        vkorc1: str = patient['VKORC1']
        vkorc1_a = vkorc1.count('A')

        cyp2c9: str = patient['CYP2C9']
        cyp2c9_2 = cyp2c9.count('2')
        cyp2c9_3 = cyp2c9.count('3')

        target_INR = patient.get('target_INR', 2.5)

        african_american = patient.get('race') == 'Black'
        stroke = patient.get('stroke') == 'Yes'
        diabetes = patient.get('diabetes') == 'Yes'
        amiodarone = patient.get('amiodarone') == 'Yes'
        fluvastatin = patient.get('fluvastatin') == 'Yes'

        # Since on day 4, we don't have dose-4, a zero is padded to avoid
        # producing error in the run time.
        dose_4, dose_3, dose_2 = ([0] + list(patient['dose_history']))[-4:-1]

        dose = exp(3.10894
                   - 0.00767 * age
                   - 0.51611 * ln_INR
                   - 0.23032 * vkorc1_a
                   - 0.14745 * cyp2c9_2
                   - 0.30770 * cyp2c9_3
                   + 0.24597 * bsa
                   + 0.26729 * target_INR
                   - 0.09644 * african_american
                   - 0.20590 * stroke
                   - 0.11216 * diabetes
                   - 0.10350 * amiodarone
                   - 0.19275 * fluvastatin
                   + 0.01690 * dose_2
                   + 0.02018 * dose_3
                   + 0.01065 * dose_4
                   ) / 7

        return dose
