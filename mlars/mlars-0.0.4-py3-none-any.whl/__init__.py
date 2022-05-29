import pandas as pd
import numpy as np
from colorama import Fore, Back, Style
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn import datasets, metrics, neighbors,  linear_model, svm
from mlars.getData import clearData, getData
from mlars.models import new_func

models = new_func()
# from xgboost import XGBClassifier
# ["XGBoost", XGBClassifier]


def t_main(df, name: str):
    df = clearData(df)
    unique = df[name].unique()
    print(Fore.YELLOW + "starting with dataframe of shape: {} {}".format(df.shape[0], df.shape[1])
          + "\nand the column is:", name
          + "\nwith {0} unique values , {1} and {2}".format(len(unique), unique[0], unique[1]))
    data = getData(df, name, unique)
    print(Fore.GREEN + "train test split done test size: {}".format(0.2))
    print(Fore.YELLOW + "training model")
    print(Fore.YELLOW +
          "new shape of train data: {} {}".format(data[0].shape[0], data[0].shape[1]))
    first_bestaccuracy = 0
    first_bestmodel = None
    second_bestaccuracy = 0
    second_bestmodel = None
    thrid_bestaccuracy = 0
    thrid_bestmodel = None
    for item in models:
        for param in item[2][0]:
            try:
                print(Fore.CYAN + item[0], end=" ")
                model = getModel(data[0], data[2], item[1], param)
                y = getPredictions(model, data[1])
                accuracy = getAccuracy(data[3], y)
                print(Fore.GREEN + "accuracy: {}".format(accuracy))
                if accuracy > first_bestaccuracy:
                    second_bestaccuracy = first_bestaccuracy
                    second_bestmodel = first_bestmodel
                    first_bestaccuracy = accuracy
                    first_bestmodel = model
                elif accuracy > second_bestaccuracy:
                    second_bestaccuracy = accuracy
                    second_bestmodel = model
                elif accuracy > thrid_bestaccuracy:
                    thrid_bestaccuracy = accuracy
                    thrid_bestmodel = model
            except:
                print(Fore.RED + "This Algorithm is not working")
    print(Fore.GREEN + "best model is: {} with accuracy: {}".format(first_bestmodel, first_bestaccuracy))
    print(Fore.GREEN + "second best model is: {} with accuracy: {}".format(
        second_bestmodel, second_bestaccuracy))
    print(Fore.GREEN + "third best model is: {} with accuracy: {}".format(
        thrid_bestmodel, thrid_bestaccuracy))
    return {"first": first_bestmodel, "second": second_bestmodel, "thrid": thrid_bestmodel}


def main(df, name: str, min: int = 103, top3: bool = False):
    if top3:
        return t_main(df, name)
    df = clearData(df)
    unique = df[name].unique()
    print(Fore.YELLOW + "starting with dataframe of shape: {} {}".format(df.shape[0], df.shape[1])
          + "\nand the column is:", name
          + "\nwith {0} unique values , {1} and {2}".format(len(unique), unique[0], unique[1]))
    data = getData(df, name, unique)
    print(Fore.GREEN + "train test split done test size: {}".format(0.2))
    print(Fore.YELLOW + "training model")
    print(Fore.YELLOW +
          "new shape of train data: {} {}".format(data[0].shape[0], data[0].shape[1]))
    bestaccuracy = 0
    for item in models:
        for param in item[2][0]:
            try:
                print(Fore.CYAN + item[0], end=" ")
                model = getModel(data[0], data[2], item[1], param)
                y = getPredictions(model, data[1])
                accuracy = getAccuracy(data[3], y)
                if accuracy*100 >= min:
                    bestmodelname = item[0]
                    bestaccuracy = accuracy
                    print(Fore.YELLOW + "done")
                    print(
                        Fore.GREEN + "best model is : {} ,with accuracy  {}".format(bestmodelname, bestaccuracy))
                    bestmodel = model
                    return bestmodel
                if accuracy > bestaccuracy:
                    bestaccuracy = accuracy
                    bestmodelname = item[0]
                    bestmodel = model
            except:
                print(Fore.BLUE + "This Algorithm is not supported")
    print(Fore.YELLOW + "done")
    print(Fore.GREEN + "best model is : {} ,with accuracy  {}".format(bestmodelname, bestaccuracy))
    return bestmodel


def getModel(X_train, y_train, Model, param):
    model = Model(param)
    model.fit(X_train, y_train)
    print(Fore.WHITE + "model fit done with params " + str(param), end=' ')
    return model


def getPredictions(model, X_test):
    predictions = model.predict(X_test)
    # print(Fore.GREEN + "predictions done")
    return predictions


def getAccuracy(y_test, predictions):
    accuracy = accuracy_score(y_test, predictions)
    print(Fore.BLUE + str(accuracy))
    return accuracy
