""" This module implements the graphic display of the GAIA plane

Implementations naming conventions are taken from
:cite:p:`figueira2005mcda`
"""

from typing import List

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from mcda.core.aliases import (  # Cannot do from ..core.aliases
    NumericPerformanceTable,
    NumericValue,
)
from mcda.outranking.promethee_common import (
    PreferenceFunction,
    preference_degree_calculation,
)


def unicriterion_net_flow(
    alternative: int,
    criterion: int,
    alternatives: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
) -> NumericValue:
    """Computes the single criterion net flow of an alternative
    considering only a criterion.

    :param alternative: index of the alternative
    :param criterion: index of the criterion
    :param alternatives: performance table
    :param preference_func_list:
    :param p_list:
    :param q_list:
    :param s_list:
    :return: net flow
    """
    net_flow = 0.0
    for i in range(len(alternatives)):
        net_flow += preference_degree_calculation(
            preference_func_list[criterion],
            p_list[criterion],
            q_list[criterion],
            s_list[criterion],
            alternatives[alternative][criterion],
            alternatives[i][criterion],
        ) - preference_degree_calculation(
            preference_func_list[criterion],
            p_list[criterion],
            q_list[criterion],
            s_list[criterion],
            alternatives[i][criterion],
            alternatives[alternative][criterion],
        )
    return net_flow


def unicriterion_flow_matrix(
    alternatives: NumericPerformanceTable,
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
) -> NumericPerformanceTable:
    """Computes the whole matrix M of single criterion net flows.

    :param alternatives: performance table
    :param preference_func_list:
    :param p_list:
    :param q_list:
    :param s_list:
    :return: net flow matrix
    """
    unicrit_flows = [
        [_ for _ in range(len(alternatives[0]))]
        for _ in range(len(alternatives))
    ]
    for act in range(len(alternatives)):
        for cri in range(len(alternatives[0])):
            unicrit_flows[act][cri] = unicriterion_net_flow(
                act,
                cri,
                alternatives,
                preference_func_list,
                p_list,
                q_list,
                s_list,
            )
    return unicrit_flows


def gaia(
    alternatives: NumericPerformanceTable,
    alternatives_names: List[str],
    preference_func_list: List[PreferenceFunction],
    p_list: List[NumericValue],
    q_list: List[NumericValue],
    s_list: List[NumericValue],
    weights: List[NumericValue],
    criteria_names: List[str],
):
    """Plots the GAIA plane and displays in the top-left corner
    the ratio of saved information by the PCA, delta.

    :param alternatives: performance table
    :param alternatives_names: corresponding alternatives' names
    :param preference_func_list:
    :param p_list:
    :param q_list:
    :param s_list:
    :param weights:
    :param criteria_names: corresponding criteria's names

    """
    net_flows = unicriterion_flow_matrix(
        alternatives, preference_func_list, p_list, q_list, s_list
    )

    pca = PCA(n_components=2)
    pca.fit(net_flows)
    delta = pca.explained_variance_ratio_[0] + pca.explained_variance_ratio_[1]
    alternative_vectors = pca.transform(net_flows)
    criterions = [
        [0 for _ in range(len(alternatives[0]))]
        for _ in range(len(alternatives[0]))
    ]
    for i in range(len(alternatives[0])):
        criterions[i][i] = 1
    criterion_vectors = pca.transform(criterions)
    S = sum(weights)
    pi = [0, 0]
    for i in range(len(alternatives[0])):
        pi[0] += criterion_vectors[i][0] * weights[i] / S
        pi[1] += criterion_vectors[i][1] * weights[i] / S

    plt.figure(figsize=[10, 10])

    for i in range(len(alternative_vectors)):
        plt.scatter(
            alternative_vectors[i][0],
            alternative_vectors[i][1],
            s=100,
            label=alternatives_names[i],
        )
    for i in range(len(criterion_vectors)):
        plt.text(
            criterion_vectors[i][0],
            criterion_vectors[i][1],
            criteria_names[i],
            ha="center",
        )
        plt.arrow(0, 0, criterion_vectors[i][0], criterion_vectors[i][1])

    plt.arrow(0, 0, pi[0], pi[1])
    plt.scatter(pi[0], pi[1], s=150, marker="*", label=r"$\pi$")

    ax = plt.gca()
    xmin, _ = ax.get_xlim()
    _, ymax = ax.get_ylim()

    plt.text(
        xmin, ymax, r"$\delta$ = %.3f" % delta, bbox=dict(boxstyle="round")
    )

    plt.legend()
    plt.plot()
    plt.show()
