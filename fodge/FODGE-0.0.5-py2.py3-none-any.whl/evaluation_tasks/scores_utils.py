"""
Utils file for first temporal link prediction task to calculate the scores.
"""

import numpy as np


def calculate_avg_score(score, rounds):
    """
    Given the lists of scores for every round of every split, calculate the average score of every split.
    :param score: F1-micro / F1-macro / Accuracy / Auc
    :param rounds: How many times the experiment has been applied for each split.
    :return: Average score for every split
    """
    all_avg_scores = []
    for i in range(score.shape[1]):
        avg_score = (np.sum(score[:, i])) / rounds
        all_avg_scores.append(avg_score)
    return all_avg_scores


def calculate_all_avg_scores_lp(micro, macro, acc, auc, rounds):
    """
    For all scores calculate the average score for every split. The function returns list for every
    score type- 1 for cheap node2vec and 2 for regular node2vec.
    """
    all_avg_micro = calculate_avg_score(micro, rounds)
    all_avg_macro = calculate_avg_score(macro, rounds)
    all_avg_acc = calculate_avg_score(acc, rounds)
    all_avg_auc = calculate_avg_score(auc, rounds)
    return all_avg_micro, all_avg_macro, all_avg_acc, all_avg_auc


def initialize_scores():
    """
    Helper function to initialize the scores for link prediction mission
    """
    my_micro = [0, 0, 0, 0, 0]
    my_macro = [0, 0, 0, 0, 0]
    my_acc = [0, 0, 0, 0, 0]
    my_auc = [0, 0, 0, 0, 0]
    return my_micro, my_macro, my_acc, my_auc


def first_help_calculate_lp(score, avg_score):
    """
    Helper function for scores calculation
    """
    score = [x + y for x, y in zip(score, avg_score)]
    return score


def second_help_calculate_lp(score, number_of_sub_graphs):
    """
    Helper function for scores calculation
    """
    score = [x / number_of_sub_graphs for x in score]
    return score