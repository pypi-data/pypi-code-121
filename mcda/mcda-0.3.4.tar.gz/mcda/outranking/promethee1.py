"""This module implements the promethee 1 algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998promethee1`.
"""

from typing import List

from mcda.core.aliases import (  # Cannot do from ..core.aliases
    NumericPerformanceTable,
    NumericValue,
)
from mcda.core.sorting import Relation, RelationType
from mcda.outranking.promethee_common import (
    PreferenceFunction,
    outranking_flow_calculation,
    scale_performance_table,
)

from ..core.scales import QuantitativeScale


def partial_order(
    actions: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    w_list: List[NumericValue],
) -> List[Relation]:
    """Compute the partial order list.

    :param actions: list of criteria value for each alternative
    :param preference_func_list: list of preference function for each criteria
    :param p_list: list of preference threshold for each criteria
    :param q_list: list of indifference threshold for each criteria
    :param s_list: list of standard deviation for each criteria
    :param w_list: list of weight of each criteria
    :return: relationslist of each alternative with all others in actions"""

    outranking_flow = outranking_flow_calculation(
        actions, preference_func_list, p_list, q_list, s_list, w_list
    )

    relations: List[Relation] = list()

    for i in range(len(outranking_flow)):
        for j in range(len(outranking_flow)):
            if i != j:
                comparison = flow_intersection(
                    outranking_flow[i], outranking_flow[j]
                )
                relations.append((i, j, comparison))

    return relations


def flow_intersection(
    outranking_flow_a: List[NumericValue],
    outranking_flow_b: List[NumericValue],
) -> RelationType:
    """Compute the positive and negative flow intersection.

    :param outranking_flow_a: the outranking flow of one aternative
    :param outranking_flow_b: the outranking flow of a second aternative
    :return: the comparison of the two alternatives in a relationType"""

    alternative_comparison: RelationType
    if (
        (
            outranking_flow_a[0] > outranking_flow_b[0]
            and outranking_flow_a[1] < outranking_flow_b[1]
        )
        or (
            outranking_flow_a[0] == outranking_flow_b[0]
            and outranking_flow_a[1] < outranking_flow_b[1]
        )
        or (
            outranking_flow_a[0] > outranking_flow_b[0]
            and outranking_flow_a[1] == outranking_flow_b[1]
        )
    ):
        alternative_comparison = RelationType.PREFERENCE
    elif (
        outranking_flow_a[0] == outranking_flow_b[0]
        and outranking_flow_a[1] == outranking_flow_b[1]
    ):
        alternative_comparison = RelationType.INDIFFERENCE
    else:
        alternative_comparison = RelationType.INCOMPARABLE

    return alternative_comparison


def promethee1(
    actions: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    scales: List[QuantitativeScale],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    w_list: List[NumericValue],
) -> List[Relation]:
    """Compute the outranking algorithm promethee1 with the partial order.

    :param actions: list of criteria value for each alternative
    :param preference_func_list: list of preference function for each criteria
    :param scales: the scale for each criteria
    :param p_list: list of preference threshold for each criteria
    :param q_list: list of indifference threshold for each criteria
    :param s_list: list of standard deviation for each criteria
    :param w_list: list of weight of each criteria
    :return: the outranking partial order of the performance table"""

    scaled_performance_table = scale_performance_table(actions, scales)
    return partial_order(
        scaled_performance_table,
        preference_func_list,
        p_list,
        q_list,
        s_list,
        w_list,
    )
