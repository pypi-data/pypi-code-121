"""This module implements the Electre 3 algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electre`.
"""
from math import floor
from typing import Any, List, Tuple, cast

from ..core.aliases import NumericPerformanceTable, NumericValue
from ..core.scales import PreferenceDirection, QuantitativeScale


def concordance_index(
    ga: NumericValue,
    gb: NumericValue,
    pga: NumericValue,
    qga: NumericValue,
    preference_direction: PreferenceDirection,
) -> NumericValue:
    """Compute the concordance index between actions a and b wrt  the criterion i.

    :param ga: preference  function  of  action a  wrt  the criterion i
    :param gb: preference  function  of  action b  wrt  the criterion i
    :param pga: preference threshold for the criterion i
    :param qga: indifference threshold for the criterion i
    :param preference_direction: direction either max or min for criterion i
    :return: concordance index value"""
    if pga < qga:
        raise ValueError(
            "Indifference value cannot be greater than preference value"
        )
    if (
        gb > (ga + pga) and preference_direction == PreferenceDirection.MAX
    ) or (gb < (ga - pga) and preference_direction == PreferenceDirection.MIN):
        return 0
    elif (
        gb <= (ga + qga) and preference_direction == PreferenceDirection.MAX
    ) or (
        gb >= (ga - qga) and preference_direction == PreferenceDirection.MIN
    ):
        return 1
    else:
        return (
            (ga + pga - gb) / (pga - qga)
            if preference_direction == PreferenceDirection.MAX
            else (-ga + pga + gb) / (pga - qga)
        )


def pairwise_concordance(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    index_a: int,
    index_b: int,
    P: List[NumericValue],
    Q: List[NumericValue],
) -> NumericValue:
    """Compute the pairwise concordance between actions a and b.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param index_a: index of action a in preference matrix
    :param index_b: index of action b in preference matrix
    :param P: preference thresholds
    :param Q: indifference thresholds
    :return: pairwise concordance value"""
    assert (
        len(performance_table) > 0
    ), "Please be sure to have correctly implemented the performance matrix"
    nb_criterias = len(performance_table[0])
    return (
        sum(
            criteria_weights[i]
            * concordance_index(
                performance_table[index_a][i],
                performance_table[index_b][i],
                P[i],
                Q[i],
                scales[i].preference_direction,
            )
            for i in range(nb_criterias)
        )
        / sum(criteria_weights[i] for i in range(nb_criterias))
    )


def discordance_index(
    ga: NumericValue,
    gb: NumericValue,
    pga: NumericValue,
    vga: NumericValue,
    preference_direction: PreferenceDirection,
) -> NumericValue:
    """Compute the discordance index between actions a and b wrt the criterion i.

    :param ga: preference  function  of  action a  wrt  the criterion i
    :param gb: preference  function  of  action b  wrt  the criterion i
    :param pga: preference threshold for the criterion i
    :param vga: veto threshold for the criterion i. None for the highest value
    :param preference_direction: direction either max or min for criterion i
    :return: discordance index value"""
    if vga is not None and pga > vga:
        raise ValueError("Preference value cannot be greater than Veto value")
    if (
        vga is None
        or (
            gb <= (ga + pga)
            and preference_direction == PreferenceDirection.MAX
        )
        or (
            gb >= (ga - pga)
            and preference_direction == PreferenceDirection.MIN
        )
    ):
        return 0
    elif (
        gb > (ga + vga) and preference_direction == PreferenceDirection.MAX
    ) or (gb < (ga - vga) and preference_direction == PreferenceDirection.MIN):
        return 1
    else:
        return (
            (gb - pga - ga) / (vga - pga)
            if preference_direction == PreferenceDirection.MAX
            else (-gb - pga + ga) / (vga - pga)
        )


def pairwise_credibility_index(
    performance_table: NumericPerformanceTable,
    index_a: int,
    index_b: int,
    C_ab,
    D_ab,
) -> NumericValue:
    """Compute the credibility index between two actions a and b.

    :param performance_table:
    :param index_a: index of action a in preference matrix
    :param index_b: index of action b in preference matrix
    :C_ab: Concordance matrix for criterion between a and b
    :D_ab:
    :return: pairwise credibility index"""
    assert (
        len(performance_table) > 0
    ), "Please be sure to have correctly implemented the performance matrix"
    nb_criterias = len(performance_table[0])
    sup_discordance = []
    for i in range(nb_criterias):
        di_ab = D_ab[i]
        if di_ab > C_ab:
            sup_discordance.append(di_ab)
    S_ab = C_ab
    if len(sup_discordance) > 0:
        for Di_ab in sup_discordance:
            S_ab = S_ab * (1 - Di_ab) / (1 - C_ab)
    return S_ab


def concordance(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
) -> List[List[NumericValue]]:
    """Compute the concordance matrix.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param P: preference thresholds
    :param Q: indifference  thresholds
    :return: concordance matrix"""

    nb_actions = len(performance_table)
    return [
        [
            pairwise_concordance(
                performance_table, criteria_weights, scales, i, j, P, Q
            )
            for j in range(nb_actions)
        ]
        for i in range(nb_actions)
    ]


def discordance(
    performance_table: NumericPerformanceTable,
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    V: List[NumericValue],
) -> List[List[List[NumericValue]]]:
    """Compute the discordance matrix.

    :param performance_table:
    :param scales:
    :param P: preference thresholds
    :param V: veto  thresholds
    :return: discordance matrix"""

    nb_criterias = len(performance_table[0])
    nb_actions = len(performance_table)
    return [
        [
            [
                discordance_index(
                    performance_table[k][j],
                    performance_table[i][j],
                    P[j],
                    V[j],
                    scales[j].preference_direction,
                )
                for j in range(nb_criterias)
            ]
            for i in range(nb_actions)
        ]
        for k in range(nb_actions)
    ]


def credibility(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    concordance_function=None,
    discordance_function=None,
) -> List[List[NumericValue]]:
    """Compute the credibility matrix.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param P: preference thresholds
    :param Q: indifference  thresholds
    :param V: veto  thresholds
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :return: discordance matrix"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )
    nb_actions = len(performance_table)
    concordance_matrix = concordance_function(
        performance_table, criteria_weights, scales, P, Q
    )
    discordance_matrix = discordance_function(performance_table, scales, P, V)
    return [
        [
            pairwise_credibility_index(
                performance_table,
                i,
                j,
                concordance_matrix[i][j],
                discordance_matrix[i][j],
            )
            for j in range(nb_actions)
        ]
        for i in range(nb_actions)
    ]


def qualification(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
    alpha: NumericValue = 0.30,
    beta: NumericValue = -0.15,
) -> List[NumericValue]:
    """Compute the qualification for each pair of alternatives a and b.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param P: preference thresholds
    :param Q: indifference thresholds
    :param V: veto thresholds
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :param alpha:  preset up values of distillation coefficients
    :param beta: preset up values of distillation coefficients
    :return: list qualifications"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    assert (
        len(performance_table) > 0
    ), "Please be sure to have correctly implemented the performance matrix"
    nb_actions = len(performance_table)
    credibility_mat = credibility_function(
        performance_table,
        criteria_weights,
        scales,
        P,
        Q,
        V,
        concordance_function,
        discordance_function,
    )
    lambda_max = max(max(credibility_mat))
    lambda_ = lambda_max - (alpha + beta * lambda_max)

    lambda_strengths = [
        sum(
            (
                credibility_mat[i][j] > lambda_
                and credibility_mat[i][j] > credibility_mat[j][i]
            )
            for j in range(nb_actions)
        )
        for i in range(nb_actions)
    ]

    lambda_weakness = [
        sum(
            (
                credibility_mat[i][j] > lambda_
                and credibility_mat[i][j] > credibility_mat[j][i]
            )
            for i in range(nb_actions)
        )
        for j in range(nb_actions)
    ]

    qualifications = [x - y for x, y in zip(lambda_strengths, lambda_weakness)]

    return cast(List[NumericValue], qualifications)


def scale(
    list_lists: List[List[int]], length: int
) -> List[List[NumericValue]]:
    """Changes the format of a list of lists of ordered actions
    into the format of an outranking matrix

    :param list_lists: the list to change
    :param length: the length of the list to change
    :return: matrix in the format of an outranking matrix"""
    matrix = cast(
        List[List[NumericValue]], [[0] * length for i in range(length)]
    )
    for index_list, list_ in enumerate(list_lists):
        for index, element in enumerate(list_):
            for element2 in list_[index + 1 :]:
                matrix[element][element2] = cast(NumericValue, -1.5)
                matrix[element2][element] = cast(NumericValue, -1.5)
            for list_2 in list_lists[index_list + 1 :]:
                for under_element in list_2:
                    matrix[cast(int, element)][cast(int, under_element)] = 1
    return cast(List[List[NumericValue]], matrix)


def descending_dist(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
    alpha: NumericValue = 0.30,
    beta: NumericValue = -0.15,
    alternative_names: List[str] = None,
) -> Tuple[List[List[Any]], List[List[NumericValue]]]:
    """Compute the descending distillation between two actions a and b.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param P: preference thresholds
    :param Q: indifference thresholds
    :param V: veto thresholds
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :param alpha:  preset up values of distillation coefficients
    :param beta: preset up values of distillation coefficients
    :param alternative_names: (optional) the name for the actions
    :return: list descending distillation and matrix of distillation"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    qualifications = qualification(
        performance_table,
        criteria_weights,
        scales,
        P,
        Q,
        V,
        concordance_function,
        discordance_function,
        credibility_function,
        alpha,
        beta,
    )
    qual = [[x, y] for x, y in zip(range(len(qualifications)), qualifications)]
    distillate = []
    while len(qual) > 0:
        indices = [qual_[0] for qual_ in qual]
        updated_performance_table = [
            performance_table[cast(int, i)] for i in indices
        ]
        qualifications = qualification(
            updated_performance_table,
            criteria_weights,
            scales,
            P,
            Q,
            V,
            concordance_function,
            discordance_function,
            credibility_function,
            alpha,
            beta,
        )
        qual = [[x, y] for x, y in zip((indices), qualifications)]

        mx = max([qual_[1]] for qual_ in qual)[0]

        maxes = [
            qual[index] for index in range(len(qual)) if qual[index][1] == mx
        ]
        if len(maxes) > 1:
            new_performance_table = [
                performance_table[cast(int, i)] for i, k in maxes
            ]
            new_qualifications = qualification(
                new_performance_table,
                criteria_weights,
                scales,
                P,
                Q,
                V,
                concordance_function,
                discordance_function,
                credibility_function,
                alpha,
                beta,
            )
            new_maxes = maxes
            mx = max(new_qualifications)
            maxes = [
                new_maxes[index]
                for index in range(len(new_qualifications))
                if new_qualifications[index] == mx
            ]
        distillate.append(list(maxes[i][0] for i in range(0, len(maxes))))
        for i in maxes:
            qual.remove(i)
    distillation_matrix = scale(
        cast(List[List[int]], distillate), len(performance_table)
    )
    distillation = [
        list(
            action
            if alternative_names is None
            else alternative_names[int(action)]
            for action in list_actions
        )
        for list_actions in distillate
    ]
    return distillation, distillation_matrix


def ascending_dist(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
    alpha: NumericValue = 0.30,
    beta: NumericValue = -0.15,
    alternative_names: List[str] = None,
) -> Tuple[List[List[Any]], List[List[NumericValue]]]:
    """Compute the ascending distillation between two actions a and b.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param P: preference thresholds
    :param Q: indifference thresholds
    :param V: veto thresholds
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :param alpha:  preset up values of distillation coefficients
    :param beta: preset up values of distillation coefficients
    :param alternative_names: (optional) the name for the actions
    :return: list ascending distillation and matrix of distillation"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )
    qualifications = qualification(
        performance_table,
        criteria_weights,
        scales,
        P,
        Q,
        V,
        concordance_function,
        discordance_function,
        credibility_function,
        alpha,
        beta,
    )

    qual = [[x, y] for x, y in zip(range(len(qualifications)), qualifications)]
    distillate = []
    while len(qual) > 0:
        indices = [qual_[0] for qual_ in qual]
        updated_performance_table = [
            performance_table[cast(int, i)] for i in indices
        ]
        qualifications = qualification(
            updated_performance_table,
            criteria_weights,
            scales,
            P,
            Q,
            V,
            concordance_function,
            discordance_function,
            credibility_function,
            alpha,
            beta,
        )
        qual = [[x, y] for x, y in zip((indices), qualifications)]

        minimum = min([qual_[1]] for qual_ in qual)[0]

        mins = [
            qual[index]
            for index in range(len(qual))
            if qual[index][1] == minimum
        ]
        if len(mins) > 1:
            new_performance_table = [
                performance_table[cast(int, i)] for i, k in mins
            ]
            new_qualifications = qualification(
                new_performance_table,
                criteria_weights,
                scales,
                P,
                Q,
                V,
                concordance_function,
                discordance_function,
                credibility_function,
                alpha,
                beta,
            )
            new_mins = mins
            minimum = min(new_qualifications)
            mins = [
                new_mins[index]
                for index in range(len(new_qualifications))
                if new_qualifications[index] == minimum
            ]
        distillate.append(list(mins[i][0] for i in range(0, len(mins))))
        for i in mins:
            qual.remove(i)
    distillate = distillate[::-1]
    distillation_matrix = scale(
        cast(List[List[int]], distillate), len(performance_table)
    )
    distillation = [
        list(
            action
            if alternative_names is None
            else alternative_names[int(action)]
            for action in list_actions
        )
        for list_actions in distillate
    ]
    return distillation, distillation_matrix


def final_ranking(
    distillation1: List[List[NumericValue]],
    distillation2: List[List[NumericValue]],
) -> List[List[NumericValue]]:
    """Compute the final ranking by combining
    the ascending and descending distillation.

    :param distillation1: ascending distillation
    :param distillation2: descending distillation
    :return: final ranking of Electre III"""

    final_matrix = [
        list((1 if floor(abs(a * b)) == 1 else a * b) for a, b in zip(x, y))
        for x, y in zip(distillation1, distillation2)
    ]
    return final_matrix


def electre_iii(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    P: List[NumericValue],
    Q: List[NumericValue],
    V: List[NumericValue],
    concordance_function=None,
    discordance_function=None,
    credibility_function=None,
    alpha: NumericValue = 0.30,
    beta: NumericValue = -0.15,
    alternative_names: List[str] = None,
) -> List[List[NumericValue]]:
    """Compute the complete electreIII algorithm

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param P: preference thresholds
    :param Q: indifference thresholds
    :param V: veto thresholds
    :param alpha:  preset up values of distillation coefficients
    :param beta: preset up values of distillation coefficients
    :param concordance_function: function used to calculate concordance matrix
    :param discordance_function: function used to calculate discordance matrix
    :param credibility_function: function used to calculate credibility matrix
    :param alternative_names: (optional) the name for the actions
    :return: final ranking of Electre III"""
    concordance_function = (
        concordance if concordance_function is None else concordance_function
    )

    discordance_function = (
        discordance if discordance_function is None else discordance_function
    )

    credibility_function = (
        credibility if credibility_function is None else credibility_function
    )

    ascending_distillate, ascending_dist_matrix = ascending_dist(
        performance_table,
        criteria_weights,
        scales,
        P,
        Q,
        V,
        concordance_function,
        discordance_function,
        credibility_function,
        alpha,
        beta,
        alternative_names,
    )
    descending_distillate, descending_dist_matrix = descending_dist(
        performance_table,
        criteria_weights,
        scales,
        P,
        Q,
        V,
        concordance_function,
        discordance_function,
        credibility_function,
        alpha,
        beta,
        alternative_names,
    )
    final_matrix = final_ranking(ascending_dist_matrix, descending_dist_matrix)
    return final_matrix
