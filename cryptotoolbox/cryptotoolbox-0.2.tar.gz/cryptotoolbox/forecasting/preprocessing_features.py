import numpy as np
import pandas as pd
from collections import Counter
from heapq import nlargest
from numba import njit, jit
from numba.typed import Dict,List


# def most_correlated_features(X,threshold):
#     generic_features = ['close','high', 'low', 'open', 'volume']
#     columns_to_compute = [col for col in X.columns if col not in generic_features]
#     output_correlations = []
#     for i in range(len(columns_to_compute)):
#         for j in range(i+1,len(columns_to_compute)):
#             left_feature = columns_to_compute[i]
#             right_feature=columns_to_compute[j]
#             if left_feature != right_feature:
#                 # print(left_feature, right_feature)
#                 # print(X[left_feature].nunique())
#                 # print('done')
#                 correlation_matrix = np.corrcoef(X[left_feature],X[right_feature])
#                 output_correlations.append(
#                     {
#                         'daily_feature_1':left_feature,
#                         'daily_feature_2':right_feature,
#                         'correlation':correlation_matrix[0][1]
#                     }
#                 )
#
#     output_correlations_df = pd.DataFrame(output_correlations)
#     output_correlations_df['abs_correlation'] = abs(output_correlations_df['correlation'] )
#     output_correlations_df = output_correlations_df.sort_values(by='abs_correlation', ascending=False)
#     columns_to_drop = output_correlations_df.loc[output_correlations_df['abs_correlation'] > threshold]['daily_feature_2'].unique()
#     return columns_to_drop

def rescalize(y, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (y - range1[0]) / delta1) + range2[0]

@njit()
def compute_features_correlation(X_array):
    X_array_trans = X_array.transpose()
    output_correlations = np.empty((len(X_array_trans), len(X_array_trans)))
    for i in range(len(X_array_trans)):
        for j in range(i+1,len(X_array_trans)):
            correlation_matrix = np.corrcoef(X_array_trans[i],X_array_trans[j])
            output_correlations[i][j] = correlation_matrix[0][1]
    return output_correlations

def most_correlated_features(X,threshold):
    generic_features = ['close', 'high', 'low', 'open', 'volume']
    columns_to_compute = [col for col in X.columns if col not in generic_features]
    text_features = X[columns_to_compute]
    output_correlations = compute_features_correlation(text_features.values)
    output_correlations_df = pd.DataFrame(output_correlations)
    output_correlations_df.columns = text_features.columns
    bool_df = (output_correlations_df.loc[:, :] < threshold) & (output_correlations_df.loc[:, :] > -threshold)
    columns_to_drop = bool_df.columns[bool_df.isin([False]).any()]
    return columns_to_drop


@njit()
def compute_correlation_to_return(X_array, ret_array):
    X_array_trans = X_array.transpose()
    output_correlations = np.empty((1, len(X_array_trans)))
    for i in range(len(X_array_trans)):
        correlation_matrix = np.corrcoef(X_array_trans[i],ret_array)
        output_correlations[0][i] = correlation_matrix[0][1]
    return output_correlations

def features_correlation_to_return(X,y):
    output_correlations = compute_correlation_to_return(X.values,y.values)
    output_correlations_df = pd.DataFrame(output_correlations)
    output_correlations_df.columns = X.columns
    # return (output_correlations_df>0).astype(int).replace({0: -1})
    correlation_to_return = output_correlations_df.values
    correlation_to_return = correlation_to_return.reshape(correlation_to_return.shape[1])
    return correlation_to_return



def get_anova_columns(X,y):
    diff = {}
    # means = X.mean().to_dict()
    medians = X.median().to_dict()
    # means_df = (X[means.keys()] >= list(means.values())).astype(int)
    # means_df['return'] = augmento_df['return']
    medians_df = (X[medians.keys()] >= list(medians.values())).astype(int)
    medians_df['return'] = y
    data_df = medians_df.copy()
    for column in X.columns:
        diff[column] = abs(pd.DataFrame(data_df.groupby(column)['return'].mean()).diff().values[-1][0])
    anova_features = nlargest(10, diff, key=diff.get)
    return anova_features


def get_binarization_threshold(X):
        return X.mean().to_dict()

def binarize_features(X,features_threshold):
    X[list(features_threshold.keys())] = (X[features_threshold.keys()] >= list(features_threshold.values())).astype(int)
    return X