import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn import svm

class MachineLearning:
    def __init__(self):
        pass

    def model_LogisticRegression(self, data, labelcol, ratio=0.3, randomseed=2022, showeva=False,savefilename='lg.pickle',modelsave = False,showeva2=False):
        # datacleanstart
        X = data[[x for x in data.columns if x != labelcol]].copy()
        y = data[labelcol].copy()

        le = LabelEncoder()
        for Xobj in list(X.dtypes[X.dtypes == object].keys()):
            X.loc[:, Xobj] = X.loc[:, Xobj].fillna('other')
            X.loc[:, Xobj] = le.fit_transform(X[Xobj].astype(str).values)
        for Xfloat in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xfloat] = X.loc[:, Xfloat].fillna(0)
        for Xint in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xint] = X.loc[:, Xint].fillna(0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=ratio, random_state=randomseed)

        # 标准化处理
        std = StandardScaler()
        X_train = std.fit_transform(X_train)
        X_test = std.transform(X_test)

        # le save
        pickle.dump(le, open('./temp.pkl', 'wb'))
        # datacleanend

        lg = LogisticRegression(C=1.0)
        lg.fit(X_train, y_train)
        y_predict = lg.predict(X_test)

        if modelsave is True:
            with open(savefilename, 'wb') as fw:
                pickle.dump(lg, fw)


        if showeva is True:
            print("logist回归系数为:\n", lg.coef_)

            print("预测值为:\n", y_predict)
            print("真实值与预测值比对:\n", y_predict == y_test)

            # rate = lg.score(X_test, y_test)
            # print("直接计算准确率为:\n", rate)
        else:
            pass
        if showeva2 is True:
            # 打印精确率、召回率、F1 系数以及该类占样本数
            labelsclass = list(set(y_train.tolist()))
            print("精确率与召回率为:\n", classification_report(y_test, y_predict, labels=labelsclass))
        print("AUCpredict值:", roc_auc_score(y_test, y_predict),"\n")

    def model_SVM(self, data, labelcol, ratio=0.3, randomseed=2022, showeva=False, savefilename='svm.pickle',modelsave = False,showeva2=False):

        # from sklearn import svm

        # datacleanstart
        X = data[[x for x in data.columns if x != labelcol]].copy()
        y = data[labelcol].copy()

        le = LabelEncoder()
        for Xobj in list(X.dtypes[X.dtypes == object].keys()):
            X.loc[:, Xobj] = X.loc[:, Xobj].fillna('other')
            X.loc[:, Xobj] = le.fit_transform(X[Xobj].astype(str).values)
        for Xfloat in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xfloat] = X.loc[:, Xfloat].fillna(0)
        for Xint in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xint] = X.loc[:, Xint].fillna(0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=ratio, random_state=randomseed)

        # 标准化处理
        std = StandardScaler()
        X_train = std.fit_transform(X_train)
        X_test = std.transform(X_test)

        # le save
        pickle.dump(le, open('./temp.pkl', 'wb'))
        # datacleanend

        SVM = svm.SVC(gamma='auto', C=1.0, decision_function_shape='ovr', kernel='rbf')
        SVM.fit(X_train, y_train)
        y_predict = SVM.predict(X_test)

        if modelsave is True:
            with open(savefilename, 'wb') as fw:
                pickle.dump(SVM, fw)

        if showeva is True:
            print("预测值为:\n", y_predict)
            print("真实值与预测值比对:\n", y_predict == y_test)

            # rate = lg.score(X_test, y_test)
            # print("直接计算准确率为:\n", rate)
        else:
            pass

        if showeva2 is True:
            # 打印精确率、召回率、F1 系数以及该类占样本数
            labelsclass = list(set(y_train.tolist()))
            print("精确率与召回率为:\n", classification_report(y_test, y_predict, labels=labelsclass))
        print("AUCpredict值:", roc_auc_score(y_test, y_predict),"\n")

    def model_DecisionTree(self, data, labelcol, ratio=0.3, randomseed=2022, showeva=False, savefilename='dt.pickle',modelsave = False,showeva2=False):



        # datacleanstart
        X = data[[x for x in data.columns if x != labelcol]].copy()
        y = data[labelcol].copy()

        le = LabelEncoder()
        for Xobj in list(X.dtypes[X.dtypes == object].keys()):
            X.loc[:, Xobj] = X.loc[:, Xobj].fillna('other')
            X.loc[:, Xobj] = le.fit_transform(X[Xobj].astype(str).values)
        for Xfloat in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xfloat] = X.loc[:, Xfloat].fillna(0)
        for Xint in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xint] = X.loc[:, Xint].fillna(0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=ratio, random_state=randomseed)

        # 标准化处理
        std = StandardScaler()
        X_train = std.fit_transform(X_train)
        X_test = std.transform(X_test)

        # le save
        pickle.dump(le, open('./temp.pkl', 'wb'))
        # datacleanend

        DT = DecisionTreeClassifier()
        DT.fit(X_train, y_train)
        y_predict = DT.predict(X_test)

        if modelsave is True:
            with open(savefilename, 'wb') as fw:
                pickle.dump(DT, fw)

        if showeva is True:
            print("预测值为:\n", y_predict)
            print("真实值与预测值比对:\n", y_predict == y_test)

            # rate = lg.score(X_test, y_test)
            # print("直接计算准确率为:\n", rate)
        else:
            pass

        if showeva2 is True:
            # 打印精确率、召回率、F1 系数以及该类占样本数
            labelsclass = list(set(y_train.tolist()))
            print("精确率与召回率为:\n", classification_report(y_test, y_predict, labels=labelsclass))
        print("AUCpredict值:", roc_auc_score(y_test, y_predict),"\n")


    def model_RandomForest(self, data, labelcol, ratio=0.3, randomseed=2022, showeva=False, savefilename='rf.pickle',modelsave = False,showeva2=False):

        # datacleanstart
        X = data[[x for x in data.columns if x != labelcol]].copy()
        y = data[labelcol].copy()

        le = LabelEncoder()
        for Xobj in list(X.dtypes[X.dtypes == object].keys()):
            X.loc[:, Xobj] = X.loc[:, Xobj].fillna('other')
            X.loc[:, Xobj] = le.fit_transform(X[Xobj].astype(str).values)
        for Xfloat in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xfloat] = X.loc[:, Xfloat].fillna(0)
        for Xint in list(X.dtypes[X.dtypes == float].keys()):
            X.loc[:, Xint] = X.loc[:, Xint].fillna(0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=ratio, random_state=randomseed)

        # 标准化处理
        std = StandardScaler()
        X_train = std.fit_transform(X_train)
        X_test = std.transform(X_test)

        # le save
        pickle.dump(le, open('./temp.pkl', 'wb'))
        # datacleanend

        RF = RandomForestClassifier()
        RF.fit(X_train, y_train)
        y_predict = RF.predict(X_test)

        if modelsave is True:
            with open(savefilename, 'wb') as fw:
                pickle.dump(RF, fw)

        if showeva is True:
            print("预测值为:\n", y_predict)
            print("真实值与预测值比对:\n", y_predict == y_test)

            # rate = lg.score(X_test, y_test)
            # print("直接计算准确率为:\n", rate)
        else:
            pass

        if showeva2 is True:
            # 打印精确率、召回率、F1 系数以及该类占样本数
            labelsclass = list(set(y_train.tolist()))
            print("精确率与召回率为:\n", classification_report(y_test, y_predict, labels=labelsclass))
        print("AUCpredict值:", roc_auc_score(y_test, y_predict),"\n")


    def model_XGBoost(self):
        pass


#
def easy_output(input, labelcol):
    ML = MachineLearning()
    print('Model LogisticRegression AUC:')
    ML.model_LogisticRegression(input, labelcol)
    print('Model SVM AUC:')
    ML.model_SVM(input, labelcol)
    print('Model DT AUC:')
    ML.model_DecisionTree(input, labelcol)
    print('Model RF AUC:')
    ML.model_RandomForest(input, labelcol)

