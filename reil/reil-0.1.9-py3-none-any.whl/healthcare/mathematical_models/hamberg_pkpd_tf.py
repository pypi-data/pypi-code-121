# -*- coding: utf-8 -*-
'''
HambergPKPD class
=================

A warfarin PK/PD model proposed by Hamberg et al. (2007).
DOI: 10.1038/sj.clpt.6100084
'''
from typing import Any, Dict, Final, List, NamedTuple, Optional, Union
import numpy as np

import tensorflow as tf
from reil.datatypes.feature import (FeatureGenerator, FeatureGeneratorSet,
                                    FeatureSet)
from reil.healthcare.mathematical_models.health_math_model import \
    HealthMathModel
from reil.utils.functions import random_lognormal_truncated


class DoseEffect(NamedTuple):
    dose: tf.Tensor
    Cs: tf.Tensor


@tf.function(
    input_signature=(
        tf.TensorSpec(shape=[], dtype=tf.float32, name='CL_S_cyp_1_1'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='CL_s_genotype'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='CL_s_age'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='age'),
    )
)
def CL_s_fn(
        CL_S_cyp_1_1: tf.Tensor, CL_s_genotype: tf.Tensor,
        CL_s_age: tf.Tensor, age: tf.Tensor):
    print('trace CL_s_fn')
    return tf.multiply(
        CL_S_cyp_1_1,
        (1.0 - (CL_s_age * tf.subtract(age, 71.0))) * tf.subtract(
            1.0, CL_s_genotype),
        name='CL_s')


@tf.function(
    input_signature=(
        tf.TensorSpec(shape=[], dtype=tf.float32, name='Q'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='CL_s'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='k_aS'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='V1'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='V2'),
    )
)
def two_compartment(
        Q: tf.Tensor, CL_s: tf.Tensor, k_aS: tf.Tensor,
        V1: tf.Tensor, V2: tf.Tensor):
    print('trace two_compartment')
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
    F = tf.constant(0.9, dtype=tf.float32, name='F')

    # Central to peripheral distribution constant
    k12 = tf.divide(Q, V1, name='k12')
    # Peripheral to central distribution constant
    k21 = tf.divide(Q, V2, name='k21')
    # Elimination rate constant
    k10 = tf.divide(CL_s, V1, name='k10')

    b = tf.add_n([k10, k21, k12], name='b')
    c = tf.multiply(k10, k21, name='c')

    # Alpha: distribution phase slope (-alpha)
    alpha = tf.divide(
        b + tf.sqrt(tf.square(b) - 4.0 * c), 2.0, name='alpha')
    # Beta: elimination phase slope (-beta)
    beta = tf.divide(
        b - tf.sqrt(tf.square(b) - 4.0 * c), 2.0, name='beta')

    # Note: Here we halved the value for KaF_2V1, because half of the
    # warfarin is S, and only S affects the INR.
    kaF_2V1 = k_aS * F / 2.0 / V1

    # $C_s$ = c_{\k_1}\exp{-k_1 t}
    #       + c_{\alpha}\exp{-\alpha t}
    #       + c_{\beta}\exp{-\beta t}
    coef_alpha = tf.multiply(
        (k21 - alpha) / ((k_aS - alpha)*(beta - alpha)), kaF_2V1,
        name='coef_alpha')
    coef_beta = tf.multiply(
        (k21 - beta) / ((k_aS - beta)*(alpha - beta)), kaF_2V1,
        name='coef_beta')
    coef_k_a = tf.multiply(
        (k21 - k_aS) / ((k_aS - alpha)*(k_aS - beta)), kaF_2V1,
        name='coef_k_a')

    # ---- End of the implementation of the two compartment model -------
    return alpha, beta, coef_alpha, coef_beta, coef_k_a


@tf.function(
    input_signature=(
        tf.TensorSpec(shape=[3], dtype=tf.float32, name='coefs'),
        tf.TensorSpec(shape=[3], dtype=tf.float32, name='exps'),
        tf.TensorSpec(shape=[None], dtype=tf.int32, name='times'),
        tf.TensorSpec(shape=[None], dtype=tf.float32, name='doses'),
        tf.TensorSpec(shape=[], dtype=tf.int32, name='pad')))
def concentration(
        coefs: tf.Tensor, exps: tf.Tensor,
        times: tf.Tensor, doses: tf.Tensor = tf.constant([1.0]),
        pad: tf.Tensor = tf.constant(0)):
    print('trace concentration')
    exponents = tf.matmul(
        -tf.expand_dims(exps, axis=1),
        tf.expand_dims(tf.cast(times, dtype=tf.float32), axis=0))
    base_cs = tf.matmul(tf.expand_dims(coefs, axis=0), tf.exp(exponents))
    cs = tf.matmul(tf.expand_dims(doses, axis=1), base_cs)
    padded_cs = tf.pad(cs, [[0, 0], [pad, 0]], 'constant')

    return padded_cs[:, :tf.shape(times)[0]]


@tf.function(
    input_signature=(
        tf.TensorSpec(shape=[3], dtype=tf.float32, name='coefs'),
        tf.TensorSpec(shape=[3], dtype=tf.float32, name='exps'),
        tf.TensorSpec(shape=[], dtype=tf.int32, name='max_time')))
def base_concentration(
        coefs: tf.Tensor, exps: tf.Tensor, max_time: tf.Tensor) -> tf.Tensor:
    print('trace base_concentration')
    times = tf.range(max_time)
    exponents = tf.matmul(
        -tf.expand_dims(exps, axis=1),
        tf.expand_dims(tf.cast(times, dtype=tf.float32), axis=0))
    base_cs = tf.matmul(tf.expand_dims(coefs, axis=0), tf.exp(exponents))
    base_cs = tf.clip_by_value(
        base_cs, clip_value_min=0.0, clip_value_max=100.0)

    return tf.squeeze(base_cs)

@tf.function(
    input_signature=(
        tf.TensorSpec(shape=[None], dtype=tf.float32, name='cs'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='dose'),
        tf.TensorSpec(shape=[], dtype=tf.int32, name='pad')))
def pad_and_dose(
        cs: tf.Tensor, dose: tf.Tensor = tf.constant(1.0),
        pad: tf.Tensor = tf.constant(0)):
    print('trace pad_and_dose')
    cs = tf.multiply(cs, dose)
    padded_cs = tf.pad(cs, [[pad, 0]], 'constant')

    return padded_cs[:tf.shape(cs)[0]]

@tf.function(
    input_signature=(
        tf.TensorSpec(shape=[None], dtype=tf.int32, name='stop_points'),
        tf.TensorSpec(shape=[None], dtype=tf.float32, name='cs'),
        tf.TensorSpec(shape=[None], dtype=tf.float32, name='err_list'),
        tf.TensorSpec(shape=[None], dtype=tf.float32, name='err_INR_list'),
        tf.TensorSpec(shape=[], dtype=tf.float32, name='EC_50_gamma'),
        tf.TensorSpec(shape=[9], dtype=tf.float32, name='A'),
        tf.TensorSpec(shape=[8], dtype=tf.float32, name='ktr'),
    )
)
# TODO: this should return A as well!
def _INR(
        stop_points: tf.Tensor, cs: tf.Tensor,
        err_list: tf.Tensor, err_INR_list: tf.Tensor,
        EC_50_gamma: tf.Tensor, A: tf.Tensor, ktr: tf.Tensor):
    print('trace _INR')
    start_day = stop_points[0]
    start_point = tf.cast(start_day * HambergPKPD._per_day, tf.int32)
    all_points = tf.range(
        start_point,
        stop_points[-1] * HambergPKPD._per_day, dtype=tf.int32)

    Cs_gamma = tf.pow(
        tf.gather(cs, all_points) * tf.gather(err_list, all_points),
        HambergPKPD._gamma)
    inflow = 1.0 - tf.divide(
        HambergPKPD._E_max * Cs_gamma, EC_50_gamma + Cs_gamma,
        name='inflow')

    starts = tf.data.Dataset.from_tensor_slices(stop_points[:-1])
    ends = tf.data.Dataset.from_tensor_slices(stop_points[1:])

    result = tf.TensorArray(
        dtype=tf.float32, size=tf.shape(stop_points)[0])
    for d1, d2 in tf.data.Dataset.zip((starts, ends)):
        steps = tf.range(
            d1 * HambergPKPD._per_day, d2 * HambergPKPD._per_day,
            dtype=tf.int32)
        for dt in steps:
            # inflow = self._inflow(
            #     self._total_cs,
            #     self._err_ss_list if dt>0 else self._err_ss_list,
            #     self._EC_50_gamma, tf.constant(dt))
            f = [inflow[dt - start_point]] * 2
            A = tf.tensor_scatter_nd_update(A, [[0], [7]], f)
            left = A[:-1]
            right = A[1:]
            A = tf.pad(right + ktr * (left - right), [[1, 0]])

        result = result.write(d2 - start_day, tf.squeeze(
            tf.multiply(
                HambergPKPD._baseINR + HambergPKPD._INR_max * tf.pow(
                    1.0 - A[6]*A[8], HambergPKPD._lambda),
                err_INR_list[d2], name='INR')))

    return result.stack()


class HambergPKPD(HealthMathModel):
    '''
    Hamberg PK/PD model for warfarin.
    '''
    _per_day: int = 24

    # Hamberg et al. (2007) - Table 2
    # CL_s: Apparent oral clearance
    # (l/h) CL_s for *1/*1 of a typical 71-yr patient
    _CL_s_1_1: Final = tf.constant(0.314, dtype=tf.float32, name='CL_s_1_1')
    _CL_s_genotypes: Final = {  # Effect of genotypes diff. from *1/*1 on CL_s
        '*1/*1': tf.constant(0.0, dtype=tf.float32, name='d_CL_s_1_1'),
        '*1/*2': tf.constant(0.315, dtype=tf.float32, name='d_CL_s_1_2'),
        '*1/*3': tf.constant(0.453, dtype=tf.float32, name='d_CL_s_1_3'),
        '*2/*2': tf.constant(0.722, dtype=tf.float32, name='d_CL_s_2_2'),
        '*2/*3': tf.constant(0.690, dtype=tf.float32, name='d_CL_s_2_3'),
        '*3/*3': tf.constant(0.852, dtype=tf.float32, name='d_CL_s_3_3')}
    # Effect of age on CL_s centered around 71 years
    _CL_s_age: Final = tf.constant(0.0091, dtype=tf.float32, name='CL_s_age')
    # (l) Apparent central volume of distribution
    _V1: Final = tf.constant(13.8, dtype=tf.float32, name='V1')
    # (1/hr) Absorption rate constant
    _k_aS: Final = tf.constant(2.0, dtype=tf.float32, name='k_aS')
    # (l/h) Apparent intercompartmental clearance
    _Q: Final = tf.constant(0.131, dtype=tf.float32, name='Q')
    # (l) Apparent peripheral volume of distribution
    _V2: Final = tf.constant(6.59, dtype=tf.float32, name='V2')

    # Interindividual variability for CL_s
    _omega_CL_s: Final = tf.constant(0.310, dtype=tf.float32, name='omega_CL_s')
    # Interindividual variability for V1
    _omega_V1: Final = tf.constant(0.262, dtype=tf.float32, name='omega_V1')
    # Interindividual variability for V2
    _omega_V2: Final = tf.constant(0.991, dtype=tf.float32, name='omega_V2')

    # Residual error after single dose
    _sigma_s: Final = tf.constant(0.0908, dtype=tf.float32, name='sigma_s')
    # Residual error after steady-state dose
    _sigma_ss: Final = tf.constant(0.301, dtype=tf.float32, name='sigma_ss')

    # Hamberg et al. (2007) - Table 4
    _E_max: Final = tf.constant(1.0, dtype=tf.float32, name='E_max')
    _gamma: Final = tf.constant(0.424, dtype=tf.float32, name='gamma')
    # (mg/l) EC_50 for VKORC1 genotype G/G
    _EC_50_GG: Final = tf.constant(4.61, dtype=tf.float32, name='EC_50_GG')
    # (mg/l) EC_50 for VKORC1 genotype G/A
    _EC_50_GA: Final = tf.constant(3.02, dtype=tf.float32, name='EC_50_GA')
    # (mg/l) EC_50 for VKORC1 genotype A/A
    _EC_50_AA: Final = tf.constant(2.20, dtype=tf.float32, name='EC_50_AA')
    # (h) Mean Transit Time
    _MTT_1: Final = tf.constant(11.6, dtype=tf.float32, name='MTT_1')
    # (h) Mean Transit Time
    _MTT_2: Final = tf.constant(120.0, dtype=tf.float32, name='MTT_2')
    _lambda: Final = tf.constant(3.61, dtype=tf.float32, name='lambda')

    # Interindividual variability for MTT_1
    _omega_MTT_1: Final = tf.constant(
        0.141, dtype=tf.float32, name='omega_MTT_1')
    # Interindividual variability for MTT_2
    _omega_MTT_2: Final = tf.constant(
        1.020, dtype=tf.float32, name='omega_MTT_2')
    # Interindividual variability for EC_50
    _omega_EC_50: Final = tf.constant(
        0.409, dtype=tf.float32, name='omega_EC_50')
    # Residual error for INR
    _sigma_INR: Final = tf.constant(
        0.0325, dtype=tf.float32, name='sigma_INR')

    # Hamberg et al. (2007) - Misc.
    _INR_max: Final = 20.0  # page 538

    # Note: In Hamberg et al. (2007), BASE_i is the measured baseline INR
    # for patients, but Ravvaz fixed it to 1.
    _baseINR = tf.ones(  # Ravvaz source code
        shape=1, dtype=tf.float32, name='baseINR')

    _parameter_generators = FeatureGeneratorSet((
        FeatureGenerator.continuous(
            name='MTT_1',  # (hours) Hamberg PK/PD
            mean=tf.math.log(_MTT_1),
            stdev=tf.sqrt(_omega_MTT_1),
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='MTT_2',  # (hours) Hamberg PK/PD
            # Hamberg et al. (2007) - Table 4
            mean=tf.math.log(_MTT_2),
            stdev=tf.sqrt(_omega_MTT_2),
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='CL_S_cyp_1_1',  # (l/h) Hamberg PK/PD
            mean=tf.math.log(_CL_s_1_1),
            stdev=tf.sqrt(_omega_CL_s),
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='V1',  # (L) Volume in central compartment
            mean=tf.math.log(_V1),
            stdev=tf.sqrt(_omega_V1),
            generator=random_lognormal_truncated,
            randomized=True),
        FeatureGenerator.continuous(
            name='V2',  # (L) volume in peripheral compartment
            mean=tf.math.log(_V2),
            stdev=tf.sqrt(_omega_V2),
            generator=random_lognormal_truncated,
            randomized=True),
    ))

    # pre-computing to gain some speed boost!
    __log_EC_50_GG: Final[tf.Tensor] = tf.math.log(_EC_50_GG)  # type: ignore
    __log_EC_50_GA: Final[tf.Tensor] = tf.math.log(_EC_50_GA)  # type: ignore
    __log_EC_50_AA: Final[tf.Tensor] = tf.math.log(_EC_50_AA)  # type: ignore
    __sqrt_omega_EC_50: Final[tf.Tensor] = tf.sqrt(_omega_EC_50)

    def __init__(  # done!
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
        self._cache_size = cache_size
        self._current_cache_size = 0
        self._last_computed_day: int = 0
        self._cached_cs: tf.Tensor

    @classmethod
    def generate(
            cls,
            input_features: Optional[FeatureSet] = None,
            **kwargs: Any) -> FeatureSet:

        feature_set = super(HambergPKPD, cls).generate(
            input_features, **kwargs)

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
                randomized=True)()

        return feature_set

    def setup(
            self, arguments: FeatureSet,
            random_seed: Optional[int] = None) -> None:
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

        args = arguments.value

        age = tf.constant(
            args['age'], dtype=tf.float32, name='age')
        MTT_1 = float(args['MTT_1'])  # type: ignore
        MTT_2 = float(args['MTT_2'])  # type: ignore
        V1 = tf.constant(
            args['V1'], dtype=tf.float32, name='V1')
        V2 = tf.constant(
            args['V2'], dtype=tf.float32, name='V2')
        EC_50 = tf.constant(
            args['EC_50'], dtype=tf.float32, name='EC_50')
        CL_S_cyp_1_1 = tf.constant(
            args['CL_S_cyp_1_1'], dtype=tf.float32, name='CL_S_cyp_1_1')

        CYP2C9 = str(args['CYP2C9'])
        if CYP2C9 not in self._CL_s_genotypes:
            raise ValueError('The CYP2C9 genotype not recognized!')

        # Note:
        # Hamberg et al. (2007) says "CLS was reduced with increasing age,
        # decreasing by approximately 9% per decade". However, it does not say
        # whether it applies to younger than 71 or not. Ravvaz assumed that it
        # does not, but Figure 3 in Hamberg et al. (2007) shows a 50-year-old
        # patient has a lower INR than a 70-year-old. So, it applies!

        CL_s = CL_s_fn(
            CL_S_cyp_1_1, self._CL_s_genotypes[CYP2C9], self._CL_s_age, age)

        alpha, beta, coef_alpha, coef_beta, coef_k_a = two_compartment(
            self._Q, CL_s, self._k_aS, V1, V2)

        self._coefs = tf.concat(
            [coef_alpha, coef_beta, coef_k_a], axis=0, name='coefs')
        self._exps = tf.concat(
            [alpha, beta, self._k_aS], axis=0, name='exps')

        # Note: According to Hamberg et al. (2007) pp. 538, $ktr_1=1/MTT_1$
        # However, Ravvaz set it to $6/MTT_1$. It must be because we have
        # 6 compartment amounts, and total $MTT_1$ for the whole chain is
        # 11.6 h (Figure 2), so each should take $\frac{1}{6} MTT_1$
        ktr1 = 6.0/MTT_1  # (1/hours)
        ktr2 = 1.0/MTT_2  # (1/hours)
        self._ktr = tf.constant([ktr1] * 6 + [0.0, ktr2], dtype=tf.float32)
        self._EC_50_gamma = tf.pow(EC_50, self._gamma)

        self._A = tf.constant([0.0] + [1.0] * 8, dtype=tf.float32)

        self._last_computed_day = 0

        self._dose_records: Dict[int, DoseEffect] = {}
        self._computed_INRs: Dict[int, tf.Tensor] = {}  # daily

        # define random generators
        detailed_cache_size = self._cache_size * self._per_day
        if self._randomized:
            if random_seed is None:
                self._random_generator = tf.random.get_global_generator()
            else:
                self._random_generator = tf.random.Generator.from_seed(
                    random_seed)

            gen_err, gen_exp_e_INR = self._random_generator.split(count=2)
            def _gen_err():
                return tf.exp(
                    gen_err.normal([detailed_cache_size], 0.0, self._sigma_ss))
            def _gen_exp_e_INR():
                return tf.exp(
                    gen_exp_e_INR.normal(
                        [self._cache_size], 0.0, self._sigma_INR))
        else:
            def _gen_err():
                return tf.ones(shape=detailed_cache_size)

            def _gen_exp_e_INR():
                return tf.ones(shape=self._cache_size)

        self._gen_err = _gen_err
        self._gen_exp_e_INR = _gen_exp_e_INR

        # setup all caches
        self._current_cache_size = self._cache_size
        self._err_list = self._gen_err()  # hourly
        # In our work, only the first dose can be considered as
        # non-steady state. So, we change the first error value accordingly.
        if self._randomized:
            self._err_list = tf.tensor_scatter_nd_update(
                self._err_list, [[0]],
                tf.exp(gen_err.normal([1], 0.0, self._sigma_s))  # type: ignore
            )

        self._exp_e_INR_list = self._gen_exp_e_INR()  # daily

        self._cached_cs = base_concentration(
            coefs=self._coefs, exps=self._exps,
            max_time=tf.constant(detailed_cache_size))
        self._total_cs = tf.Variable(
            [0.0] * detailed_cache_size, name='total_cs',
            dtype=tf.float32, trainable=False)

    def _expand_caches(self, segment_count: int = 1):
        per_day = self._per_day
        self._current_cache_size += self._cache_size * segment_count

        self._err_list = tf.concat(
            [self._err_list, *(self._gen_err() for _ in range(segment_count))],
            axis=0)
        self._exp_e_INR_list = tf.concat(
            [
                self._exp_e_INR_list,
                *(self._gen_exp_e_INR() for _ in range(segment_count))],
            axis=0)

        self._cached_cs = base_concentration(
            coefs=self._coefs, exps=self._exps,
            max_time=tf.constant(self._current_cache_size * per_day))

        self._total_cs = tf.Variable(
            [0.0] * self._current_cache_size * per_day,
            name='total_cs', dtype=tf.float32, trainable=False)

        for day, (dose, _) in self._dose_records.items():
            cs = pad_and_dose(
                    cs=self._cached_cs, dose=dose,
                    pad=tf.constant(day * per_day))
            self._dose_records[day] = DoseEffect(dose, cs)
            self._total_cs.assign_add(cs)

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
        return {
            t: info.dose.numpy()[0]  # type: ignore
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

        if max(dose) >= self._current_cache_size:
            segment_count = (
                max(dose) - self._current_cache_size
            ) // self._cache_size + 1
            self._expand_caches(segment_count=segment_count)

        for day, _dose in dose.items():
            if _dose != 0.0:
                if day in self._dose_records:
                    prev_dose = \
                        self._dose_records[day][0].numpy[0]  # type: ignore
                else:
                    prev_dose = 0.0

                new_dose = prev_dose + _dose
                if new_dose < 0.0:
                    raise ValueError(
                        'Total dose for a day cannot be negative.')

                new_dose = tf.constant(new_dose, dtype=tf.float32)
                cs = pad_and_dose(
                        cs=self._cached_cs, dose=new_dose,
                        pad=tf.constant(day * self._per_day))
                self._dose_records[day] = DoseEffect(new_dose, cs)
                self._total_cs.assign_add(cs)

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
            self._last_computed_day = 0
            self._computed_INRs = {}
            not_computed_days = days

        if self._last_computed_day == 0:
            self._A = tf.constant(
                [0.0] + [1.0] * 8, dtype=tf.float32, name='A')

        stop_points = [self._last_computed_day] + sorted(
            list(not_computed_days))
        self._last_computed_day = stop_points[-1]

        INRs = _INR(
            tf.constant(stop_points, dtype=tf.int32), self._total_cs,
            self._err_list, self._exp_e_INR_list,
            self._EC_50_gamma, self._A, self._ktr)

        for day, inr in zip(set(stop_points), INRs.numpy()):
            self._computed_INRs[day] = inr

        return [self._computed_INRs[i] for i in days]

    # @staticmethod
    # @tf.function(
    #     input_signature=(
    #         tf.TensorSpec(shape=[None], dtype=tf.float32, name='Cs'),
    #         tf.TensorSpec(shape=[None], dtype=tf.float32, name='error'),
    #         tf.TensorSpec(shape=[], dtype=tf.float32, name='EC_50_gamma'),
    #         tf.TensorSpec(shape=[None], dtype=tf.int32, name='t')))
    # def _inflow(
    #         Cs: tf.Tensor, err_list: tf.Tensor,
    #         EC_50_gamma: tf.Tensor,
    #         t: tf.Tensor) -> tf.Tensor:
    #     '''
    #     Compute the warfarin concentration that enters the two compartments
    #     in the PK/PD model.

    #     Arguments
    #     ---------
    #     t:
    #         The time for which the input is requested.
    #         t = Hours * _per_hour + delta_t

    #     Returns
    #     -------
    #     :
    #         The input value.

    #     Notes
    #     -----
    #     To speed up the process, total concentration is being cached for a
    #     number of days. For days beyond this range, concentration values are
    #     computed and used on each call.
    #     '''
    #     Cs_gamma = tf.pow(
    #         tf.gather(Cs, t) * tf.gather(err_list, t), HambergPKPD._gamma)
    #     inflow = 1.0 - tf.divide(
    #         HambergPKPD._E_max * Cs_gamma, EC_50_gamma + Cs_gamma,
    #         name='inflow')

    #     return inflow

    # @staticmethod
    # @tf.function(
    #     input_signature=(
    #         tf.TensorSpec(shape=[9], dtype=tf.float32, name='A'),
    #         tf.TensorSpec(shape=[], dtype=tf.float32, name='error')
    #     )
    # )
    # def _INR(A: tf.Tensor, error: tf.Tensor) -> tf.Tensor:
    #     '''
    #     Compute the INR on day `d`.

    #     Arguments
    #     ---------

    #     d:
    #         The day for which the input is requested.

    #     Returns
    #     -------
    #     :
    #         The INR value.

    #     Notes
    #     -----
    #     To speed up the process, total concentration is being cached for a
    #     number of days. For days beyond this range, concentration values are
    #     computed and used on each call.
    #     '''

    #     # Note: we defined `A` in such a way to compute changes in `A`s
    #     # easier. In our implementation, `A8` is the `A7` in Hamberg et al.
    #     return tf.squeeze(tf.multiply(
    #         HambergPKPD._baseINR + HambergPKPD._INR_max * tf.pow(
    #             1.0 - A[6]*A[8], HambergPKPD._lambda),  # type: ignore
    #         error, name='INR'))

