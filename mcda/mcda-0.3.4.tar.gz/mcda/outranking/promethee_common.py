"""This module implements the common promethee methods.

Implementation and naming conventions are taken from
:cite:p:`vincke1998promethee1`.
"""

import copy
from enum import Enum
from math import exp
from typing import List

from mcda.core.aliases import (  # Cannot do from ..core.aliases
    NumericFunction,
    NumericPerformanceTable,
    NumericValue,
)

from ..core.scales import PreferenceDirection, QuantitativeScale


class PreferenceFunction(Enum):
    """Enumeration of the preference functions."""

    USUAL = 1
    U_SHAPE = 2
    V_SHAPE = 3
    LEVEL = 4
    LINEAR = 5
    GAUSSIAN = 6


def usual_function() -> NumericFunction:
    """Implements the usual function.

    :return: the result of the lambda variable on the usual function"""
    return lambda x: 1 if x > 0 else 0


def u_shape_function(q: NumericValue) -> NumericFunction:
    """Implements the u-shape function.

    :param q: the indifference threshold
    :return: the result of the lambda variable on the u-shape function"""
    return lambda x: 1 if x > q else 0


def v_shape_function(p: NumericValue) -> NumericFunction:
    """Implements the v-shape function.

    :param p: the preference threshold
    :return: the result of the lambda variable on the v-shape function"""
    return lambda x: 1 if x > p else abs(x) / p


def level_function(p: NumericValue, q: NumericValue) -> NumericFunction:
    """Implements the level function.

    :param p: the preference threshold
    :param q: the indifference threshold
    :return: the result of the lambda variable on the level function"""
    return lambda x: 1 if x > p else 1 / 2 if q < x else 0


def linear_function(p: NumericValue, q: NumericValue) -> NumericFunction:
    """Implements the linear function.

    :param p: the preference threshold
    :param q: the indifference threshold
    :return: the result of the lambda variable on the linear function"""
    return lambda x: 1 if x > p else (abs(x) - q) / (p - q) if q < x else 0


def gaussian_function(s: NumericValue) -> NumericFunction:
    """Implements the gaussian function.

    :param s: the standard deviation
    :return: the result of the lambda variable on the gaussian function"""
    return lambda x: 1 - exp(-(x ** 2) / (2 * s ** 2))


def preference_degree_calculation(
    pref_func: PreferenceFunction,
    p: NumericValue,
    q: NumericValue,
    s: NumericValue,
    ga: NumericValue,
    gb: NumericValue,
) -> NumericValue:
    """Compute the preference degree for two criteria of the alternatives.

    :param pref_func: the preference function for the criteria
    :param p: the preference threshold for the criteria
    :param q: the indifference threshold for the criteria
    :param s: the standard deviation for the criteria
    :param ga: value of the criteria for the first alternative
    :param gb: value of the criteria for the second alternative
    :return: the preference degree of the alternatives with the pref_func"""

    if ga - gb <= 0:
        return 0
    if pref_func is PreferenceFunction.USUAL:
        my_func = usual_function()
    elif pref_func is PreferenceFunction.U_SHAPE:
        my_func = u_shape_function(q)
    elif pref_func is PreferenceFunction.V_SHAPE:
        my_func = v_shape_function(p)
    elif pref_func is PreferenceFunction.LEVEL:
        if q > p:
            raise ValueError(
                "incorrect threshold : q "
                + str(q)
                + " greater than p "
                + str(p)
            )
        my_func = level_function(p, q)
    elif pref_func is PreferenceFunction.LINEAR:
        if q > p:
            raise ValueError(
                "incorrect threshold : q "
                + str(q)
                + " greater than p "
                + str(p)
            )
        my_func = linear_function(p, q)
    elif pref_func is PreferenceFunction.GAUSSIAN:
        my_func = gaussian_function(s)
    else:
        raise ValueError(
            "pref_func "
            + str(pref_func)
            + " is not known. \n See PreferenceFunction Enum"
        )
    pref_degree = my_func(ga - gb)
    return pref_degree


def multicriteria_preference_degree_calculation(
    action1: List[NumericValue],
    action2: List[NumericValue],
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    w_list: List[NumericValue],
) -> NumericValue:
    """Compute the multicriteria preference degree of two alternatives.

    :param action1: list of criteria values for one alternative
    :param action2: list of criteria values for the second alternative
    :param preference_func_list: list of preference function for each criteria
    :param p_list: list of preference threshold for each criteria
    :param q_list: list of indifference threshold for each criteria
    :param s_list: list of standard deviation for each criteria
    :param w_list: list of weight of each criteria
    :return: the multicriteria preference degree for the alternatives"""

    multi_pref_degree = 0.0
    for f, p, q, s, a, b, w in zip(
        preference_func_list, p_list, q_list, s_list, action1, action2, w_list
    ):
        multi_pref_degree += w * preference_degree_calculation(
            f, p, q, s, a, b
        )
    multi_pref_degree /= sum(w_list)
    return multi_pref_degree


def positive_preference_flow_calculation(
    action1: List[NumericValue],
    other_actions: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    w_list: List[NumericValue],
) -> NumericValue:
    """Compute the positive preference flow.

    :param action1: list of criteria values for one alternative
    :param other_actions: list of criteria values for the other alternatives
    :param preference_func_list: list of preference function for each criteria
    :param p_list: list of preference threshold for each criteria
    :param q_list: list of indifference threshold for each criteria
    :param s_list: list of standard deviation for each criteria
    :param w_list: list of weight of each criteria
    :return: the positive preference flow calculation for the action1"""

    positive_pref_flow = 0.0
    for other_action in other_actions:
        positive_pref_flow += multicriteria_preference_degree_calculation(
            action1,
            other_action,
            preference_func_list,
            p_list,
            q_list,
            s_list,
            w_list,
        )
    return positive_pref_flow


def negative_preference_flow_calculation(
    action1: List[NumericValue],
    other_actions: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    w_list: List[NumericValue],
) -> NumericValue:
    """Compute the negative preference flow.

    :param action1: list of criteria values for one alternative
    :param other_actions: list of criteria values for the other alternatives
    :param preference_func_list: list of preference function for each criteria
    :param p_list: list of preference threshold for each criteria
    :param q_list: list of indifference threshold for each criteria
    :param s_list: list of standard deviation for each criteria
    :param w_list: list of weight of each criteria
    :return: the negative preference flow calculation for the action1"""

    negative_pref_flow = 0.0
    for other_action in other_actions:
        negative_pref_flow += multicriteria_preference_degree_calculation(
            other_action,
            action1,
            preference_func_list,
            p_list,
            q_list,
            s_list,
            w_list,
        )
    return negative_pref_flow


def outranking_flow_calculation(
    actions: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    w_list: List[NumericValue],
) -> NumericPerformanceTable:
    """Compute the outranking flow.

    :param actions: list of criteria values for each alternative
    :param preference_func_list: list of preference function for each criteria
    :param p_list: list of preference threshold for each criteria
    :param q_list: list of indifference threshold for each criteria
    :param s_list: list of standard deviation for each criteria
    :param w_list: list of weight of each criteria
    :return: the outranking flow list of each action in actions"""

    outranking_flow: NumericPerformanceTable = []
    for i in range(len(actions)):
        other_actions = actions.copy()
        del other_actions[i]
        pos_pref = positive_preference_flow_calculation(
            actions[i],
            other_actions,
            preference_func_list,
            p_list,
            q_list,
            s_list,
            w_list,
        )
        neg_pref = negative_preference_flow_calculation(
            actions[i],
            other_actions,
            preference_func_list,
            p_list,
            q_list,
            s_list,
            w_list,
        )

        outranking_flow.append([pos_pref, neg_pref])
    return outranking_flow


def scale_performance_table(
    actions: NumericPerformanceTable, scales: List[QuantitativeScale]
) -> NumericPerformanceTable:
    """Rearrange the performance table if there are criterias to minimize

    :param actions: list of criteria value for each alternative
    :param scales: the scale for each criteria
    :return: the scaled performance table"""

    scaled_actions: NumericPerformanceTable = copy.deepcopy(actions)

    for i in range(len(scales)):
        if scales[i].preference_direction == PreferenceDirection.MIN:
            for j in range(len(scaled_actions)):
                scaled_actions[j][i] = -scaled_actions[j][i]

    return scaled_actions
