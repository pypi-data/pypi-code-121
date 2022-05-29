"""This module implements the promethee 2 algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998promethee1`.
"""


from typing import List

from mcda.core.aliases import (  # Cannot do from ..core.aliases
    NumericPerformanceTable,
    NumericValue,
)
from mcda.outranking.promethee_common import (
    PreferenceFunction,
    outranking_flow_calculation,
    scale_performance_table,
)

from ..core.scales import QuantitativeScale


def total_order(
    actions: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    w_list: List[NumericValue],
) -> List[List[NumericValue]]:
    """Compute the total order list.

    :param actions: list of criteria value for each alternative
    :param preference_func_list: list of preference function for each criteria
    :param p_list: list of preference threshold for each criteria
    :param q_list: list of indifference threshold for each criteria
    :param s_list: list of standard deviation for each criteria
    :param w_list: list of weight of each criteria
    :return: the outranking total order of the performance table"""

    outranking_flow = outranking_flow_calculation(
        actions, preference_func_list, p_list, q_list, s_list, w_list
    )

    difference_flow: List[List[NumericValue]] = [[0, 0]] * len(outranking_flow)

    for i in range(len(outranking_flow)):
        difference_flow[i] = [i, outranking_flow[i][0] - outranking_flow[i][1]]

    difference_flow = sorted(difference_flow, key=lambda x: x[1])
    difference_flow.reverse()

    return difference_flow


def promethee2(
    actions: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    scales: List[QuantitativeScale],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    w_list: List[NumericValue],
) -> List[List[NumericValue]]:
    """Compute the outranking algorithm promethee2 with the total order.

    :param actions: list of criteria value for each alternative
    :param preference_func_list: list of preference function for each criteria
    :param scales: the scale for each criteria
    :param p_list: list of preference threshold for each criteria
    :param q_list: list of indifference threshold for each criteria
    :param s_list: list of standard deviation for each criteria
    :param w_list: list of weight of each criteria
    :return: the outranking total order of the performance table"""

    scaled_performance_table = scale_performance_table(actions, scales)

    return total_order(
        scaled_performance_table,
        preference_func_list,
        p_list,
        q_list,
        s_list,
        w_list,
    )
