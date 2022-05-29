"""This module implements the electre 2 algorithm.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electre`.
"""

from typing import Any, List, Tuple, cast

from mcda.core.aliases import NumericPerformanceTable, NumericValue
from mcda.core.scales import QuantitativeScale
from mcda.outranking.electre1 import concordance, discordance


def outranking_calculus(
    concordance: List[List[NumericValue]],
    discordance: List[List[NumericValue]],
    c_hat_sup: NumericValue,
    c_hat_inf: NumericValue,
    d_hat_sup: NumericValue,
    d_hat_inf: NumericValue,
) -> Tuple[List[List[NumericValue]], List[List[NumericValue]]]:
    """Calculate the weak and strong outranking matrices.

    :param concordance: concordance matrix
    :param discordance: discordance matrix
    :param c_hat_sup: higher concordance threshold
    :param c_hat_inf: lower concordance threshold
    :param d_hat_sup: higher discordance threshold
    :param d_hat_inf: lower discordance threshold
    :return:
        weak & strong outranking matrices based
        on a concordance & discordance matrices
    """
    nb_columns = len(concordance[0])
    nb_lines = len(concordance)
    s_dominance_matrix = []
    w_dominance_matrix = []
    for i in range(nb_lines):
        s_dominance_line = []
        w_dominance_line = []
        for j in range(nb_columns):
            s_dominance_line.append(
                cast(
                    NumericValue,
                    0.0
                    if i == j
                    else (
                        1.0
                        if (
                            concordance[i][j] >= concordance[j][i]
                            and concordance[i][j] >= c_hat_sup
                            and discordance[i][j] <= d_hat_inf
                        )
                        else 0.0
                    ),
                )
            )

            w_dominance_line.append(
                cast(
                    NumericValue,
                    0.0
                    if i == j
                    else (
                        1.0
                        if (
                            (
                                concordance[i][j] >= concordance[j][i]
                                and concordance[i][j] >= c_hat_sup
                                and d_hat_sup >= discordance[i][j] >= d_hat_inf
                            )
                            or (
                                concordance[i][j] >= concordance[j][i]
                                and concordance[i][j] >= c_hat_inf
                                and discordance[i][j] <= d_hat_sup
                            )
                        )
                        else 0.0
                    ),
                )
            )
        s_dominance_matrix.append(s_dominance_line)
        w_dominance_matrix.append(w_dominance_line)
    return s_dominance_matrix, w_dominance_matrix


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
                matrix[element][element2] = cast(NumericValue, -0.5)
                matrix[element2][element] = cast(NumericValue, -0.5)
            for list_2 in list_lists[index_list + 1 :]:
                for under_element in list_2:
                    matrix[cast(int, element)][cast(int, under_element)] = 1
    return cast(List[List[NumericValue]], matrix)


def descending_dist(
    concordance_mat: List[List[NumericValue]],
    discordance_mat: List[List[NumericValue]],
    c_hat_sup: NumericValue,
    c_hat_inf: NumericValue,
    d_hat_sup: NumericValue,
    d_hat_inf: NumericValue,
    alternative_names: List[str] = None,
) -> Tuple[List[List[Any]], List[List[NumericValue]]]:
    """Compute the descending distillation.

    :param concordance_mat: List[List[NumericValue]],
    :param discordance_mat: List[List[NumericValue]],
    :param c_hat_sup: higher concordance threshold
    :param c_hat_inf: lower concordance threshold
    :param d_hat_sup: higher discordance threshold
    :param d_hat_inf: lower discordance threshold
    :param alternative_names: (optional) the name for the actions
    :return: list of the descending distillation"""
    s_dominance_matrix, w_dominance_matrix = outranking_calculus(
        concordance_mat,
        discordance_mat,
        c_hat_sup,
        c_hat_inf,
        d_hat_sup,
        d_hat_inf,
    )
    distillate = []
    rest = list(range(len(w_dominance_matrix)))
    while len(rest) > 0:
        B = []
        for action_a in rest:
            outranked = 0
            for action_b in rest:
                if s_dominance_matrix[action_b][action_a] == 1.0:
                    outranked += 1
                    break
            if outranked == 0:
                B.append(action_a)

        A = []
        for action_a in rest:
            outranked = 0
            for action_b in B:
                if w_dominance_matrix[action_b][action_a] == 1.0:
                    outranked += 1
                    break
            if outranked == 0:
                A.append(action_a)
        for i in A:
            rest.remove(i)
        distillate.append(A)
    distillation_matrix = scale(
        cast(List[List[int]], distillate), len(concordance_mat)
    )
    distillation = [
        list(
            action if alternative_names is None else alternative_names[action]
            for action in list_actions
        )
        for list_actions in distillate
    ]
    return distillation, distillation_matrix


def ascending_dist(
    concordance_mat: List[List[NumericValue]],
    discordance_mat: List[List[NumericValue]],
    c_hat_sup: NumericValue,
    c_hat_inf: NumericValue,
    d_hat_sup: NumericValue,
    d_hat_inf: NumericValue,
    alternative_names: List[str] = None,
) -> Tuple[List[List[Any]], List[List[NumericValue]]]:
    """Compute the ascending distillation.

    :param concordance_mat: List[List[NumericValue]],
    :param discordance_mat: List[List[NumericValue]],
    :param c_hat_sup: higher concordance threshold
    :param c_hat_inf: lower concordance threshold
    :param d_hat_sup: higher discordance threshold
    :param d_hat_inf: lower discordance threshold
    :param alternative_names: (optional) the name for the actions
    :return: list of the ascending distillation"""
    s_dominance_matrix, w_dominance_matrix = outranking_calculus(
        concordance_mat,
        discordance_mat,
        c_hat_sup,
        c_hat_inf,
        d_hat_sup,
        d_hat_inf,
    )
    distillate = []
    rest = list(range(len(w_dominance_matrix)))
    while len(rest) > 0:
        B = []
        for action_a in rest:
            outrank = 0
            for action_b in rest:
                if s_dominance_matrix[action_a][action_b] == 1.0:
                    outrank += 1
                    break
            if outrank == 0:
                B.append(action_a)

        A = []
        for action_a in B:
            outrank = 0
            for action_b in rest:
                if w_dominance_matrix[action_a][action_b] == 1.0:
                    outrank += 1
                    break
            if outrank == 0:
                A.append(action_a)
        for i in A:
            rest.remove(i)
        distillate.append(A)
    distillation_matrix = scale(
        cast(List[List[int]], distillate)[::-1], len(concordance_mat)
    )
    distillation = [
        list(
            action if alternative_names is None else alternative_names[action]
            for action in list_actions
        )
        for list_actions in distillate[::-1]
    ]
    return distillation, distillation_matrix


def final_ranking(
    distillation1: List[List[NumericValue]],
    distillation2: List[List[NumericValue]],
) -> List[List[NumericValue]]:
    """Compute the final ranking by combining the
    ascending and descending distillation.

    :param distillation1: ascending distillation
    :param distillation2: descending distillation
    :return: final ranking of Electre II"""

    final_matrix = [
        list((a * b if a * b >= 0 else 0) for a, b in zip(x, y))
        for x, y in zip(distillation1, distillation2)
    ]
    return final_matrix


def electre_ii(
    performance_table: NumericPerformanceTable,
    criteria_weights: List[NumericValue],
    scales: List[QuantitativeScale],
    c_hat_sup: NumericValue,
    c_hat_inf: NumericValue,
    d_hat_sup: NumericValue,
    d_hat_inf: NumericValue,
    concordance_matrix=None,
    discordance_matrix=None,
    alternative_names: List[str] = None,
) -> List[List[NumericValue]]:
    """Compute final ranking for Electre II.

    :param performance_table:
    :param criteria_weights:
    :param scales:
    :param c_hat_sup: higher concordance threshold
    :param c_hat_inf: lower concordance threshold
    :param d_hat_sup: higher discordance threshold
    :param d_hat_inf: lower discordance threshold
    :param concordance_matrix: concordance matrix
    :param discordance_matrix: discordance matrix
    :param alternative_names: (optional) the name for the actions
    :return: list of final ranking for Electre II"""
    concordance_matrix = (
        concordance(performance_table, criteria_weights, scales)
        if concordance_matrix is None
        else concordance_matrix
    )
    discordance_matrix = (
        discordance(performance_table)
        if discordance_matrix is None
        else discordance_matrix
    )
    ascending_distillate, ascending_dist_matrix = ascending_dist(
        concordance_matrix,
        discordance_matrix,
        c_hat_sup,
        c_hat_inf,
        d_hat_sup,
        d_hat_inf,
        alternative_names,
    )
    descending_distillate, descending_dist_matrix = descending_dist(
        concordance_matrix,
        discordance_matrix,
        c_hat_sup,
        c_hat_inf,
        d_hat_sup,
        d_hat_inf,
        alternative_names,
    )
    final_rank = final_ranking(ascending_dist_matrix, descending_dist_matrix)
    return final_rank
