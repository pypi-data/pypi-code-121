import numpy as np
from kdmt.dict import get_keys_for_value
import copy

def exist_two_class(matrix):
    """
    to ensure all cols in coding matrix have 1 and -1
    :param matrix: coding matrix
    :return: true or false
    """
    col_count = matrix.shape[1]
    for i in range(col_count):
        col_unique = np.unique(matrix[:, i])
        if (1 not in col_unique) or (-1 not in col_unique):
            return False
    return True

def get_data_subset(data, label, target_label):
    """
    to get data with certain labels
    :param data: data set
    :param label: label corresponding to data
    :param target_label: the label which we want to get certain data
    :return:
    """
    data_subset = np.array([data[i] for i in range(len(label)) if label[i] in target_label])
    label_subset = np.array([label[i] for i in range(len(label)) if label[i] in target_label])
    return data_subset, label_subset

def get_subset_feature_from_matrix(matrix, index):
    """
    I forget what it uses to.
    :param matrix:
    :param index:
    :return:
    """
    res = []
    for i in range(matrix.shape[1]):
        class_1 = []
        class_2 = []
        for j in range(matrix.shape[0]):
            if matrix[j, i] > 0:
                class_1.append(get_keys_for_value(index, j)[0])
            elif matrix[j, i] < 0:
                class_2.append(get_keys_for_value(index, j)[0])
        res.append(class_1)
        res.append(class_2)
    return res


def create_col_from_partition(class_1_variety, class_2_variety, index):
    """
    create a col based on a certain partition
    :param class_1_variety: a part of partition as positive group
    :param class_2_variety: another part of partition as negative group
    :param index: index of coding matrix
    :return: a col
    """
    col = np.zeros((len(index), 1))
    for i in class_1_variety:
        col[index[i]] = 1
    for i in class_2_variety:
        col[index[i]] = -1
    return col

def get_data_from_col(data, label, col, index):
    """
    to get data subset form a col, where the value is not zero
    :param data: data set
    :param label: label corresponding to data
    :param col: the col we want to get data subset
    :param index: the index for matrix
    :return: data subset and corresponding labels
    """
    data_result = None
    cla_result = None
    for i in range(len(col)):
        if col[i] != 0:
            d = np.array([data[k] for k in range(len(label)) if label[k] == get_key(index, i)])
            c = np.ones(len(d)) * col[i]
            if d.shape[0] > 0 and d.shape[1] > 0:
                if data_result is None:
                    data_result = copy.copy(d)
                    cla_result = copy.copy(c)
                else:
                    data_result = np.vstack((data_result, d))
                    cla_result = np.hstack((cla_result, c))
    return data_result, cla_result