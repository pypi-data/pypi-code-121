# -*- coding: utf-8 -*-
'''
Gage class
==========

Gage dosing protocol ('pharmacogenetic', 'clinical'), based on `
Gage et al. (2008)
<https://doi.org/10.1038/clpt.2008.10>`_
'''

from math import exp, sqrt
from typing import Any, Dict, Literal, Tuple

import reil.healthcare.dosing_protocols.dosing_protocol as dp


class Gage(dp.DosingProtocol):
    '''
    Gage dosing protocol ('pharmacogenetic', 'clinical'), based on `
    Gage et al. (2008)
    <https://doi.org/10.1038/clpt.2008.10>`_
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
        '''
        Prescribe a dose for the given `patient` and `additional_info`.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - BSA (m^2)
            - CYP2C9 *
            - VKORC1 *
            - target_INR
            - race (Only 'Black' changes the dose.)
            - amiodarone ('Yes', 'No')
            - tobaco ('Yes', 'No')
            - DVT/PE ('Yes', 'No') (Deep Venous Thrombosis/ Pulmonary Embolism)

        additional_info:
            A dictionary of information being communicated between protocols at
            each call to `prescribe`.

        Returns
        -------
        :
            A `DosingDecision` along with updated `additional_info`.

        Notes
        -----
        * `CYP2C9` and `VKORC1` are only available in the
            pharmacogenetic model.
        '''
        dose = self._method(patient)

        return dp.DosingDecision(dose), additional_info

    @staticmethod
    def clinical(patient: Dict[str, Any]) -> float:
        '''
        Determine warfarin dose using clinical Gage formula.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - BSA (m^2)
            - race (Only 'Black' changes the dose.)
            - amiodarone ('Yes', 'No')
            - tobaco ('Yes', 'No')
            - target_INR
            - DVT/PE ('Yes', 'No') (Deep Venous Thrombosis/ Pulmonary Embolism)

        Returns
        -------
        :
            The maintenance dose

        Notes
        -----
        If BSA is not provided, weight (lb) and height (in) is used to
        calculate BSA using Mosteller method.

        target_INR is assumed 2.5 if not provided.
        '''
        if (bsa := patient.get('BSA')) is None:
            try:
                bsa = sqrt(patient['height'] * 2.54 *
                           patient['weight'] * 0.454 / 3600)
            except KeyError:
                raise KeyError(
                    'Either `BSA` in m^2, or `weight` in lb and `height` in in'
                    'should be provided.')

        african_american = patient.get('race') == 'Black'
        target_INR = patient.get('target_INR', 2.5)
        amiodarone = patient.get('amiodarone') == 'Yes'
        smokes = patient.get('tobaco') == 'Yes'
        dvt_pe = patient.get('DVT/PE') == 'Yes'

        dose = exp(0.613
                   + 0.4250 * bsa
                   - 0.0075 * patient['age']
                   + 0.1560 * african_american
                   + 0.2160 * target_INR
                   - 0.2570 * amiodarone
                   + 0.1080 * smokes
                   + 0.0784 * dvt_pe)

        return dose

    @staticmethod
    def pg(patient: Dict[str, Any]) -> float:
        '''
        Determine warfarin dose using pharmacogenetic Gage formula.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - BSA (m^2)
            - CYP2C9
            - VKORC1
            - target_INR
            - race (Only 'Black' changes the dose.)
            - amiodarone ('Yes', 'No')
            - tobaco ('Yes', 'No')
            - DVT/PE ('Yes', 'No') (Deep Venous Thrombosis/ Pulmonary Embolism)

        Returns
        -------
        :
            The maintenance dose

        Notes
        -----
        If BSA is not provided, weight (lb) and height (in) is used to
        calculate BSA using Mosteller method.

        target_INR is assumed 2.5 if not provided.
        '''
        if (bsa := patient.get('BSA')) is None:
            try:
                bsa = sqrt(patient['height'] * 2.54 *
                           patient['weight'] * 0.454 / 3600)
            except KeyError:
                raise KeyError(
                    'Either `BSA` in m^2, or `weight` in lb and `height` in in'
                    ' should be provided.')

        african_american = patient.get('race') == 'Black'
        target_INR = patient.get('target_INR', 2.5)
        amiodarone = patient.get('amiodarone') == 'Yes'
        smokes = patient.get('tobaco') == 'Yes'
        dvt_pe = patient.get('DVT/PE') == 'Yes'

        cyp2c9 = patient.get('CYP2C9', '')
        cyp2c9_2 = cyp2c9.count('*2')
        cyp2c9_3 = cyp2c9.count('*3')
        vkorc1_ga = patient['VKORC1'] == 'G/A'

        dose = exp(0.9751
                   - 0.3238 * vkorc1_ga
                   + 0.4317 * bsa
                   - 0.4008 * cyp2c9_3
                   - 0.00745 * patient['age']
                   - 0.2066 * cyp2c9_2
                   + 0.2029 * target_INR
                   - 0.2538 * amiodarone
                   + 0.0922 * smokes
                   - 0.0901 * african_american
                   + 0.0664 * dvt_pe)

        return dose
