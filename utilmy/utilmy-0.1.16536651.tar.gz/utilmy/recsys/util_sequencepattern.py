# -*- coding: utf-8 -*-
MNAME = "utilmy.recsys.util_sequencepattern"
""" utils for sequential pattern discovery




"""
import os,sys, collections, random, numpy as np,  glob, pandas as pd
from box import Box
from copy import deepcopy
from tqdm import tqdm


## for plotting
import matplotlib.pyplot as plt
import seaborn as sns



######## Logger #############################################################################
from utilmy import log, log2, help_create
def help():
    print( help_create(MNAME) )


####### Tests ###############################################################################
def test_all():
    log(MNAME)
    test1()
    # test2()



def test1():
    pass


#############################################################################################
###########  Core ###########################################################################

def pd_get_sequence_patterns(df:pd.DataFrame, col_itemid:str, col_price:str, min_freq:int=2, price_min:int=None, price_max:int=None, sep=","):
    """
       Seq2Pat (AAAI'22) is a research library for sequence-to-pattern generation to discover sequential patterns 

    pip install seq2pat
    https://github.com/fidelity/seq2pat

    Average: This constraint specifies the average value of an attribute across all events in a pattern.
    Gap: This constraint specifies the difference between the attribute values of every two consecutive events in a pattern.
    Median: This constraint specifies the median value of an attribute across all events in a pattern.
    Span: This constraint specifies the difference between the maximum and the minimum value of an attribute across all events in a pattern.


    # Example to show how to find frequent sequential patterns from a given sequence database subject to constraints

    # Seq2Pat over 3 sequences
    seq2pat = Seq2Pat(sequences=[["A", "A", "B", "A", "D"],
                                ["C", "B", "A"],
                                ["C", "A", "C", "D"]])

    # Price attribute corresponding to each item
    price = Attribute(values=[[5, 5, 3, 8, 2],
                              [1, 3, 3],
                              [4, 5, 2, 1]])

    # Average price constraint
    seq2pat.add_constraint(3 <= price.average() <= 4)

    # Patterns that occur at least twice (A-D)
    patterns = seq2pat.get_patterns(min_frequency=2)

    """
    from sequential.seq2pat import Seq2Pat, Attribute
    sequences = df[col_itemid].values
    if  isinstance( sequences[0] , str):
      sequences = [ s.split(sep)) for s in sequences ]

    prices = df[col_price].values
    if  isinstance( prices[0] , str):
      prices = [ s.split(sep) for s in prices ]
    
    seq2pat  = Seq2Pat(sequences= sequences)

    if price_min is not None :
       seq2pat.add_constraint(price_min <= price.average() <= price_max )

    patterns = seq2pat.get_patterns(min_frequency= min_freq)
    return patterns




if 'utils':

    def pd_train_test_split(df, y, test_size=0.3, shuffle=False):
        '''
        Split the dataframe into train / test
        '''
        dtf_train, dtf_test = model_selection.train_test_split(df, test_size=test_size, shuffle=shuffle)
        print("X_train shape:", dtf_train.drop(y, axis=1).shape, "| X_test shape:", dtf_test.drop(y, axis=1).shape)
        print("y:")
        for i in dtf_train["y"].value_counts(normalize=True).index:
            print(" ", i, " -->  train:", round(dtf_train["y"].value_counts(normalize=True).loc[i], 2),
                              "| test:", round(dtf_test["y"].value_counts(normalize=True).loc[i], 2))
        print(dtf_train.shape[1], "features:", dtf_train.drop(y, axis=1).columns.to_list())
        return dtf_train, dtf_test



    def pd_colstring_encode(df, column):
        '''
        Transform an array of strings into an array of int.
        '''
        df[column+"_id"] = df[column].factorize(sort=True)[0]
        dic_class_mapping = dict( df[[column+"_id",column]].drop_duplicates().sort_values(column+"_id").values )
        return df, dic_class_mapping



    def metric_classifier_multilabel_show(y_test, predicted, predicted_prob, figsize=(15,5)):
        '''
        Evaluates a model performance.
        Doc::

            y_test: array
            predicted: array
            predicted_prob: array
            figsize: tuple - plot setting
        '''
        classes = np.unique(y_test)
        y_test_array = pd.get_dummies(y_test, drop_first=False).values

        ## Accuracy, Precision, Recall
        accuracy = metrics.accuracy_score(y_test, predicted)
        auc = metrics.roc_auc_score(y_test, predicted_prob, multi_class="ovr")
        print("Accuracy:",  round(accuracy,2))
        print("Auc:", round(auc,2))
        print("Detail:")
        print(metrics.classification_report(y_test, predicted))

        ## Plot confusion matrix
        cm = metrics.confusion_matrix(y_test, predicted)
        fig, ax = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', ax=ax, cmap=plt.cm.Blues, cbar=False)
        ax.set(xlabel="Pred", ylabel="True", xticklabels=classes, yticklabels=classes, title="Confusion matrix")
        plt.yticks(rotation=0)

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=figsize)
        ## Plot roc
        for i in range(len(classes)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test_array[:,i], predicted_prob[:,i])
            ax[0].plot(fpr, tpr, lw=3, label='{0} (area={1:0.2f})'.format(classes[i], metrics.auc(fpr, tpr)))
        ax[0].plot([0,1], [0,1], color='navy', lw=3, linestyle='--')
        ax[0].set(xlim=[-0.05,1.0], ylim=[0.0,1.05], xlabel='False Positive Rate',
                  ylabel="True Positive Rate (Recall)", title="Receiver operating characteristic")
        ax[0].legend(loc="lower right")
        ax[0].grid(True)

        ## Plot precision-recall curve
        for i in range(len(classes)):
            precision, recall, thresholds = metrics.precision_recall_curve(y_test_array[:,i], predicted_prob[:,i])
            ax[1].plot(recall, precision, lw=3, label='{0} (area={1:0.2f})'.format(classes[i], metrics.auc(recall, precision)))
        ax[1].set(xlim=[0.0,1.05], ylim=[0.0,1.05], xlabel='Recall', ylabel="Precision", title="Precision-Recall curve")
        ax[1].legend(loc="best")
        ax[1].grid(True)
        plt.show()




###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()
=======
# -*- coding: utf-8 -*-
MNAME = "utilmy.recsys.util_sequencepattern"
HELP = """ utils for sequential pattern discovery




"""
import os,sys, collections, random, numpy as np,  glob, pandas as pd
from box import Box
from copy import deepcopy
from tqdm import tqdm


## for plotting
import matplotlib.pyplot as plt
import seaborn as sns



######## Logger #############################################################################
from utilmy import log, log2, help_create
def help():
    print( HELP + help_create(MNAME) )


####### Tests ###############################################################################
def test_all():
    log(MNAME)
    test1()
    # test2()



def test1():
    pass


#############################################################################################
###########  Core ###########################################################################

def pd_get_sequence_patterns(df:pd.DataFrame, col_itemid:str, col_price:str, min_freq:int=2, price_min:int=None, price_max:int=None, sep=","):
    """
       Seq2Pat (AAAI'22) is a research library for sequence-to-pattern generation to discover sequential patterns 

    pip install seq2pat
    https://github.com/fidelity/seq2pat

    Average: This constraint specifies the average value of an attribute across all events in a pattern.
    Gap: This constraint specifies the difference between the attribute values of every two consecutive events in a pattern.
    Median: This constraint specifies the median value of an attribute across all events in a pattern.
    Span: This constraint specifies the difference between the maximum and the minimum value of an attribute across all events in a pattern.


    # Example to show how to find frequent sequential patterns from a given sequence database subject to constraints

    # Seq2Pat over 3 sequences
    seq2pat = Seq2Pat(sequences=[["A", "A", "B", "A", "D"],
                                ["C", "B", "A"],
                                ["C", "A", "C", "D"]])

    # Price attribute corresponding to each item
    price = Attribute(values=[[5, 5, 3, 8, 2],
                              [1, 3, 3],
                              [4, 5, 2, 1]])

    # Average price constraint
    seq2pat.add_constraint(3 <= price.average() <= 4)

    # Patterns that occur at least twice (A-D)
    patterns = seq2pat.get_patterns(min_frequency=2)

    """
    from sequential.seq2pat import Seq2Pat, Attribute
    sequences = df[col_itemid].values
    if  isinstance( sequences[0] , str):
      sequences = [ s.split(sep)) for s in sequences ]

    prices = df[col_price].values
    if  isinstance( prices[0] , str):
      prices = [ s.split(sep) for s in prices ]
    
    seq2pat  = Seq2Pat(sequences= sequences)

    if price_min is not None :
       seq2pat.add_constraint(price_min <= price.average() <= price_max )

    patterns = seq2pat.get_patterns(min_frequency= min_freq)
    return patterns




if 'utils':

    def pd_train_test_split(df, y, test_size=0.3, shuffle=False):
        '''
        Split the dataframe into train / test
        '''
        dtf_train, dtf_test = model_selection.train_test_split(df, test_size=test_size, shuffle=shuffle)
        print("X_train shape:", dtf_train.drop(y, axis=1).shape, "| X_test shape:", dtf_test.drop(y, axis=1).shape)
        print("y:")
        for i in dtf_train["y"].value_counts(normalize=True).index:
            print(" ", i, " -->  train:", round(dtf_train["y"].value_counts(normalize=True).loc[i], 2),
                              "| test:", round(dtf_test["y"].value_counts(normalize=True).loc[i], 2))
        print(dtf_train.shape[1], "features:", dtf_train.drop(y, axis=1).columns.to_list())
        return dtf_train, dtf_test



    def pd_colstring_encode(df, column):
        '''
        Transform an array of strings into an array of int.
        '''
        df[column+"_id"] = df[column].factorize(sort=True)[0]
        dic_class_mapping = dict( df[[column+"_id",column]].drop_duplicates().sort_values(column+"_id").values )
        return df, dic_class_mapping



    def metric_classifier_multilabel_show(y_test, predicted, predicted_prob, figsize=(15,5)):
        '''
        Evaluates a model performance.
        :parameter
            :param y_test: array
            :param predicted: array
            :param predicted_prob: array
            :param figsize: tuple - plot setting
        '''
        classes = np.unique(y_test)
        y_test_array = pd.get_dummies(y_test, drop_first=False).values

        ## Accuracy, Precision, Recall
        accuracy = metrics.accuracy_score(y_test, predicted)
        auc = metrics.roc_auc_score(y_test, predicted_prob, multi_class="ovr")
        print("Accuracy:",  round(accuracy,2))
        print("Auc:", round(auc,2))
        print("Detail:")
        print(metrics.classification_report(y_test, predicted))

        ## Plot confusion matrix
        cm = metrics.confusion_matrix(y_test, predicted)
        fig, ax = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', ax=ax, cmap=plt.cm.Blues, cbar=False)
        ax.set(xlabel="Pred", ylabel="True", xticklabels=classes, yticklabels=classes, title="Confusion matrix")
        plt.yticks(rotation=0)

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=figsize)
        ## Plot roc
        for i in range(len(classes)):
            fpr, tpr, thresholds = metrics.roc_curve(y_test_array[:,i], predicted_prob[:,i])
            ax[0].plot(fpr, tpr, lw=3, label='{0} (area={1:0.2f})'.format(classes[i], metrics.auc(fpr, tpr)))
        ax[0].plot([0,1], [0,1], color='navy', lw=3, linestyle='--')
        ax[0].set(xlim=[-0.05,1.0], ylim=[0.0,1.05], xlabel='False Positive Rate',
                  ylabel="True Positive Rate (Recall)", title="Receiver operating characteristic")
        ax[0].legend(loc="lower right")
        ax[0].grid(True)

        ## Plot precision-recall curve
        for i in range(len(classes)):
            precision, recall, thresholds = metrics.precision_recall_curve(y_test_array[:,i], predicted_prob[:,i])
            ax[1].plot(recall, precision, lw=3, label='{0} (area={1:0.2f})'.format(classes[i], metrics.auc(recall, precision)))
        ax[1].set(xlim=[0.0,1.05], ylim=[0.0,1.05], xlabel='Recall', ylabel="Precision", title="Precision-Recall curve")
        ax[1].legend(loc="best")
        ax[1].grid(True)
        plt.show()




###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()
