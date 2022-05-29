"""This module implements the electre-tri B algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electreTRI`.
"""

from typing import Dict, List, Tuple

from mcda.core.sorting import RelationType

from ..core.aliases import NumericPerformanceTable, NumericValue
from ..core.scales import QuantitativeScale
from .electre3 import concordance, credibility, discordance


def outrank(
    alt_performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    index_a: int,
    index_b: int,
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    lambda_: NumericValue,
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
) -> Tuple[NumericValue, NumericValue, RelationType]:
    """Compute outranking test over 2 actions.

    :param alt_performance_table: Concatenation of performance table / profiles
    :param criteria_weights:
    :param scales: Scaling List
    :param index_a: index of action a in preference matrix
    :param index_b: index of a class
    :param P: preference thresholds
    :param Q: indifference  thresholds
    :param V: veto thresholds
    :param lambda_: cut level
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :return: boolean"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    credibility_mat = credibility_function(
        alt_performance_table,
        criteria_weights,
        scales,
        P,
        Q,
        V,
        concordance_function,
        discordance_function,
    )
    aSb = credibility_mat[index_a][index_b]
    bSa = credibility_mat[index_b][index_a]
    if aSb >= lambda_ and bSa >= lambda_:
        return (index_a, index_b, RelationType.INDIFFERENCE)
    elif aSb >= lambda_ > bSa:
        return (index_a, index_b, RelationType.PREFERENCE)
    elif aSb < lambda_ <= bSa:
        return (index_b, index_a, RelationType.PREFERENCE)
    return (index_a, index_b, RelationType.INCOMPARABLE)


def pessimistic_procedure(
    performance_table: NumericPerformanceTable,
    B: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    lambda_: NumericValue = 0.75,
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
) -> Dict[int, List[int]]:
    """Compute the pessimistic procedure
    In the output ranking, class -1 means incomparable class

    :param performance_table:
    :param B: profil
    :param criteria_weights:
    :param scales: Scaling List
    :param P: preference thresholds
    :param Q: indifference  thresholds
    :param V: veto thresholds
    :param lambda_: cut level
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :return: pessimistic_ranking"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    altered_performance_table = performance_table + B
    nbr_classes = len(B)
    nbr_actions = len(performance_table)
    classes = {}
    class_ = []
    actions = {action: 0 for action in range(nbr_actions)}
    for i in range(nbr_classes + nbr_actions - 1, nbr_actions - 1, -1):
        for action in actions:
            a, b, relation = outrank(
                altered_performance_table,
                criteria_weights,
                scales,
                action,
                i,
                P,
                Q,
                V,
                lambda_,
                concordance_function,
                discordance_function,
                credibility_function,
            )
            if a == action and relation == RelationType.PREFERENCE:
                class_.append(action)
                actions[action] = 1
        actions = {action: 0 for action in actions if actions[action] == 0}
        classes[i - (nbr_actions - 1)] = class_
        class_ = []
    if len(actions) > 0:
        classes[0] = []
        classes[-1] = []
        for action in actions:
            a, b, relation = outrank(
                altered_performance_table,
                criteria_weights,
                scales,
                nbr_classes,
                action,
                P,
                Q,
                V,
                lambda_,
                concordance_function,
                discordance_function,
                credibility_function,
            )
            if a == nbr_classes and (
                relation == RelationType.PREFERENCE
                or relation == RelationType.INDIFFERENCE
            ):
                classes[0].append(action)
            else:
                classes[-1].append(action)
    return classes


def optimistic_procedure(
    performance_table: NumericPerformanceTable,
    B: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    lambda_: NumericValue,
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
) -> Dict[int, List[int]]:
    """Compute the optimistic procedure.
    In the output ranking, class -1 means incomparable class

    :param performance_table:
    :param B: profil
    :param criteria_weights:
    :param scales: Scaling List
    :param P: preference thresholds
    :param Q: indifference  thresholds
    :param V: veto thresholds
    :param lambda_: cut level
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :return: optimistic_ranking"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    altered_performance_table = performance_table + B
    nbr_classes = len(B)
    nbr_actions = len(performance_table)
    classes = {}
    class_ = []
    actions = {action: 0 for action in range(nbr_actions)}
    for i in range(nbr_actions, nbr_classes + nbr_actions):
        for action in actions:
            a, b, relation = outrank(
                altered_performance_table,
                criteria_weights,
                scales,
                i,
                action,
                P,
                Q,
                V,
                lambda_,
                concordance_function,
                discordance_function,
                credibility_function,
            )
            if a == i and (relation == RelationType.PREFERENCE):
                class_.append(action)
                actions[action] = 1
        actions = {action: 0 for action in actions if actions[action] == 0}
        classes[i - nbr_actions] = class_
        class_ = []
    if len(actions) > 0:
        classes[2] = []
        classes[-1] = []
        for action in actions:
            a, b, relation = outrank(
                altered_performance_table,
                criteria_weights,
                scales,
                action,
                nbr_classes + nbr_actions - 1,
                P,
                Q,
                V,
                lambda_,
                concordance_function,
                discordance_function,
                credibility_function,
            )
            if a == action and (
                relation == RelationType.PREFERENCE
                or relation == RelationType.INDIFFERENCE
            ):
                classes[2].append(action)
            else:
                classes[-1].append(action)
    return classes


def electre_tri(
    performance_table: NumericPerformanceTable,
    B: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    lambda_: NumericValue,
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
) -> Tuple[Dict[int, List[int]], Dict[int, List[int]]]:
    """Compute the electre_tri algorithm.
    In the output ranking, class -1 means incomparable class

    :param performance_table:
    :param B: profil
    :param criteria_weights:
    :param scales: Scaling List
    :param P: preference thresholds
    :param Q: indifference  thresholds
    :param V: veto thresholds
    :param lambda_: cut level
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :return: [optimistic_ranking, pessimistic_ranking]"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    optimistic = optimistic_procedure(
        performance_table,
        B,
        criteria_weights,
        scales,
        P,
        Q,
        V,
        lambda_,
        concordance_function,
        discordance_function,
        credibility_function,
    )
    pessimistic = pessimistic_procedure(
        performance_table,
        B,
        criteria_weights,
        scales,
        P,
        Q,
        V,
        lambda_,
        concordance_function,
        discordance_function,
        credibility_function,
    )
    return optimistic, pessimistic
