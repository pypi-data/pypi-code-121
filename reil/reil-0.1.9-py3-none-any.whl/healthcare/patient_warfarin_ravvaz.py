# -*- coding: utf-8 -*-
'''
PatientWarfarinRavvaz class
===========================

A warfarin patient class with features and parameters of Ravvaz et al. 2016.

Features included in this model are:
* age
* weight
* height
* gender
* race
* tobaco
* amiodarone
* fluvastatin
* CYP2C9
* VKORC1
* MTT_1
* MTT_2
* cyp_1_1
* V1
* V2
* EC_50
'''
from typing import Any, Dict, Optional

from reil.datatypes.feature import FeatureGenerator, FeatureGeneratorSet
from reil.healthcare.mathematical_models import HealthMathModel
from reil.healthcare.patient import Patient
from reil.serialization import serialize
from reil.utils.functions import random_categorical, random_normal_truncated


class PatientWarfarinRavvaz(Patient):
    def __init__(
            self,
            model: HealthMathModel,
            random_seed: Optional[int] = None,
            randomized: bool = True,
            allow_missing_genotypes: bool = True,
            **feature_values: Any) -> None:
        '''
        Parameters
        ----------
        model:
            A `HealthMathModel` to be used to model patient's behavior.

        randomized:
            Whether patient characteristics and model parameters should be
            generated randomly or deterministically.

        feature_values:
            Keyword arguments by which some of the `features` of the patient
            can be determined. For example, if "age" is one of the features,
            age=40.0 will set the initial age to 40.0.
        '''
        self.feature_gen_set = FeatureGeneratorSet((
            FeatureGenerator.continuous(
                name='age',  # (years) Aurora population
                lower=18.0, upper=150.0, mean=67.30, stdev=13.43,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.continuous(
                name='weight',  # (lb) Aurora population
                lower=70.0, upper=500.0, mean=199.24, stdev=54.71,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.continuous(
                name='height',  # (in) Aurora population
                lower=45.0, upper=85.0, mean=66.78, stdev=4.31,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='gender',  # Aurora population
                categories=('Female', 'Male'),
                probabilities=(0.5314, 0.4686),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='race',  # Aurora Avatar Population
                categories=('White', 'Black', 'Asian',
                            'American Indian', 'Pacific Islander'),
                probabilities=(0.9522, 0.0419, 0.0040, 0.0018, 1e-4),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='tobaco',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.9067, 0.0933),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='amiodarone',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.8849, 0.1151),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='fluvastatin',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.9998, 0.0002),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='CYP2C9',  # Aurora Avatar Population
                categories=('*1/*1', '*1/*2', '*1/*3',
                            '*2/*2', '*2/*3', '*3/*3'),
                probabilities=(0.6739, 0.1486, 0.0925, 0.0651, 0.0197, 2e-4),
                generator=random_categorical,
                randomized=randomized,
                allow_missing=allow_missing_genotypes),
            FeatureGenerator.categorical(
                name='VKORC1',  # Aurora Avatar Population
                categories=('G/G', 'G/A', 'A/A'),
                probabilities=(0.3837, 0.4418, 0.1745),
                generator=random_categorical,
                randomized=randomized,
                allow_missing=allow_missing_genotypes),

            # 'sensitivity': FeatureGenerator.categorical(
            #     name='sensitivity',
            #     categories=('normal', 'sensitive', 'highly sensitive'),
            #     generator=lambda f: f.value,
            #     randomized=randomized)
        ))

        self._sensitivity_gen = FeatureGenerator.categorical(
            name='sensitivity',
            categories=('normal', 'sensitive', 'highly sensitive'),
            allow_missing=allow_missing_genotypes)

        self._randomized = randomized
        super().__init__(model, random_seed, **feature_values)
        self._generate_sensitivity()

    def generate(self) -> None:
        super().generate()
        self._generate_sensitivity()

    def _generate_sensitivity(self):
        combo = (
            str(self.feature_set['CYP2C9'].value) +
            str(self.feature_set['VKORC1'].value))

        if combo in ('*1/*1G/G', '*1/*2G/G', '*1/*1G/A'):
            s = 'normal'
        elif combo in (
                '*1/*2G/A', '*1/*3G/A', '*2/*2G/A',
                '*2/*3G/G', '*1/*3G/G', '*2/*2G/G',
                '*1/*2A/A', '*1/*1A/A'):
            s = 'sensitive'
        elif combo in (
                '*3/*3G/G',
                '*3/*3G/A', '*2/*3G/A',
                '*3/*3A/A', '*2/*3A/A', '*2/*2A/A', '*1/*3A/A'):
            s = 'highly sensitive'
        else:
            raise ValueError(
                f'Unknown CYP2C9 and VKORC1 combination: {combo}.')

        self.feature_set += self._sensitivity_gen(s)

    def get_config(self) -> Dict[str, Any]:
        config = super().get_config()
        config.update({'randomized': self._randomized})
        config['internal_states'].update(
            {'sensitivity_gen': serialize(self._sensitivity_gen)})

        return config


class PatientWarfarinBalanced(PatientWarfarinRavvaz):
    def __init__(
            self,
            model: HealthMathModel,
            random_seed: Optional[int] = None,
            randomized: bool = True,
            allow_missing_genotypes: bool = True,
            **feature_values: Any) -> None:
        '''
        Parameters
        ----------
        model:
            A `HealthMathModel` to be used to model patient's behavior.

        randomized:
            Whether patient characteristics and model parameters should be
            generated randomly or deterministically.

        feature_values:
            Keyword arguments by which some of the `features` of the patient
            can be determined. For example, if "age" is one of the features,
            age=40.0 will set the initial age to 40.0.
        '''
        self.feature_gen_set = FeatureGeneratorSet((
            FeatureGenerator.continuous(
                name='age',  # (years) Aurora population
                lower=18.0, upper=150.0, mean=67.30, stdev=13.43,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.continuous(
                name='weight',  # (lb) Aurora population
                lower=70.0, upper=500.0, mean=199.24, stdev=54.71,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.continuous(
                name='height',  # (in) Aurora population
                lower=45.0, upper=85.0, mean=66.78, stdev=4.31,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='gender',  # Aurora population
                categories=('Female', 'Male'),
                probabilities=(0.5314, 0.4686),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='race',  # Aurora Avatar Population
                categories=('White', 'Black', 'Asian',
                            'American Indian', 'Pacific Islander'),
                probabilities=(0.9522, 0.0419, 0.0040, 0.0018, 1e-4),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='tobaco',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.9067, 0.0933),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='amiodarone',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.8849, 0.1151),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='fluvastatin',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.9998, 0.0002),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='CYP2C9',  # Aurora Avatar Population
                categories=('*1/*1', '*1/*2', '*1/*3',
                            '*2/*2', '*2/*3', '*3/*3'),
                # probabilities=(0.6739, 0.1486, 0.0925, 0.0651, 0.0197, 2e-4),
                generator=random_categorical,
                randomized=randomized,
                allow_missing=allow_missing_genotypes),
            FeatureGenerator.categorical(
                name='VKORC1',  # Aurora Avatar Population
                categories=('G/G', 'G/A', 'A/A'),
                # probabilities=(0.3837, 0.4418, 0.1745),
                generator=random_categorical,
                randomized=randomized,
                allow_missing=allow_missing_genotypes),

            # 'sensitivity': FeatureGenerator.categorical(
            #     name='sensitivity',
            #     categories=('normal', 'sensitive', 'highly sensitive'),
            #     generator=lambda f: f.value,
            #     randomized=randomized)
        ))

        self._sensitivity_gen = FeatureGenerator.categorical(
            name='sensitivity',
            categories=('normal', 'sensitive', 'highly sensitive'),
            allow_missing=allow_missing_genotypes)

        self._randomized = randomized
        super(PatientWarfarinRavvaz, self).__init__(
            model, random_seed, **feature_values)
        self._generate_sensitivity()


class PatientWarfarinOversampled(PatientWarfarinRavvaz):
    def __init__(
            self,
            model: HealthMathModel,
            random_seed: Optional[int] = None,
            randomized: bool = True,
            allow_missing_genotypes: bool = True,
            **feature_values: Any) -> None:
        '''
        Parameters
        ----------
        model:
            A `HealthMathModel` to be used to model patient's behavior.

        randomized:
            Whether patient characteristics and model parameters should be
            generated randomly or deterministically.

        feature_values:
            Keyword arguments by which some of the `features` of the patient
            can be determined. For example, if "age" is one of the features,
            age=40.0 will set the initial age to 40.0.
        '''
        self.feature_gen_set = FeatureGeneratorSet((
            FeatureGenerator.continuous(
                name='age',  # (years) Aurora population
                lower=18.0, upper=150.0, mean=67.30, stdev=13.43,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.continuous(
                name='weight',  # (lb) Aurora population
                lower=70.0, upper=500.0, mean=199.24, stdev=54.71,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.continuous(
                name='height',  # (in) Aurora population
                lower=45.0, upper=85.0, mean=66.78, stdev=4.31,
                generator=random_normal_truncated,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='gender',  # Aurora population
                categories=('Female', 'Male'),
                probabilities=(0.5314, 0.4686),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='race',  # Aurora Avatar Population
                categories=('White', 'Black', 'Asian',
                            'American Indian', 'Pacific Islander'),
                probabilities=(0.9522, 0.0419, 0.0040, 0.0018, 1e-4),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='tobaco',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.9067, 0.0933),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='amiodarone',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.8849, 0.1151),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='fluvastatin',  # Aurora Avatar Population
                categories=('No', 'Yes'),
                probabilities=(0.9998, 0.0002),
                generator=random_categorical,
                randomized=randomized),
            FeatureGenerator.categorical(
                name='CYP2C9',  # Aurora Avatar Population
                categories=('*1/*1', '*1/*2', '*1/*3',
                            '*2/*2', '*2/*3', '*3/*3'),
                probabilities=(0.5, 0.1, 0.1, 0.1, 0.1, 0.1),
                generator=random_categorical,
                randomized=randomized,
                allow_missing=allow_missing_genotypes),
            FeatureGenerator.categorical(
                name='VKORC1',  # Aurora Avatar Population
                categories=('G/G', 'G/A', 'A/A'),
                probabilities=(0.3837, 0.4418, 0.1745),
                generator=random_categorical,
                randomized=randomized,
                allow_missing=allow_missing_genotypes),

            # 'sensitivity': FeatureGenerator.categorical(
            #     name='sensitivity',
            #     categories=('normal', 'sensitive', 'highly sensitive'),
            #     generator=lambda f: f.value,
            #     randomized=randomized)
        ))

        self._sensitivity_gen = FeatureGenerator.categorical(
            name='sensitivity',
            categories=('normal', 'sensitive', 'highly sensitive'),
            allow_missing=allow_missing_genotypes)

        self._randomized = randomized
        super(PatientWarfarinRavvaz, self).__init__(
            model, random_seed, **feature_values)
        self._generate_sensitivity()
