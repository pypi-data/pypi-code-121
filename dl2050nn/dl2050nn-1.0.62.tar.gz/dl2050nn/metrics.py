import math
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns


"""
    Precision:
        A measure of exactness.
        Out of those predicted positive, how many are actual positive.
        Good measure when the costs of False Positive is high (ex: email spam).

    Recall:
        A measure of a classifiers completeness.
        How many of the Actual Positives the model captured.
        Good measure when the costs of False Negatives is high (ex: fraud detection or sick patient detection).

    F1 Score (or F-score)
        A weighted average of precision and recall.
        Seek a balance between Precision and Recall when there is an uneven class (large number of Actual Negatives).
        Higher if both Precision and Recall are higher.

    Receiver Operating Characteristic (ROC)
        ROC curves feature true positive rate on the Y axis, and false positive rate on the X axis.
        Top left corner is the ideal point - a false positive rate of zero, and a true positive rate of one.
        A larger area under the curve (AUC) is better.
        The steepness of ROC curves is  important, to maximize the TPR while minimizing the FPR.

    Suppose a computer program for recognizing dogs in photographs identifies 8 dogs in a picture containing 12 dogs and
    some cats. Of the 8 dogs identified, 5 actually are dogs (true positives), while the rest are cats (false positives).
    The program's recal is 5/12 and the precision is 5/8.

"""


def accuracy(y2, y):
    y2 = torch.max(y2, dim=1)[1]
    return (y2==y).float().mean().item()

def recall(y2, y): # TPR = TP/P (same as sensitivity)
    y2 = torch.max(y2, dim=1)[1]
    tp = torch.mul((y2==y), y.byte()).sum().item()
    p = (y==1).sum().item()
    r = float(tp) / float(p) if p>0 else 0.0
    return r

def sensitivity(y2, y): # TPR = TP/P (same as recall)
    return recall(y2, y)

def specificity(y2, y): # TNR = TN/N
    y2 = torch.max(y2, dim=1)[1]
    tn = torch.mul((y2==y), y.byte()^1).sum().item()
    n = (y==0).sum().item()
    return tn/n if n>0 else 0.0

def precision(y2, y): # TP/(TP+FP)
    y2 = torch.max(y2, dim=1)[1]
    tp = torch.mul((y2==y), y.byte()).sum().item()
    p = (y2==1).sum().item()
    return tp/p if p>0 else 0.0

def accuracy2(y2, y, threshold=0.5):
    y2 = (y2 > threshold).byte()
    y = y.byte()
    return (y2==y).float().mean().item()

def precision2(y2, y, threshold=0.5):
    y2 = (y2 > threshold).byte()
    y = y.byte()
    tp = torch.mul((y2==y), y).sum().item()
    n = (y2==1).sum().item()
    r = float(tp) / float(n) if n>0 else 0.0
    return r

def recall2(y2, y, threshold=0.5):
    y2 = (y2 > threshold).byte()
    y = y.byte()
    tp = torch.mul((y2==y), y).sum().item()
    n = (y==1).sum().item()
    r = float(tp) / float(n) if n>0 else 0.0
    return r

def f1(y2, y):
    p = precision(y2, y)
    r = recall(y2, y)
    if p+r==0.0: return 0.0
    return 2*(p*r)/(p+r)

def f2(y2, y):
    p = precision2(y2, y)
    r = recall2(y2, y)
    return 2*(p*r)/(p+r)

def roc(y2, y): return roc_auc_score(y.cpu().numpy(), np.exp(y2.cpu().numpy()[:,1]))
def gini(y2, y): return 2 * roc(y2, y) - 1
def gini_normalized(y2, y): return gini(y2, y) / gini(y, y)

def gini1(y2, y, cmpcol=0, sortcol=1):
    #y2 = torch.max(y2, dim=1)[1].numpy()
    all = np.asarray(np.c_[ y, y2, np.arange(len(y)) ], dtype=np.float)
    all = all[ np.lexsort((all[:,2], -1*all[:,1])) ]
    totalLosses = all[:,0].sum()
    giniSum = all[:,0].cumsum().sum() / totalLosses
    giniSum -= (len(y) + 1) / 2.
    return giniSum / len(y)

def gini2(actual, pred):
    n = len(actual)
    a_s = actual[np.argsort(pred)]
    a_c = a_s.cumsum()
    giniSum = a_c.sum() / a_c[-1] - (n + 1) / 2.0
    return giniSum / n

def mse1(y2, y):
    return ((y - y2)**2).mean()

def exp_mse(y2, y):
    y = y.exp()
    y2 = y2.exp()
    return ((y - y2)**2).mean()

def exp_rmspe(y2, y):
    y = y.exp()
    y2 = y2.exp()
    r = (y - y2) / y
    return math.sqrt((r**2).mean())

def percent(y2, y):
    return ((y2 - y) / y).mean()

def exp_percent(y2, y):
    return ((y2.exp() - y.exp()).abs() / y.exp()).mean()
