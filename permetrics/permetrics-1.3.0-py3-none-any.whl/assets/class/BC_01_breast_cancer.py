#!/usr/bin/env python
# Created by "Thieu" at 15:54, 18/05/2022 ----------%                                                                               
#       Email: nguyenthieu2102@gmail.com            %                                                    
#       Github: https://github.com/thieu1995        %                         
# --------------------------------------------------%

import numpy as np
from sklearn.metrics import confusion_matrix
# from sklearn.datasets import load_breast_cancer
# from sklearn.preprocessing import StandardScaler
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import confusion_matrix
#
# dataset = load_breast_cancer()
#
# print('Target variables  : ', dataset['target_names'])
# (unique, counts) = np.unique(dataset['target'], return_counts=True)
# print('Unique values of the target variable', unique)
# print('Counts of the target variable :', counts)
#
# ## 'malignant': 0,  'benign': 1
#
# X = dataset['data']
# y = dataset['target']
#
# standardizer = StandardScaler()
# X = standardizer.fit_transform(X)
# X_train, X_test, y_train, y_test = train_test_split(X, y , test_size=0.25, random_state=0)
#
# model = LogisticRegression()
# model.fit(X_train, y_train)
# predictions = model.predict(X_test)
#
# ## Calculate the accuracy score by comparing the actual values and predicted values.
# cm = confusion_matrix(y_test, predictions)
# print(cm)
#
# TN, FP, FN, TP = confusion_matrix(y_test, predictions).ravel()
# print('True Positive(TP)  = ', TP)
# print('False Positive(FP) = ', FP)
# print('True Negative(TN)  = ', TN)
# print('False Negative(FN) = ', FN)
#
# accuracy = (TP+TN) /(TP+FP+TN+FN)
# print('Accuracy of the binary classification = {:0.3f}'.format(accuracy))

# def helper():
#     return dict(zip(range(len(np.unique(labels))), np.unique(labels)))




# A Simple Confusion Matrix Implementation
def confusionmatrix(actual, predicted, labels=None, normalize=None):
    """
    Generate a confusion matrix for multiple classification
    @params:
        actual      - a list of integers or strings for known classes
        predicted   - a list of integers or strings for predicted classes
        normalize   - optional boolean for matrix normalization
    @return:
        matrix      - a 2-dimensional list of pairwise counts
    """
    # Get values by label
    unique = sorted(set(actual))
    matrix = [[0 for _ in unique] for _ in unique]
    imap   = {key: i for i, key in enumerate(unique)}

    # Generate Confusion Matrix
    for p, a in zip(actual, predicted):
        matrix[imap[p]][imap[a]] += 1

    # Matrix Normalization
    matrix = np.array(matrix)
    with np.errstate(all="ignore"):
        if normalize == "true":
            matrix_normalized = matrix / matrix.sum(axis=1, keepdims=True)
        elif normalize == "pred":
            matrix_normalized = matrix / matrix.sum(axis=0, keepdims=True)
        elif normalize == "all":
            matrix_normalized = matrix / matrix.sum()
        else:
            matrix_normalized = matrix
        matrix_normalized = np.nan_to_num(matrix_normalized)

    # Matrix Normalization
    # matrix = np.array(matrix)
    # matrix_normalized = np.zeros_like(matrix).astype(float)
    # if normalize == "true":
    #     sigma = np.sum(matrix, axis=1)
    #     for idx in range(len(unique)):
    #         matrix_normalized[idx, :] = 0.0 if sigma[idx] == 0 else matrix[idx, :] / sigma[idx]
    # elif normalize == "pred":
    #     sigma = np.sum(matrix, axis=0)
    #     for idx in range(len(unique)):
    #         matrix_normalized[:, idx] = 0.0 if sigma[idx] == 0 else matrix[:, idx] / sigma[idx]
    # elif normalize == "all":
    #     matrix_normalized = matrix / np.sum(matrix)
    # else:
    #     matrix_normalized = matrix

    # Get values by label
    if labels is None:
        return matrix_normalized
    elif isinstance(labels, (list, tuple, np.ndarray)):
        labels = list(labels)
        if np.all(np.isin(labels, unique)):
            matrix_final = [[0 for _ in labels] for _ in labels]
            imap_final = {key: i for i, key in enumerate(labels)}
            for label1 in labels:
                for label2 in labels:
                    matrix_final[imap_final[label1]][imap_final[label2]] = matrix_normalized[imap[label1]][imap[label2]]
            return np.array(matrix_final)
        else:
            print("All specified label should be in y_true!")
            exit(0)
    else:
        print("Labels should be a tuple / a list / a numpy array!")
        exit(0)



## simple test case

# tn, fp, fn, tp = confusion_matrix([0, 1, 0, 1], [1, 1, 1, 0]).ravel()
# print((tn, fp, fn, tp))
#
# tn, fp, fn, tp = confusionmatrix([0, 1, 0, 1], [1, 1, 1, 0]).ravel()
# print((tn, fp, fn, tp))


## First test case

# print("=====================1st test case=====================")
# y_true = np.array(["cat", "ant", "cat", "cat", "ant", "bird"])
# y_pred = np.array(["ant", "ant", "cat", "cat", "ant", "cat"])
# print(confusionmatrix(y_true, y_pred))
# print(confusion_matrix(y_true, y_pred))
#
# print("========")
#
# y_true = np.array([2, 0, 2, 2, 0, 1])
# y_pred = np.array([0, 0, 2, 2, 0, 2])
# print(confusionmatrix(y_true, y_pred))
# print(confusion_matrix(y_true, y_pred))



## Second test case

# print("=====================2nd test case=====================")
# y_true = np.array(["cat", "ant", "cat", "cat", "ant", "bird"])
# y_pred = np.array(["ant", "ant", "cat", "cat", "ant", "cat"])
#
# t1 = confusion_matrix(y_true, y_pred)
# t2 = confusion_matrix(y_true, y_pred, normalize='true')
# t3 = confusion_matrix(y_true, y_pred, normalize='pred')
# t4 = confusion_matrix(y_true, y_pred, normalize='all')
# print(f"t1: {t1}")
# print(f"t2: {t2}")
# print(f"t3: {t3}")
# print(f"t4: {t4}")
#
# print("=============")
#
# t1 = confusionmatrix(y_true, y_pred)
# t2 = confusionmatrix(y_true, y_pred, normalize='true')
# t3 = confusionmatrix(y_true, y_pred, normalize='pred')
# t4 = confusionmatrix(y_true, y_pred, normalize='all')
# print(f"t1: {t1}")
# print(f"t2: {t2}")
# print(f"t3: {t3}")
# print(f"t4: {t4}")


## 3rd test case

# print("=========================3rd test case======================")
#
# y_true = ["cat", "ant", "cat", "cat", "ant", "bird"]
# y_pred = ["ant", "ant", "cat", "cat", "ant", "cat"]
#
# t1 = confusion_matrix(y_true, y_pred, labels=["ant", "bird", "cat"])
# t2 = confusion_matrix(y_true, y_pred, labels=["cat", "bird", "ant"])
# t3 = confusion_matrix(y_true, y_pred, labels=["bird", "cat", "ant"])
# print(f"t1: {t1}")
# print(f"t2: {t2}")
# print(f"t3: {t3}")
#
# print("=============")
#
# t1 = confusionmatrix(y_true, y_pred, labels=["ant", "bird", "cat"])
# t2 = confusionmatrix(y_true, y_pred, labels=["cat", "bird", "ant"])
# t3 = confusionmatrix(y_true, y_pred, labels=["bird", "cat", "ant"])
# print(f"t1: {t1}")
# print(f"t2: {t2}")
# print(f"t3: {t3}")


print("=========================last test case======================")

y_true = ["cat", "ant", "cat", "cat", "ant", "bird"]
y_pred = ["ant", "ant", "cat", "cat", "ant", "cat"]

t1 = confusion_matrix(y_true, y_pred)
print(t1)

t1 = confusionmatrix(y_true, y_pred)
print(t1)















