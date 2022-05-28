# -*- coding: utf-8 -*-
'''
IWPC class
==========

IWPC warfarin dosing protocols.

`clinical` and `pharmacogenetic` protocols based on `IWPC (2009)
<https://doi.org/10.1056/nejmoa0809329>`_

`modified` pharmacogenetic and `loading_dose` protocols based on
`Pirmohamed et al. (2013) <https://doi.org/10.1056/NEJMoa1311386>`_
'''

from math import exp
from typing import Any, Dict, Literal, Tuple

import reil.healthcare.dosing_protocols.dosing_protocol as dp
from reil.datatypes import feature


class IWPC(dp.DosingProtocol):
    '''
    IWPC warfarin dosing protocol, based on `IWPC (2009)
    <https://doi.org/10.1056/nejmoa0809329>`_
    '''

    def __init__(self,
                 method: Literal['pharmacogenetic',
                                 'clinical',
                                 'modified',
                                 'loading_dose'] = 'pharmacogenetic') -> None:
        '''
        Arguments
        ---------
        method:
            One of 'pharmacogenetic', 'clinical', 'modified', 'loading_dose'.
        '''
        if method.lower() == 'clinical':
            self._method = self.clinical
        elif method.lower() == 'modified':
            self._method = self.modified_pharmacogenetic
        elif method.lower() in ['pg', 'pharmacogenetic', 'default']:
            self._method = self.pharmacogenetic
        elif method.lower() in ['loading', 'loading_dose']:
            self._method = self.loading_dose
        else:
            raise ValueError(
                f'Unknown method {method}.\n'
                'Acceptable methods are pharmacogenetic, clinical, '
                'modified, and loading_dose.')

        self.reset()

    def prescribe(self,
                  patient: Dict[str, Any],
                  additional_info:  dp.AdditionalInfo
                  ) -> Tuple[dp.DosingDecision, dp.AdditionalInfo]:
        day = patient['day']

        if self._method is self.loading_dose:
            if day == 1:
                doses = self.loading_dose(patient)
                additional_info.update({'doses': doses})
            elif day <= 3:
                doses = additional_info['doses']
            else:
                raise ValueError(
                    'loading_dose method is only available for '
                    'days 1, 2, and 3.')

            dosing_decision = dp.DosingDecision(doses[day-1], 1)
        else:
            dosing_decision = dp.DosingDecision(
                self._method(patient))  # type: ignore
            additional_info.pop('doses', None)

        return dosing_decision, additional_info

    @staticmethod
    def clinical(patient: Dict[str, Any]) -> float:
        '''
        Determine warfarin dose using clinical IWPC formula.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - height (in)
            - weight (lb)
            - race ('Asian', 'Black', 'Mixed', `MISSING`)
            - amiodarone ('Yes', 'No')
            - enzyme_inducer ('Yes' if patient takes any of
                              carbamazepine, phenytoin, rifampin, or
                              rifampicin, otherwise 'No')

        Returns
        -------
        :
            The maintenance dose
        '''
        age_in_decades = patient['age'] // 10
        height_in_cm = patient['height'] * 2.54
        weight_in_kg = patient['weight'] * 0.454

        race: Any = patient.get('race', feature.MISSING)
        african_american = race == 'Black'
        asian = race == 'Asian'
        missing_or_mixed_race = int(race in (feature.MISSING, 'Mixed'))
        amiodarone = patient.get('amiodarone') == 'Yes'
        enzyme_inducer = patient.get('enzyme_inducer') == 'Yes'

        weekly_dose = (4.0376
                       - 0.2546 * age_in_decades
                       + 0.0118 * height_in_cm
                       + 0.0134 * weight_in_kg
                       - 0.6752 * asian
                       + 0.4060 * african_american
                       + 0.0443 * missing_or_mixed_race
                       + 1.2799 * enzyme_inducer
                       - 0.5695 * amiodarone) ** 2

        return weekly_dose / 7.0

    @staticmethod
    def pharmacogenetic(patient: Dict[str, Any]) -> float:
        '''
        Determine warfarin dose using pharmacogenetic IWPC formula.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - height (in)
            - weight (lb)
            - VKORC1 ('G/G', 'G/A', 'A/A', `MISSING`)
            - CYP2C9 ('*1/*1', '*1/*2', '*1/*3', '*2/*2', '*2/*3',
                      '*3/*3', `MISSING`)
            - race ('Asian', 'Black', 'Mixed', `MISSING`)
            - amiodarone ('Yes', 'No')
            - enzyme_inducer ('Yes' if patient takes any of
                              carbamazepine, phenytoin, rifampin, or
                              rifampicin, otherwise 'No')

        Returns
        -------
        :
            The maintenance dose
        '''
        age_in_decades = patient['age'] // 10
        height_in_cm = patient['height'] * 2.54
        weight_in_kg = patient['weight'] * 0.454

        vkorc1 = patient['VKORC1']
        vkorc1_ga = vkorc1 == 'G/A'
        vkorc1_aa = vkorc1 == 'A/A'
        vkorc1_unknown = vkorc1 == feature.MISSING

        cyp2c9 = patient['CYP2C9']
        cyp2c9_12 = cyp2c9 == '*1/*2'
        cyp2c9_13 = cyp2c9 == '*1/*3'
        cyp2c9_22 = cyp2c9 == '*2/*2'
        cyp2c9_23 = cyp2c9 == '*2/*3'
        cyp2c9_33 = cyp2c9 == '*3/*3'
        cyp2c9_unknown = cyp2c9 == feature.MISSING

        race: Any = patient.get('race', feature.MISSING)
        african_american = race == 'Black'
        asian = race == 'Asian'
        missing_or_mixed_race = int(race in (feature.MISSING, 'Mixed'))
        amiodarone = patient.get('amiodarone') == 'Yes'
        enzyme_inducer = patient.get('enzyme_inducer') == 'Yes'

        weekly_dose = (5.6044
                       - 0.2614 * age_in_decades
                       + 0.0087 * height_in_cm
                       + 0.0128 * weight_in_kg
                       - 0.8677 * vkorc1_ga
                       - 1.6974 * vkorc1_aa
                       - 0.4854 * vkorc1_unknown
                       - 0.5211 * cyp2c9_12
                       - 0.9357 * cyp2c9_13
                       - 1.0616 * cyp2c9_22
                       - 1.9206 * cyp2c9_23
                       - 2.3312 * cyp2c9_33
                       - 0.2188 * cyp2c9_unknown
                       - 0.1092 * asian
                       - 0.2760 * african_american
                       - 0.1032 * missing_or_mixed_race
                       + 1.1816 * enzyme_inducer
                       - 0.5503 * amiodarone) ** 2

        return weekly_dose / 7.0

    @staticmethod
    def modified_pharmacogenetic(patient: Dict[str, Any]) -> float:
        '''
        Determine warfarin dose using the modified pharmacogenetic IWPC
        formula.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - height (in)
            - weight (lb)
            - VKORC1 ('G/G', 'G/A', 'A/A')
            - CYP2C9 ('*1/*1', '*1/*2', '*1/*3', '*2/*2', '*2/*3', '*3/*3')
            - amiodarone ('Yes', 'No')

        Returns
        -------
        :
            The maintenance dose
        '''
        age = patient['age']
        height_in_cm = patient['height'] * 2.54
        weight_in_kg = patient['weight'] * 0.454

        vkorc1 = patient['VKORC1']
        vkorc1_ga = vkorc1 == 'G/A'
        vkorc1_aa = vkorc1 == 'A/A'

        cyp2c9 = patient['CYP2C9']
        cyp2c9_12 = cyp2c9 == '*1/*2'
        cyp2c9_13 = cyp2c9 == '*1/*3'
        cyp2c9_22 = cyp2c9 == '*2/*2'
        cyp2c9_23 = cyp2c9 == '*2/*3'
        cyp2c9_33 = cyp2c9 == '*3/*3'

        amiodarone = patient.get('amiodarone') == 'Yes'

        weekly_dose = (5.6044
                       - 0.02614 * age
                       + 0.0087 * height_in_cm
                       + 0.0128 * weight_in_kg
                       - 0.8677 * vkorc1_ga
                       - 1.6974 * vkorc1_aa
                       - 0.5211 * cyp2c9_12
                       - 0.9357 * cyp2c9_13
                       - 1.0616 * cyp2c9_22
                       - 1.9206 * cyp2c9_23
                       - 2.3312 * cyp2c9_33
                       - 0.5503 * amiodarone) ** 2

        return weekly_dose / 7.0

    @staticmethod
    def loading_dose(patient: Dict[str, Any]) -> Tuple[float, float, float]:
        '''
        Determine warfarin dose using the modified pharmacogenetic IWPC
        formula.

        Arguments
        ---------
        patient:
            A dictionary of patient characteristics including:
            - age
            - height (in)
            - weight (lb)
            - VKORC1 ('G/G', 'G/A', 'A/A')
            - CYP2C9 ('*1/*1', '*1/*2', '*1/*3', '*2/*2', '*2/*3', '*3/*3')
            - amiodarone ('Yes', 'No')

        Returns
        -------
        :
            A list of warfarin doses for three days
        '''
        maintenance_dose = IWPC.modified_pharmacogenetic(patient)
        cyp2c9 = patient['CYP2C9']

        k24 = {'*1/*1': 0.0189,
               '*1/*2': 0.0158,
               '*1/*3': 0.0132,
               '*2/*2': 0.0130,
               '*2/*3': 0.0090,
               '*3/*3': 0.0075
               }[cyp2c9] * 24

        LD3 = maintenance_dose / ((1 - exp(-k24)) *
                                  (1 + exp(-k24) + exp(-2*k24)))
        # The following dose calculation is based on EU-PACT report page 19
        # Ravvaz uses the same formula, but uses weekly dose. However,
        # EU-PACT explicitly mentions "predicted daily dose (D)"
        LD3_WD = LD3 - maintenance_dose
        loading_doses = (
            maintenance_dose + LD3_WD * 1.5,
            maintenance_dose + LD3_WD,
            maintenance_dose + LD3_WD * 0.5)

        return loading_doses

    def reset(self) -> None:
        '''Reset the dosing protocol'''
        self._doses = []
