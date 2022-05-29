"""This module implements utils function for outranking algorithms.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electre`.
"""
from copy import deepcopy
from typing import Dict, List

from mcda.core.aliases import NumericValue
from mcda.core.sorting import Relation, RelationType


def transitive_reduction(graph: Dict[int, List[int]]) -> Dict[int, List[int]]:
    """Remove distant preferences from graph

    :param graph: unreduced graph
    :return: reduced graph with only shortest path"""
    for key, values in graph.items():
        temp = values
        for value in values:
            if graph[value] != []:
                temp = [i for i in temp if i not in graph[value]]
        graph[key] = temp
    return graph


def transitive_reduction_matrix(
    global_final_rank: List[List[NumericValue]],
) -> List[List[NumericValue]]:
    """Remove distant preferences from matrix

    :param final_rank: matrix of preferences
    :return: reduced matrix with only shortest path"""
    graph = to_graph(global_final_rank)
    graph = transitive_reduction(graph)
    final_rank = deepcopy(global_final_rank)
    for i in range(len(final_rank)):
        for j in range(len(final_rank[i])):
            if (final_rank[i][j] == 1) and (j not in graph[i]):
                final_rank[i][j] = 0
    return final_rank


def to_graph(matrix: List[List[NumericValue]]) -> Dict[int, List[int]]:
    """Create the graph of the preferences

    :param final_rank: matrix of preferences
    :return: graph with every preferences"""
    graph: Dict[int, List[int]] = {}
    for action, relations in enumerate(matrix):
        graph[action] = []
        for compared_action, value in enumerate(relations):
            if value == 1 and action != compared_action:
                graph[action].append(compared_action)
    return graph


def dijskstra(graph: Dict[int, List[int]], x: int, y: int) -> List[int]:
    """return the longest path from an action to another

    :param final_rank: graph
    :param x: initial action
    :param y: final action
    :return: the longest path"""
    verteces = [x]
    distances = {x: 0}
    tracks: Dict[int, List[int]] = {x: []}
    while verteces:
        point = verteces.pop(0)  # or we can use deque
        for voisin in graph[point]:
            new_track = tracks[point] + [voisin]
            verteces.append(voisin)
            new_dist = distances[point] + 1
            if voisin not in distances or new_dist > distances[voisin]:
                distances[voisin] = new_dist
                tracks[voisin] = new_track
    return tracks[y]


def relation_to_matrix(relations: List[Relation]) -> List[List[NumericValue]]:
    """transform a list of relations to a matrix

    :param relations: List of relations
    :return: matrix"""
    a = []
    for relation in relations:
        if relation[0] not in a:
            a.append(relation[0])
        if relation[1] not in a:
            a.append(relation[1])
    matrix: List[List[NumericValue]] = [
        [0 for j in range(len(a))] for i in range(len(a))
    ]
    for relation in relations:
        if relation[2] == RelationType.PREFERENCE:
            matrix[relation[0]][relation[1]] = 1
        if relation[2] == RelationType.INDIFFERENCE:
            matrix[relation[0]][relation[1]] = 0.25

    return matrix


def matrix_to_relation_list(
    matrix: List[List[NumericValue]],
) -> List[Relation]:
    """transform a matrix to a list of relations

    :param matrix: the matrix of relations
    :return: List of relations"""
    relations: List[Relation] = list()
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i != j:
                if matrix[i][j] == 1:
                    relations.append((i, j, RelationType.PREFERENCE))
                if matrix[i][j] == 0.25:
                    relations.append((i, j, RelationType.INDIFFERENCE))

    return relations
