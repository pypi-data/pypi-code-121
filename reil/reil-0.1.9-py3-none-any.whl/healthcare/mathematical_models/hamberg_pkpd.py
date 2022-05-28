# -*- coding: utf-8 -*-
'''
HambergPKPD class
=================

A warfarin PK/PD model proposed by Hamberg et al. (2007).
DOI: 10.1038/sj.clpt.6100084
'''
import math
from typing import Any, Dict, Final, List, NamedTuple, Optional, Union

import numpy as np
import reil
from reil.datatypes.feature import (Feature, FeatureGenerator,
                                    FeatureGeneratorSet, FeatureSet)
from reil.healthcare.mathematical_models.health_math_model import \
    HealthMathModel
from reil.utils.functions import random_lognormal_truncated


class DoseEffect(NamedTuple):
    dose: float
    Cs: List[float]  # np.array


class HambergPKPD(HealthMathModel):
    '''
    Hamberg PK/PD model for warfarin.
    '''
    # region: class attributes
    _per_day: Final[int] = 24  # 24

    # Hamberg et al. (2007) - Table 2
    # CL_s: Apparent oral clearance
    _CL_s_1_1: Final = 0.314  # (l/h) CL_s for *1/*1 of a typical 71-yr patient
    _CL_s_genotypes: Final = {  # Effect of genotypes diff. from *1/*1 on CL_s
        '*1/*1': 0.0,
        '*1/*2': 0.315,
        '*1/*3': 0.453,
        '*2/*2': 0.722,
        '*2/*3': 0.690,
        '*3/*3': 0.852}
    _CL_s_age: Final = 0.0091  # Effect of age on CL_s centered around 71 years
    _V1: Final = 13.8  # (l) Apparent central volume of distribution
    _k_aS: Final = 2.0  # (1/hr) Absorption rate constant
    _Q: Final = 0.131    # (l/h) Apparent intercompartmental clearance
    _V2: Final = 6.59  # (l) Apparent peripheral volume of distribution

    _omega_CL_s: Final = 0.310  # Interindividual variability for CL_s
    _omega_V1: Final = 0.262  # Interindividual variability for V1
    _omega_V2: Final = 0.991  # Interindividual variability for V2

    _sigma_s: Final = 0.0908  # Residual error after single dose
    _sigma_ss: Final = 0.301  # Residual error after steady-state dose

    # Hamberg et al. (2007) - Table 4
    _E_max: Final = 1.0
    _gamma: Final = 0.424
    _EC_50_GG: Final = 4.61  # (mg/l) EC_50 for VKORC1 genotype G/G
    _EC_50_GA: Final = 3.02  # (mg/l) EC_50 for VKORC1 genotype G/A
    _EC_50_AA: Final = 2.20  # (mg/l) EC_50 for VKORC1 genotype A/A
    _MTT_1: Final = 11.6  # (h) Mean Transit Time
    _MTT_2: Final = 120  # (h) Mean Transit Time
    _lambda: Final = 3.61

    _omega_MTT_1: Final = 0.141  # Interindividual variability for MTT_1
    _omega_MTT_2: Final = 1.020  # Interindividual variability for MTT_2
    _omega_EC_50: Final = 0.409  # Interindividual variability for EC_50
    _sigma_INR: Final = 0.0325  # Residual error for INR

    # Hamberg et al. (2007) - Misc.
    _INR_max: Final = 20.0  # page 538

    # Note: In Hamberg et al. (2007), BASE_i is the measured baseline INR
    # for patients, but Ravvaz fixed it to 1.
    _baseINR: Final = 1.0    # Ravvaz source code

    __log_MTT_1 = math.log(_MTT_1)
    __sqrt_omega_MTT_1 = math.sqrt(_omega_MTT_1)
    __log_MTT_2 = math.log(_MTT_2)
    __sqrt_omega_MTT_2 = math.sqrt(_omega_MTT_2)
    __log_CL_s_1_1 = math.log(_CL_s_1_1)
    __sqrt_omega_CL_s = math.sqrt(_omega_CL_s)
    __log_V1 = math.log(_V1)
    __sqrt_omega_V1 = math.sqrt(_omega_V1)
    __log_V2 = math.log(_V2)
    __sqrt_omega_V2 = math.sqrt(_omega_V2)
    __log_EC_50_GG = math.log(_EC_50_GG)
    __log_EC_50_GA = math.log(_EC_50_GA)
    __log_EC_50_AA = math.log(_EC_50_AA)
    __sqrt_omega_EC_50 = math.sqrt(_omega_EC_50)

    __FeatureGenerator_EC_50_non_random = FeatureGenerator.continuous(
        name='EC_50',  # (mg/L) Hamberg PK/PD
        mean=1.0,
        stdev=__sqrt_omega_EC_50,
        generator=random_lognormal_truncated,
        randomized=False)

    __FeatureGenerator_EC_50_GG = FeatureGenerator.continuous(
        name='EC_50',  # (mg/L) Hamberg PK/PD
        mean=__log_EC_50_GG,
        stdev=__sqrt_omega_EC_50,
        generator=random_lognormal_truncated,
        randomized=True)

    __FeatureGenerator_EC_50_GA = FeatureGenerator.continuous(
        name='EC_50',  # (mg/L) Hamberg PK/PD
        mean=__log_EC_50_GA,
        stdev=__sqrt_omega_EC_50,
        generator=random_lognormal_truncated,
        randomized=True)

    __FeatureGenerator_EC_50_AA = FeatureGenerator.continuous(
        name='EC_50',  # (mg/L) Hamberg PK/PD
        mean=__log_EC_50_AA,
        stdev=__sqrt_omega_EC_50,
        generator=random_lognormal_truncated,
        randomized=True)

    _parameter_generators = FeatureGeneratorSet((
        FeatureGenerator.continuous(
            name='MTT_1',  # (hours) Hamberg PK/PD
            mean=__log_MTT_1,
            stdev=__sqrt_omega_MTT_1,
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='MTT_2',  # (hours) Hamberg PK/PD
            # Hamberg et al. (2007) - Table 4
            mean=__log_MTT_2,
            stdev=__sqrt_omega_MTT_2,
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='CL_S_cyp_1_1',  # (l/h) Hamberg PK/PD
            mean=__log_CL_s_1_1,
            stdev=__sqrt_omega_CL_s,
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='V1',  # (L) Volume in central compartment
            mean=__log_V1,
            stdev=__sqrt_omega_V1,
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='V2',  # (L) volume in peripheral compartment
            mean=__log_V2,
            stdev=__sqrt_omega_V2,
            generator=random_lognormal_truncated,
            randomized=True),
    ))

    # endregion

    def __init__(
            self, randomized: bool = True,
            cache_size: int = 30) -> None:
        """
        Arguments
        ---------
        randomized:
            Whether to have random effects in patient response to warfarin.

        cache_size:
            Size of the cache used to store pre-computed values needed for
            INR computation.
        """
        self._randomized = randomized
        self._cache_size = math.ceil(cache_size)
        self._last_computed_day: int = 0
        self._cached_cs: Dict[float, List[float]] = {}
        self._age = None

    @classmethod
    def generate(
            cls,
            rnd_generators: reil.RandomGeneratorsType,
            input_features: Optional[FeatureSet] = None,
            **kwargs: Any) -> FeatureSet:
        with reil.random_generator_context(*rnd_generators):
            feature_set = super(HambergPKPD, cls).generate(
                rnd_generators=rnd_generators,
                input_features=input_features, **kwargs)
            temp = (input_features or {}).get('VKORC1')
            if temp is None:
                if 'EC_50' not in kwargs:
                    raise ValueError(
                        'Either input_features should contain VKORC1 or '
                        'EC_50 should be provided as a keyword argument.'
                    )
                feature_set += cls.__FeatureGenerator_EC_50_non_random(
                    kwargs['EC_50'])

            else:
                vkorc1 = temp.value
                if vkorc1 == 'G/G':
                    feature_set += cls.__FeatureGenerator_EC_50_GG(
                        kwargs.get('EC_50'))
                elif vkorc1 in ('G/A', 'A/G'):
                    feature_set += cls.__FeatureGenerator_EC_50_GA(
                        kwargs.get('EC_50'))
                else:  # 'A/A'
                    feature_set += cls.__FeatureGenerator_EC_50_AA(
                        kwargs.get('EC_50'))

        return feature_set

    def setup(
            self, rnd_generators: reil.RandomGeneratorsType,
            input_features: Optional[FeatureSet] = None) -> None:
        '''
        Set up the model.

        Arguments
        ---------
        arguments:
            `Feature` instances required to setup the model.

        Notes
        -----
        This model requires `age`, `CYP2C9`, `MTT_1`, `MTT_2`, `EC_50`,
        `cyp_1_1`, `V1`, and `V2`. The genotype of `VKORC1` is not directly
        used in this implementation. Instead, one should use it to generate
        `EC_50`. See `WarfarinPatient` class.

        Raises
        ------
        ValueError:
            `CYP2C9` is not one of the acceptable values:
            *1/*1, *1/*2, *1/*3, *2/*2, *2/*3, *3/*3
        '''

        if input_features is None:
            raise TypeError('input_features expected.')

        args = input_features.value

        self._age = float(args['age'])  # type: ignore
        self._CYP2C9 = str(args['CYP2C9'])
        self._observed_MTT_1 = float(args['MTT_1'])  # type: ignore
        self._observed_MTT_2 = float(args['MTT_2'])  # type: ignore
        self._observed_V1 = float(args['V1'])  # type: ignore
        self._observed_V2 = float(args['V2'])  # type: ignore
        self._EC_50 = float(args['EC_50'])  # type: ignore
        self._CL_S_cyp_1_1 = float(args['CL_S_cyp_1_1'])  # type: ignore

        if self._CYP2C9 not in self._CL_s_genotypes:
            raise ValueError('The CYP2C9 genotype not recognized!')

        # Note:
        # Hamberg et al. (2007) says "CLS was reduced with increasing age,
        # decreasing by approximately 9% per decade". However, it does not say
        # whether it applies to younger than 71 or not. Ravvaz assumed that it
        # does not, but Figure 3 in Hamberg et al. (2007) shows a 50-year-old
        # patient has a lower INR than a 70-year-old. So, it applies!
        CL_s = self._CL_S_cyp_1_1 * (
            1.0 - (self._CL_s_age * (self._age - 71.0))
        ) * (1 - self._CL_s_genotypes[self._CYP2C9])

        # -------- Implementation of the two compartment model ------------
        # Adapted from Ravvaz source code in R
        # Similar to "Equations to use for time points when absorption can
        # occur and compartment A is unsaturated" available at
        # http://www.rsc.org/suppdata/c7/md/c7md00586e/c7md00586e1.pdf
        # There, compartments B and C are equivalent of compartments 1 and 2
        # here. Also, k_1...k_4 are K_aS, k12, k21, k10, respectively.
        # Note that $x_B^0$ and $x_C^0$ terms are zero as described in that
        # document.

        # bioavilability fraction 0-1 (from: "Applied Pharmacokinetics &
        # Pharmacodynamics 4th edition, p.717", some other references)
        F = 0.9

        k12 = self._Q / self._observed_V1  # Central to peripheral distribution constant
        k21 = self._Q / self._observed_V2  # Peripheral to central distribution constant
        k10 = CL_s / self._observed_V1  # Elimination rate constant

        b = k10 + k21 + k12
        c = k10 * k21

        # Alpha: distribution phase slope (-alpha)
        # Beta: elimination phase slope (-beta)
        alpha = (b + math.sqrt(b ** 2 - 4 * c)) / 2
        beta = (b - math.sqrt(b ** 2 - 4 * c)) / 2

        # Note: Here we halved the value for KaF_2V1, because half of the
        # warfarin is S, and only S affects the INR.
        kaF_2V1 = (self._k_aS * F / 2) / self._observed_V1

        # $C_s$ = c_{\k_1}\exp{-k_1 t}
        #       + c_{\alpha}\exp{-\alpha t}
        #       + c_{\beta}\exp{-\beta t}
        coef_alpha = (
            (k21 - alpha)
            / ((self._k_aS - alpha) * (beta - alpha))
        ) * kaF_2V1
        coef_beta = (
            (k21 - beta)
            / ((self._k_aS - beta) * (alpha - beta))
        ) * kaF_2V1
        coef_k_a = (
            (k21 - self._k_aS)
            / ((self._k_aS - alpha) * (self._k_aS - beta))
        ) * kaF_2V1

        self._coefs = np.array([coef_alpha, coef_beta, coef_k_a])
        self._exps = np.array([alpha, beta, self._k_aS])

        # ---- End of the implementation of the two compartment model -------

        # Note: According to Hamberg et al. (2007) pp. 538, $ktr_1=1/MTT_1$
        # However, Ravvaz set it to $6/MTT_1$. It must be because we have
        # 6 compartment amounts, and total $MTT_1$ for the whole chain is
        # 11.6 h (Figure 2), so each should take $\frac{1}{6} MTT_1$
        ktr1 = 6.0 / self._observed_MTT_1  # (1/hours)
        ktr2 = 1.0 / self._observed_MTT_2  # (1/hours)
        self._ktr = np.array([ktr1] * 6 + [0.0, ktr2])  # type: ignore
        self._EC_50_gamma = self._EC_50 ** self._gamma

        self._A = np.array([0.0] + [1.0] * 8)  # type: ignore
        self._last_computed_day = 0

        self._dose_records: Dict[int, DoseEffect] = {}
        self._computed_INRs: Dict[int, float] = {}  # daily

        detailed_cache_size = self._cache_size * self._per_day

        if self._randomized:
            self._random_generator = rnd_generators[1]

            def _gen_err():  # type: ignore
                return np.exp(  # type: ignore
                    self._random_generator.normal(
                        0.0, self._sigma_ss, detailed_cache_size))

            def _gen_exp_e_INR():  # type: ignore
                return np.exp(  # type: ignore
                    self._random_generator.normal(
                        0.0, self._sigma_INR, self._cache_size))
        else:
            def _gen_err():
                return np.ones(shape=detailed_cache_size)

            def _gen_exp_e_INR():
                return np.ones(shape=self._cache_size)

        self._gen_err = _gen_err
        self._gen_exp_e_INR = _gen_exp_e_INR

        self._current_cache_size = self._cache_size
        # Stead-state has higher variance, and our work is in a sense
        # steady-state dosing. So, we only use `ss` case for errors.
        self._err_list = self._gen_err()  # hourly
        # if self._randomized:
        #     self._err_list[0] = np.exp(  # type: ignore
        #         self._random_generator.normal(0.0, self._sigma_s))

        self._exp_e_INR_list = self._gen_exp_e_INR()  # daily

        self._cached_cs = self._base_concentration(
            coefs=self._coefs, exps=self._exps,
            max_time=detailed_cache_size)
        self._total_cs = np.array([0.0] * detailed_cache_size)  # hourly
        # For day 0, with baseINR of 1.0 and A=[1]x8, only the random term remains
        # self._computed_INRs[0] = self._exp_e_INR_list[0]

    def _expand_caches(self, segment_count: int = 1):
        per_day = self._per_day
        self._current_cache_size += self._cache_size * segment_count

        self._err_list = np.concatenate(
            [self._err_list, *(self._gen_err() for _ in range(segment_count))],
            axis=0)
        self._exp_e_INR_list = np.concatenate(
            [
                self._exp_e_INR_list,
                *(self._gen_exp_e_INR() for _ in range(segment_count))],
            axis=0)

        self._cached_cs = self._base_concentration(
            coefs=self._coefs, exps=self._exps,
            max_time=self._current_cache_size * per_day)

        self._total_cs = np.array([0.0] * self._current_cache_size * per_day)

        for day, (dose, _) in self._dose_records.items():
            cs = self._pad_and_dose(
                cs=self._cached_cs, dose=dose,
                pad=day * per_day)
            self._dose_records[day] = DoseEffect(dose, cs)
            self._total_cs += cs

    def run(self, **inputs: Any) -> Dict[str, Any]:
        '''
        Run the model.

        Arguments
        ---------
        inputs:
            - A dictionary called "dose" with days for each dose as keys and
              the amount of dose as values.
            - A list called "measurement_days" that shows INRs of which days
              should be returned.

        Returns
        -------
        :
            A dictionary with keyword "INR" and a list of doses for the
            specified days.
        '''
        self.prescribe(inputs.get('dose', {}))

        if days := inputs.get('measurement_days'):
            return {'INR': self.INR(days)}

        return {'INR': {}}

    @property
    def dose(self) -> Dict[int, float]:
        '''
        Return doses for each day.

        Returns
        -------
        :
            A dictionary with days as keys and doses as values.
        '''
        return {t: info.dose
                for t, info in self._dose_records.items()}

    def prescribe(self, dose: Dict[int, float]) -> None:
        '''
        Add warfarin doses at the specified days.

        Arguments
        ---------
        dose:
            A dictionary with days as keys and doses as values.
        '''
        # if a dose is added ealier in the list, INRs should be updated all
        # together because the history of "A" array is not kept.
        try:
            if self._last_computed_day > min(dose.keys()):
                self._last_computed_day = 0
        except ValueError:  # no doses
            pass

        if max(dose or {0: 0.0}) >= self._current_cache_size:
            segment_count = (
                max(dose) - self._current_cache_size
            ) // self._cache_size + 1
            self._expand_caches(segment_count=segment_count)

        for day, _dose in dose.items():
            if _dose != 0.0:
                if day in self._dose_records:
                    prev_dose = self._dose_records[day][0]
                else:
                    prev_dose = 0.0

                new_dose = prev_dose + _dose
                if new_dose < 0.0:
                    raise ValueError(
                        'Total dose for a day cannot be negative.')

                cs = self._pad_and_dose(
                    cs=self._cached_cs, dose=new_dose,
                    pad=day * self._per_day)

                self._dose_records[day] = DoseEffect(new_dose, cs)
                self._total_cs += cs

    def INR(self, measurement_days: Union[int, List[int]]) -> List[float]:
        '''
        Compute INR values for the specified days.

        Arguments
        ---------
        measurement_days:
            One of a list of all days for which INR should be computed.

        Returns
        -------
        :
            A list of INRs for the specified days.
        '''
        days: List[int]

        days = (measurement_days if hasattr(measurement_days, '__iter__')
                else [measurement_days])  # type: ignore

        if max(days) >= self._current_cache_size:
            segment_count = (
                max(days) - self._current_cache_size
            ) // self._cache_size + 1
            self._expand_caches(segment_count=segment_count)

        not_computed_days = set(days).difference(self._computed_INRs)
        if (not_computed_days and
                min(not_computed_days) < self._last_computed_day):
            self._last_computed_day = int(0)
            self._computed_INRs = {}
            not_computed_days = days

        if self._last_computed_day == 0:
            self._A = np.array([0.0] + [1.0] * 8)  # type: ignore

        stop_points = [self._last_computed_day] + sorted(
            list(not_computed_days))
        self._last_computed_day = stop_points[-1]

        start_day = stop_points[0]
        start_point = start_day * HambergPKPD._per_day
        all_points = list(range(
            math.floor(start_point),
            math.ceil(stop_points[-1] * HambergPKPD._per_day)))

        Cs_gamma = np.power(  # type: ignore
            self._total_cs[all_points] *
            self._err_list[all_points],  # type: ignore
            HambergPKPD._gamma)
        inflow = 1.0 - np.divide(  # type: ignore
            HambergPKPD._E_max * Cs_gamma,  # type: ignore
            self._EC_50_gamma + Cs_gamma)

        A = self._A
        ktr = self._ktr
        for d1, d2 in zip(stop_points[:-1], stop_points[1:]):
            steps = range(
                math.floor(d1 * HambergPKPD._per_day),
                math.ceil(d2 * HambergPKPD._per_day))
            for dt in steps:
                A[0] = A[7] = inflow[dt - start_point]
                A[1:] += ktr * (A[:-1] - A[1:])
                # A = np.clip(A, a_min=0.0, a_max=1.0)
            self._computed_INRs[d2] = np.multiply(  # type: ignore
                HambergPKPD._baseINR +
                HambergPKPD._INR_max * np.power(  # type: ignore
                    1.0 - A[6] * A[8], HambergPKPD._lambda),
                self._exp_e_INR_list[int(d2)])  # type: ignore

        self._A = A

        return [self._computed_INRs[i] for i in days]

    @staticmethod
    def _base_concentration(coefs, exps, max_time):
        times = range(max_time)
        # clipping to avoid underflow. We do not need to be that accurate!
        exponents = np.clip(
            np.matmul(
                -np.expand_dims(exps, axis=1), np.expand_dims(times, axis=0)),
            a_min=-100.0, a_max=None)
        temp = np.exp(exponents)  # type: ignore
        base_cs = np.matmul(
            np.expand_dims(coefs, axis=0), temp)  # type: ignore
        base_cs = np.clip(base_cs, a_min=0.0, a_max=None)

        return np.squeeze(base_cs)

    @staticmethod
    def _pad_and_dose(cs, dose: float = 1.0, pad: int = 0):
        cs = np.multiply(cs, [dose])  # type: ignore
        padded_cs = np.pad(cs, [[pad, 0]], 'constant')

        return padded_cs[:cs.shape[0]]  # type: ignore

    def get_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = super().get_config()
        config.update({
            'randomized': self._randomized,
            'cache_size': self._cache_size})
        if self._age is not None:
            config.update(
                dict(
                    random_generator=self._random_generator,
                    age=self._age,
                    CYP2C9=self._CYP2C9,
                    MTT_1=self._observed_MTT_1,
                    MTT_2=self._observed_MTT_2,
                    V1=self._observed_V1,
                    V2=self._observed_V2,
                    EC_50=self._EC_50,
                    CL_S_cyp_1_1=self._CL_S_cyp_1_1,
                    dose=self.dose))

        return config

    @classmethod
    def from_config(cls, config: Dict[str, Any]):
        instance = cls(
            randomized=config['randomized'],
            cache_size=config['cache_size'])
        if 'age' in config:
            input_features = FeatureSet(
                Feature.categorical(name=name, value=config[name])
                for name in (
                    'age', 'CYP2C9', 'MTT_1', 'MTT_2',
                    'V1', 'V2', 'EC_50', 'CL_S_cyp_1_1'))
            instance.setup(
                rnd_generators=(
                    None, config['random_generator'], None),  # type: ignore
                input_features=input_features)

            instance.prescribe(config['dose'])

            return instance
