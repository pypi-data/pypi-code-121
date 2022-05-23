"""
the names of ECOC methods :
1.OVA ECOC
2.OVO ECOC
3.Dense random ECOC
4.Sparse random ECOC
5.D ECOC
6.AGG ECOC
7.CL_ECOC
8.ECOC_ONE
9.ECOC_MDC

There are all defined as class, which inherit __BaseECOC
"""
import logging
import random
from itertools import combinations
import copy
from scipy.special import comb
import numpy as np
from kdmt.matrix import has_duplicate_col, has_duplicate_row
from kolibri.utils.matrix import exist_two_class, get_data_subset
from kolibri.backend.sklearn.meta.ecoc.sffs import sffs
from kolibri.backend.sklearn.meta.ecoc import criterion
from kdmt.distances import euclidean_distance

def create_ova_matrix(label, data=None):
    """
    Description
    -----------
    Create a one versus all code matrix

    :param label: class labels
    :return: code matrix and the the index of the lables
    """
    index = {l: i for i, l in enumerate(np.unique(label))}
    matrix = np.eye(len(index)) * 2 - 1
    return matrix, index


def create_ovo_matrix(label, data=None):
    """
    Description
    -----------
    Create a one versus one code matrix

    :param label: class labels
    :return: code matrix and the the index of the lables
    """

    index = {l: i for i, l in enumerate(np.unique(label))}
    groups = combinations(range(len(index)), 2)
    matrix_row = len(index)
    matrix_col = np.int(comb(len(index), 2))
    col_count = 0
    matrix = np.zeros((matrix_row, matrix_col))
    for group in groups:
        class_1_index = group[0]
        class_2_index = group[1]
        matrix[class_1_index, col_count] = 1
        matrix[class_2_index, col_count] = -1
        col_count += 1
    return matrix, index


def create_rand_matrix(label, data=None):
    """
    Dense random ECOC
    """
    while True:
        index = {l: i for i, l in enumerate(np.unique(label.data))}
        matrix_row = len(index)
        if matrix_row > 3:
            matrix_col = np.int(np.floor(10 * np.log10(matrix_row)))
        else:
            matrix_col = matrix_row
        matrix = np.random.random((matrix_row, matrix_col))
        class_1_index = matrix > 0.5
        class_2_index = matrix < 0.5
        matrix[class_1_index] = 1
        matrix[class_2_index] = -1
        if (not has_duplicate_col(matrix)) and (not has_duplicate_row(matrix)) and exist_two_class(matrix):
            return matrix, index


def create_sparse_matrix(label, data=None):
    """
    Sparse random ECOC
    """
    while True:
        index = {l: i for i, l in enumerate(np.unique(label))}
        matrix_row = len(index)
        if matrix_row > 3:
            matrix_col = np.int(np.floor(15 * np.log10(matrix_row)))
        else:
            matrix_col = np.int(np.floor(10 * np.log10(matrix_row)))
        matrix = np.random.random((matrix_row, matrix_col))
        class_0_index = np.logical_and(0.25 <= matrix, matrix < 0.75)
        class_1_index = matrix >= 0.75
        class_2_index = matrix < 0.25
        matrix[class_0_index] = 0
        matrix[class_1_index] = 1
        matrix[class_2_index] = -1
        if (not has_duplicate_col(matrix)) and (not has_duplicate_row(matrix)) and exist_two_class(matrix):
            return matrix, index


def create_descriminant_matrix(label, data):
    """
    Discriminant ECOC
    """

    index = {l: i for i, l in enumerate(np.unique(label))}
    matrix = None
    labels_to_divide = [np.unique(label)]

    while len(labels_to_divide) > 0:
        label_set = labels_to_divide.pop(0)
        datas, labels = get_data_subset(data, label, label_set)
        class_1_variety_result, class_2_variety_result = sffs(datas, labels)
        new_col = np.zeros((len(index), 1))
        for i in class_1_variety_result:
            new_col[index[i]] = 1
        for i in class_2_variety_result:
            new_col[index[i]] = -1
        if matrix is None:
            matrix = copy.copy(new_col)
        else:
            matrix = np.hstack((matrix, new_col))
        if len(class_1_variety_result) > 1:
            labels_to_divide.append(class_1_variety_result)
        if len(class_2_variety_result) > 1:
            labels_to_divide.append(class_2_variety_result)
    return matrix, index


def create_agglomerative_matrix(label, data):
    """
    Agglomerative ECOC
    """
    index = {l: i for i, l in enumerate(np.unique(label))}
    matrix = None
    labels_to_agg = np.unique(label)
    labels_to_agg_list = [[x] for x in labels_to_agg]
    label_dict = {labels_to_agg[value]: value for value in range(labels_to_agg.shape[0])}
    num_of_length = len(labels_to_agg_list)
    class_1_variety = []
    class_2_variety = []
    while len(labels_to_agg_list) > 1:
        score_result = np.inf
        for i in range(0, len(labels_to_agg_list) - 1):
            for j in range(i + 1, len(labels_to_agg_list)):
                class_1_data, class_1_label = get_data_subset(data, label, labels_to_agg_list[i])
                class_2_data, class_2_label = get_data_subset(data, label, labels_to_agg_list[j])
                score = criterion.agg_score(class_1_data, class_1_label, class_2_data, class_2_label,
                                                score=criterion.max_distance_score)
                if score < score_result:
                    score_result = score
                    class_1_variety = labels_to_agg_list[i]
                    class_2_variety = labels_to_agg_list[j]
        new_col = np.zeros((num_of_length, 1))
        for i in class_1_variety:
            new_col[label_dict[i]] = 1
        for i in class_2_variety:
            new_col[label_dict[i]] = -1
        if matrix is None:
            matrix = new_col
        else:
            matrix = np.hstack((matrix, new_col))
        new_class = class_1_variety + class_2_variety
        labels_to_agg_list.remove(class_1_variety)
        labels_to_agg_list.remove(class_2_variety)
        labels_to_agg_list.insert(0, new_class)
    return matrix, index


def create_centroid_matrix(label, data):
    """
    Centroid loss ECOC, which use regressors as base estimators
    """
    index = {l: i for i, l in enumerate(np.unique(label))}
    matrix = None
    labels_to_divide = [np.unique(label)]
    data=data.toarray()
    while len(labels_to_divide) > 0:
        label_set = labels_to_divide.pop(0)
        datas, labels = get_data_subset(data, label, label_set)
        class_1_variety_result, class_2_variety_result = sffs(datas, labels,
                                                                  score=criterion.max_center_distance_score)
        class_1_data_result, class_1_label_result = get_data_subset(data, label, class_1_variety_result)
        class_2_data_result, class_2_label_result = get_data_subset(data, label, class_2_variety_result)
        class_1_center_result = np.average(class_1_data_result, axis=0)
        class_2_center_result = np.average(class_2_data_result, axis=0)
        belong_to_class_1 = [
            euclidean_distance(x, class_1_center_result) <= euclidean_distance(x, class_2_center_result)
            for x in class_1_data_result]
        belong_to_class_2 = [
            euclidean_distance(x, class_2_center_result) <= euclidean_distance(x, class_1_center_result)
            for x in class_2_data_result]
        class_1_true_num = {k: 0 for k in class_1_variety_result}
        class_2_true_num = {k: 0 for k in class_2_variety_result}
        for y in class_1_label_result[belong_to_class_1]:
            class_1_true_num[y] += 1
        for y in class_2_label_result[belong_to_class_2]:
            class_2_true_num[y] += 1
        class_1_label_count = {k: list(class_1_label_result).count(k) for k in class_1_variety_result}
        class_2_label_count = {k: list(class_2_label_result).count(k) for k in class_2_variety_result}
        class_1_ratio = {k: class_1_true_num[k] / class_1_label_count[k] for k in class_1_variety_result}
        class_2_ratio = {k: -class_2_true_num[k] / class_2_label_count[k] for k in class_2_variety_result}
        new_col = np.zeros((len(index), 1))
        for i in class_1_ratio:
            new_col[index[i]] = class_1_ratio[i]
        for i in class_2_ratio:
            new_col[index[i]] = class_2_ratio[i]
        if matrix is None:
            matrix = copy.copy(new_col)
        else:
            matrix = np.hstack((matrix, new_col))
        if len(class_1_variety_result) > 1:
            labels_to_divide.append(class_1_variety_result)
        if len(class_2_variety_result) > 1:
            labels_to_divide.append(class_2_variety_result)
    return matrix, index


def get_code_matrix(method='rand'):
    return eval('create_{}_matrix'.format(method))