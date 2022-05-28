# -*- coding: utf-8 -*-
'''
HambergPKPD class
=================

A warfarin PK/PD model proposed by Hamberg et al. (2007).
DOI: 10.1038/sj.clpt.6100084
'''
import math
from typing import (Any, Callable, Dict, Final, Iterable, List, NamedTuple,
                    NewType, Optional, Union)

import numpy as np
import reil
from reil.datatypes.feature import (FeatureGenerator, FeatureGeneratorSet,
                                    FeatureSet)
from reil.healthcare.mathematical_models.health_math_model import \
    HealthMathModel
from reil.utils.functions import random_lognormal_truncated

Day = NewType('Day', float)
Hour = NewType('Hour', int)
dT = NewType('dT', int)


class DoseEffect(NamedTuple):
    dose: float
    Cs: Callable[[Iterable[dT]], List[float]]


class HambergPKPD(HealthMathModel):
    '''
    Hamberg PK/PD model for warfarin.
    '''
    _per_hour: int = 1

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

    _parameter_generators = FeatureGeneratorSet((
        FeatureGenerator.continuous(
            name='MTT_1',  # (hours) Hamberg PK/PD
            mean=math.log(_MTT_1),
            stdev=math.sqrt(_omega_MTT_1),
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='MTT_2',  # (hours) Hamberg PK/PD
            # Hamberg et al. (2007) - Table 4
            mean=math.log(_MTT_2),
            stdev=math.sqrt(_omega_MTT_2),
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='CL_S_cyp_1_1',  # (l/h) Hamberg PK/PD
            mean=math.log(_CL_s_1_1),
            stdev=math.sqrt(_omega_CL_s),
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='V1',  # (L) Volume in central compartment
            mean=math.log(_V1),
            stdev=math.sqrt(_omega_V1),
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='V2',  # (L) volume in peripheral compartment
            mean=math.log(_V2),
            stdev=math.sqrt(_omega_V2),
            generator=random_lognormal_truncated,
            randomized=True),
    ))

    # pre-computing to gain some speed boost!
    __log_EC_50_GG: Final[float] = math.log(_EC_50_GG)
    __log_EC_50_GA: Final[float] = math.log(_EC_50_GA)
    __log_EC_50_AA: Final[float] = math.log(_EC_50_AA)
    __sqrt_omega_EC_50: Final[float] = math.sqrt(_omega_EC_50)

    def __init__(
            self, randomized: bool = True,
            cache_size: Day = Day(30)) -> None:
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
        self._last_computed_day: Day = Day(0)
        self._cached_cs: Dict[float, List[float]] = {}

    @classmethod
    def generate(
            cls,
            rnd_generators: reil.RandomGeneratorsType,
            input_features: Optional[FeatureSet] = None,
            **kwargs: Any) -> FeatureSet:

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

            feature_set += FeatureGenerator.continuous(
                name='EC_50',  # (mg/L) Hamberg PK/PD
                mean=1.0,
                stdev=HambergPKPD.__sqrt_omega_EC_50,
                generator=random_lognormal_truncated,
                randomized=False)(kwargs['EC_50'])

        else:
            vkorc1 = temp.value
            if vkorc1 == 'G/G':
                mean = HambergPKPD.__log_EC_50_GG
            elif vkorc1 in ('G/A', 'A/G'):
                mean = HambergPKPD.__log_EC_50_GA
            else:  # 'A/A'
                mean = HambergPKPD.__log_EC_50_AA

            feature_set += FeatureGenerator.continuous(
                name='EC_50',  # (mg/L) Hamberg PK/PD
                mean=mean,
                stdev=HambergPKPD.__sqrt_omega_EC_50,
                generator=random_lognormal_truncated,
                randomized=True)(kwargs.get('EC_50'))

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
        # Note: In Hamberg et al. (2007), BASE_i is the measured baseline INR
        # for patients, but Ravvaz fixed it to 1.
        self._baseINR = 1.0    # Ravvaz source code

        if input_features is None:
            raise TypeError(
                'age, CYP2C9, VKORC1, MTT_1, MTT_2, V1, V2, EC_50, CL_S_cyp_1_1 are required.'
                ' Got None!')

        args = input_features.value

        age = float(args['age'])  # type: ignore
        CYP2C9 = str(args['CYP2C9'])
        MTT_1 = float(args['MTT_1'])  # type: ignore
        MTT_2 = float(args['MTT_2'])  # type: ignore
        V1 = float(args['V1'])  # type: ignore
        V2 = float(args['V2'])  # type: ignore
        EC_50 = float(args['EC_50'])  # type: ignore
        CL_S_cyp_1_1 = float(args['CL_S_cyp_1_1'])  # type: ignore

        if CYP2C9 not in self._CL_s_genotypes:
            raise ValueError('The CYP2C9 genotype not recognized!')

        # Note:
        # Hamberg et al. (2007) says "CLS was reduced with increasing age,
        # decreasing by approximately 9% per decade". However, it does not say
        # whether it applies to younger than 71 or not. Ravvaz assumed that it
        # does not, but Figure 3 in Hamberg et al. (2007) shows a 50-year-old
        # patient has a lower INR than a 70-year-old. So, it applies!
        CL_s = CL_S_cyp_1_1 * (
            1.0 - (self._CL_s_age * (age - 71.0))
        ) * (1 - self._CL_s_genotypes[CYP2C9])

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

        k12 = self._Q / V1  # Central to peripheral distribution constant
        k21 = self._Q / V2  # Peripheral to central distribution constant
        k10 = CL_s / V1  # Elimination rate constant

        b = k10 + k21 + k12
        c = k10 * k21

        # Alpha: distribution phase slope (-alpha)
        # Beta: elimination phase slope (-beta)
        self._alpha = (b + math.sqrt(b ** 2 - 4*c)) / 2
        self._beta = (b - math.sqrt(b ** 2 - 4*c)) / 2

        # Note: Here we halved the value for KaF_2V1, because half of the
        # warfarin is S, and only S affects the INR.
        kaF_2V1 = (self._k_aS * F / 2) / V1

        # $C_s$ = c_{\k_1}\exp{-k_1 t}
        #       + c_{\alpha}\exp{-\alpha t}
        #       + c_{\beta}\exp{-\beta t}
        self._coef_alpha = (
            (k21 - self._alpha)
            / ((self._k_aS - self._alpha)*(self._beta - self._alpha))
        ) * kaF_2V1
        self._coef_beta = (
            (k21 - self._beta)
            / ((self._k_aS - self._beta)*(self._alpha - self._beta))
        ) * kaF_2V1
        self._coef_k_a = (
            (k21 - self._k_aS)
            / ((self._k_aS - self._alpha)*(self._k_aS - self._beta))
        ) * kaF_2V1

        # ---- End of the implementation of the two compartment model -------

        # Note: According to Hamberg et al. (2007) pp. 538, $ktr_1=1/MTT_1$
        # However, Ravvaz set it to $6/MTT_1$. It must be because we have
        # 6 compartment amounts, and total $MTT_1$ for the whole chain is
        # 11.6 h (Figure 2), so each should take $\frac{1}{6} MTT_1$
        ktr1 = 6.0 / MTT_1  # (1/hours)
        ktr2 = 1.0 / MTT_2  # (1/hours)
        self._ktr = np.array([0.0] + [ktr1] * 6 + [0.0, ktr2])  # type: ignore
        self._EC_50_gamma = EC_50 ** self._gamma

        self._dose_records: Dict[Day, DoseEffect] = {}
        cs_size = self._cache_size * 24 * self._per_hour
        self._total_cs = np.array([0.0] * cs_size)  # type: ignore  hourly
        # self._computed_INRs = [0.0] * (self._cache_size + 1)  # daily
        self._computed_INRs: Dict[Day, float] = {}  # daily
        self._err_list: List[List[float]] = []  # hourly
        self._err_ss_list: List[List[float]] = []  # hourly
        self._exp_e_INR_list: List[List[float]] = []  # daily

        day_0 = Day(0)
        dt_0 = dT(0)
        self._last_computed_day = day_0

        temp_cs_generator = self._CS_function_generator(dt_0, 1.0)
        self._cached_cs = {
            1.0: temp_cs_generator(range(cs_size))}  # type: ignore

        self._A = np.array([0.0] + [1.0] * 8)  # type: ignore

        # running _err to initialize their cache for reproducibility purposes
        self._err(dt_0, False)
        self._err(dt_0, True)
        self._computed_INRs[day_0] = self._INR(self._A, day_0)

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
        self.dose = inputs.get('dose', {})

        if days := inputs.get('measurement_days'):
            return {'INR': self.INR(days)}

        return {'INR': {}}

    @property
    def dose(self) -> Dict[Day, float]:
        '''
        Return doses for each day.

        Returns
        -------
        :
            A dictionary with days as keys and doses as values.
        '''
        return {t: info.dose
                for t, info in self._dose_records.items()}

    @dose.setter
    def dose(self, dose: Dict[Day, float]) -> None:
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
                self._last_computed_day = Day(0)
        except ValueError:  # no doses
            pass

        for day, _dose in dose.items():
            if _dose != 0.0:
                dt = dT(math.ceil(day * 24 * self._per_hour))
                if day in self._dose_records:
                    # TODO: Implement!
                    raise NotImplementedError

                self._dose_records[day] = DoseEffect(
                    _dose, self._CS_function_generator(dt, _dose))

                self._total_cs += np.array(  # type: ignore
                    self._dose_records[day].Cs(range(
                        self._cache_size * 24 * self._per_hour)  # type: ignore
                    )
                )

    def INR(self, measurement_days: Union[Day, List[Day]]) -> List[float]:
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
        days: List[Day]

        days = (measurement_days if hasattr(measurement_days, '__iter__')
                else [measurement_days])  # type: ignore

        not_computed_days = set(days).difference(self._computed_INRs)
        if (not_computed_days and
                min(not_computed_days) < self._last_computed_day):
            self._last_computed_day = Day(0)
            self._computed_INRs = {}
            not_computed_days = days

        if self._last_computed_day == 0:
            self._A = np.array([0.0] + [1.0] * 8)  # type: ignore

        stop_points = [self._last_computed_day] + list(not_computed_days)
        for d1, d2 in zip(stop_points[:-1], stop_points[1:]):
            delta_Ts = 24 * self._per_hour
            for dt in range(int(d1 * delta_Ts), int(d2 * delta_Ts)):
                self._A[0] = self._A[7] = self._inflow(dt)  # type: ignore
                self._A[1:] += self._ktr[1:] * \
                    (self._A[0:-1] - self._A[1:]) / self._per_hour

            self._computed_INRs[d2] = self._INR(self._A, Day(int(d2)))

        self._last_computed_day = stop_points[-1]

        return [self._computed_INRs[i] for i in days]

    def _CS_function_generator(
            self, dt_dose: dT, dose: float
    ) -> Callable[[Iterable[dT]], List[float]]:
        '''
        Generate a Cs function.

        Arguments
        ---------
        dt_dose:
            The time in which the dose is administered.

        dose:
            The value of the dose administered.

        Returns
        -------
        :
            A function that gets the time and returns that time's
            warfarin concentration.

        Notes
        -----
        To speed up the process, the generated function uses a pre-computed
        cache of concentrations and only computes the concentration
        if the requested day is beyond the cached range.
        '''
        if dose == 1.0:
            cached_cs_temp = []
        else:
            if dose not in self._cached_cs:
                self._cached_cs[dose] = [dose * cs
                                         for cs in self._cached_cs[1.0]]
            cached_cs_temp = self._cached_cs[dose]

        def Cs(dts: Iterable[dT]) -> List[float]:
            '''
            Get delta_t list and return the warfarin concentration of
            those times.

            Arguments
            ---------
            dts:
                The times for which concentration value is needed.

            Returns
            -------
            :
                Warfarin concentration
            '''
            max_diff = len(cached_cs_temp)
            coef_alpha = self._coef_alpha
            coef_beta = self._coef_beta
            coef_k_a = self._coef_k_a
            alpha = self._alpha
            beta = self._beta
            k_aS = self._k_aS

            # For hour_diff == 0, the Cs equation itself is zero, so included
            # it in the main if to avoid unnecessary computation.
            return [
                0.0 if (dt_diff := dt - dt_dose) <= 0
                else (
                    cached_cs_temp[dt_diff] if dt_diff < max_diff
                    else (
                        coef_alpha *
                        math.exp(-alpha * dt_diff / self._per_hour) +
                        coef_beta *
                        math.exp(-beta * dt_diff / self._per_hour) +
                        coef_k_a *
                        math.exp(-k_aS * dt_diff / self._per_hour)
                    ) * dose
                ) for dt in dts]

        return Cs

    def _err(self, dt: dT, ss: bool = False) -> float:
        '''
        Generate error term for the requested day.

        Arguments
        ---------
        dt:
            The time for which the error is requested.

        ss:
            Whether the error is for the steady-state case. For single dose
            it should be `False`, and for multiple doses, it should be `True`.

        Returns
        -------
        :
            The error value.

        Notes
        -----
        To speed up the process and generate reproducible results in each run,
        the errors are cached in batches.
        For each call of the function, the cached error is returned. If
        the `hour` is beyond the cached range, a new range of error values
        are generated and added to the cache.
        Also, error is per hour. So, for any fraction of hour, the same
        value will be returned.
        '''
        if self._randomized:
            h = dt // self._per_hour
            hourly_cache_size = self._cache_size * 24
            index_0 = h // hourly_cache_size
            index_1 = h % hourly_cache_size
            e_list = self._err_ss_list if ss else self._err_list
            try:
                return e_list[index_0][index_1]
            except IndexError:
                missing_rows = index_0 - len(e_list) + 1
                stdev = self._sigma_ss if ss else self._sigma_s
                for _ in range(missing_rows):
                    e_list.append(np.exp(np.random.normal(  # type:ignore
                        0, stdev, hourly_cache_size)))

            return e_list[index_0][index_1]
        else:
            return 1.0

    def _exp_e_INR(self, d: Day) -> float:
        '''
        Generate exp(error) term of INR for the requested day.

        Arguments
        ---------
        d:
            The day for which the error is requested.

        Returns
        -------
        :
            The error value.

        Notes
        -----
            error is generated per day. So, if the given `d` is fractional,
            it will be truncated and the respective error is returned.

            To speed up the process and generate reproducible results in each
            run, the errors are cached in batches.
            For each call of the function, the cached error is returned. If
            the `day` is beyond the cached range, a new range of error values
            are generated and added to the cache.
        '''
        _d = int(d)
        if self._randomized:
            index_0 = _d // self._cache_size
            index_1 = _d % self._cache_size
            try:
                return self._exp_e_INR_list[index_0][index_1]
            except IndexError:
                missing_rows = index_0 - len(self._exp_e_INR_list) + 1
                for _ in range(missing_rows):
                    self._exp_e_INR_list.append(
                        np.exp(np.random.normal(  # type:ignore
                            0, self._sigma_INR,
                            self._cache_size)))

            return self._exp_e_INR_list[index_0][index_1]

        else:
            return 1.0

    def _inflow(self, t: dT) -> float:
        '''
        Compute the warfarin concentration that enters the two compartments
        in the PK/PD model.

        Arguments
        ---------
        t:
            The time for which the input is requested.
            t = Hours * _per_hour + delta_t

        Returns
        -------
        :
            The input value.

        Notes
        -----
        To speed up the process, total concentration is being cached for a
        number of days. For days beyond this range, concentration values are
        computed and used on each call.
        '''
        try:
            Cs = self._total_cs[t]
        except IndexError:
            Cs = sum(v.Cs([t])[0]
                     for v in self._dose_records.values())

        Cs_gamma = (Cs * self._err(t, True)) ** self._gamma
        inflow = 1 - (
            (self._E_max * Cs_gamma) / (self._EC_50_gamma + Cs_gamma))

        return inflow

    def _INR(self, A: np.ndarray, d: Day) -> float:
        '''
        Compute the INR on day `d`.

        Arguments
        ---------

        d:
            The day for which the input is requested.

        Returns
        -------
        :
            The INR value.

        Notes
        -----
        To speed up the process, total concentration is being cached for a
        number of days. For days beyond this range, concentration values are
        computed and used on each call.
        '''

        # Note: we defined `A` in such a way to compute changes in `A`s
        # easier. In our implementation, `A8` is the `A7` in Hamberg et al.
        return (self._baseINR +
                (self._INR_max * ((1 - A[6]*A[8]) ** self._lambda))
                ) * self._exp_e_INR(d)
