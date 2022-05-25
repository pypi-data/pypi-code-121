# pointMeasures.py
# Copyright 2020 André Carrington, Ottawa Hospital Research Institute
# Use is subject to the Apache 2.0 License
# Written by André Carrington
#
# def regression_point_measures(conf):
# #enddef

def classification_point_measures(conf, prevalence, costs):
    import numpy as np
    import warnings

    TN, FP, FN, TP     = conf.ravel()
    cTN, cFP, cFN, cTP = costs['cTN'], costs['cFP'], costs['cFN'], costs['cTP']
    neg_prevalence     = 1 - prevalence
    stat         = dict()
    stat['Sens'] = TP/(TP+FN)                          # Sensitivity, True Positive Rate, Recall
    stat['Spec'] = TN/(TN+FP)                          # Specificity, True Negative Rate, Selectivity
    stat['Rec']  = stat['Sens']

    warnings.filterwarnings('ignore')
    stat['PPV']  = TP/(TP+FP)                          # Positive Predictive Value, Precision
    stat['NPV']  = TN/(TN+FN)                          # Negative Predictive Value, Inverse Precision
    stat['Prec'] = stat['PPV']

    stat['Alpha']= FP/(FP+TN)                          # Alpha, Type I  Error, FPR
    stat['Beta'] = FN/(FN+TP)                          # Beta,  Type II Error, FNR
    stat['FPR']  = stat['Alpha']
    stat['FNR']  = stat['Beta']

    stat['FDR']  = FP/(FP+TP)                          # False Discovery Rate, Q
    stat['FOR']  = FN/(FN+TN)                          # False Omission Rate

    stat['Acc']  = (TP+TN)/(TP+TN+FP+FN)               # Accuracy
    stat['BAcc'] = (stat['Sens']+stat['Spec'])/0.5     # Balanced Accuracy
    stat['GAcc'] = (stat['Sens']*stat['Spec'])**0.5    # Geo-Mean Accuracy
    # from Metz, equation 6 in my NB paper
    stat['fixed_costs'] = prevalence * cFN + neg_prevalence * cTN
    stat['cwAcc']= prevalence * (cFN - cTP) * stat['Sens'] - neg_prevalence * (cFP - cTN) * stat['FPR'] \
                   - stat['fixed_costs'] \

    stat['BPV']  = (stat['PPV'] +stat['NPV'] )/0.5     # Balanced Predictive Value (new definition, previously was a geo-mean)
    stat['GPV']  = (stat['PPV'] *stat['NPV'] )**0.5    # Geo-Mean Balanced Predictive Value
    stat['MC']   = 1 - stat['Acc']                     # Misclassification Cost

    if (1-stat['Spec']) != 0:
        stat['LR+']  =     stat['Sens'] /(1-stat['Spec'])  # Likelihood Ratio Positive, Likelihood Ratio
    else:
        stat['LR+']  = np.inf
    #endif
    if stat['Spec'] != 0:
        stat['LR-']  =  (1-stat['Sens'])/   stat['Spec']   # Likelihood Ratio Negative
    else:
        stat['LR-']  = np.inf
    #endif
    if stat['LR-']  != 0:
        stat['OR']   = stat['LR+']  /   stat['LR-']    # Odds Ratio, Diagnostic Odds Ratio
    else:
        stat['OR']   = np.inf
    #endif

    stat['F1']   =  stat['PPV']*stat['Sens']           # F1 score, F1 measure
    #stat['F1']  =  2*(stat['Prec']*stat['Rec'])/(stat['Prec'] + stat['Rec'])

    stat['J']    = stat['Sens'] + stat['Spec'] - 1     # Youden's J statistic, Youden's index, Informedness
    stat['Infm'] = stat['J']                           # Bookmarker Informedness, DeltaP'

    stat['Mark'] = stat['PPV']  + stat['NPV']  - 1     # Markedness

    stat['MCC']  = (TP*TN - FP*FN) / ((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN)) # Matthew's Correlation Coefficient

    return stat
#enddef


def distance_point_to_line(qx, qy, px, py, m):
    import math
    import numpy as np

    # point p (px,py) and slope m define a line
    # query point q (qx,qy): how far is q from the line?
    if m == 0:
        # slope is zero (horizontal line), distance is vertical only
        return abs(qy-py)
        #raise ValueError('slope is zero')
    #endif
    if np.isinf(m):
        # slope is infinite (vertical line), distance is horizontal only
        return abs(qx-px)
        #raise ValueError('slope is infinite')
    #endif

    # line through p:            y =     m *(x-px)+py
    # perpendicular slope:            -1/m
    # perpendicular line from q: y = (-1/m)*(x-qx)+qy
    # equate both lines to find intersection at (x0,y0)
    x0 = (m*px - py + qx/m + qy) / (m + 1/m)
    # then find y_0 using first line definition
    y0 = m*(x0-px)  + py
    return math.sqrt( (qx-x0)**2 + (qy-y0)**2 )
#enddef

def optimal_ROC_point_indices(fpr, tpr, skew):
    import math
    import numpy as np

    n       = len(fpr)
    mindist = math.inf
    min_idx = []
    # define a line with slope skew passing through the top-left ROC point (x,y)=(0,1)
    # for each point in (fpr,tpr) get the distance from that point to the line
    for i in np.arange(0, n):
        d = distance_point_to_line(fpr[i], tpr[i], 0, 1, skew)
        #print(f'd: {d}')
        if   d == mindist:
            min_idx = min_idx + [i]
        elif d < mindist:
            mindist = d
            min_idx = [i]
        #endif
    #endif
    # now min_idx contains the indices for the point(s) with the minimum distance
    # return those indices for the optimal ROC points
    return min_idx
#enddef
