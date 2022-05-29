import pickle

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn import svm
from sklearn import linear_model


class MachineLearning:
    def __init__(self):
        pass

    def dataclean(self, data, labelcol, ratio=0.3, randomseed=2022, stand=True):
        # datacleanstart
        X = data[[x for x in data.columns if x != labelcol]].copy()
        y = data[labelcol].copy()

        # fillna
        for Xfloat in list(X.dtypes[X.dtypes == float].keys()):
            meanval = X[Xfloat].mean()
            X[Xfloat].fillna(meanval, inplace=True)

        le = LabelEncoder()
        for Xobj in list(X.dtypes[X.dtypes == object].keys()):
            X.loc[:, Xobj] = X.loc[:, Xobj].fillna('other')
            X.loc[:, Xobj] = le.fit_transform(X[Xobj].astype(str).values)
        for Xfloat in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xfloat] = X.loc[:, Xfloat].fillna(0)
        for Xint in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xint] = X.loc[:, Xint].fillna(0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=ratio, random_state=randomseed)

        if stand is True:
            # 标准化处理
            std = StandardScaler()
            X_train = std.fit_transform(X_train)
            X_test = std.transform(X_test)

        return X_train, X_test, y_train, y_test

    def model_LogisticRegression(self, X_train, X_test, y_train, y_test):
        lg = LogisticRegression(C=1.0)
        lg.fit(X_train, y_train)
        y_predict = lg.predict(X_test)
        return y_predict, y_test

    def model_SVM(self, X_train, X_test, y_train, y_test):
        SVM = svm.SVC(gamma='auto', C=1.0, decision_function_shape='ovr', kernel='rbf')
        SVM.fit(X_train, y_train)
        y_predict = SVM.predict(X_test)
        return y_predict, y_test

    def model_DecisionTree(self, X_train, X_test, y_train, y_test):
        DT = DecisionTreeClassifier()
        DT.fit(X_train, y_train)
        y_predict = DT.predict(X_test)
        return y_predict, y_test

    def model_RandomForest(self, X_train, X_test, y_train, y_test):
        RF = RandomForestClassifier()
        RF.fit(X_train, y_train)
        y_predict = RF.predict(X_test)
        return y_predict, y_test

    def model_LinearRegression(self, X_train, X_test, y_train, y_test):
        Linear = linear_model.LinearRegression(fit_intercept=False)
        Linear.fit(X_train, y_train)
        y_predict = Linear.predict(X_test)
        return y_predict, y_test

    def auc(self, y_test, y_predict, report=False):
        if report is True:
            labelsclass = list(set(y_test.tolist()))
            print("精确率与召回率为:\n", classification_report(y_test, y_predict, labels=labelsclass))
        return roc_auc_score(y_test, y_predict)

    def easyauc_output(self, data, labelcol):
        ML = MachineLearning()
        X_train, X_test, y_train, y_test = ML.dataclean(data, labelcol)
        y_predict, y_test = ML.model_LogisticRegression(X_train, X_test, y_train, y_test)
        print('model_LogisticRegression:', ML.auc(y_predict, y_test))
        y_predict, y_test = ML.model_SVM(X_train, X_test, y_train, y_test)
        print('model_SVM:', ML.auc(y_predict, y_test))
        y_predict, y_test = ML.model_RandomForest(X_train, X_test, y_train, y_test)
        print('model_RandomForest:', ML.auc(y_predict, y_test))
        y_predict, y_test = ML.model_DecisionTree(X_train, X_test, y_train, y_test)
        print('model_DecisionTree:', ML.auc(y_predict, y_test))
