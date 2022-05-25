from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn import metrics
import numpy as np

def meanshift(x):
    bandwidth = estimate_bandwidth(x,quantile=0.3, random_state=2)
    model = MeanShift(bandwidth=bandwidth).fit(x)
    label = model.labels_
    silhouette = metrics.silhouette_score(x, label)

    if silhouette < 0:
        print('''
        The score of clustring is {}%
        Datapoints have been assigned to the wrong clusters.
        You should consider preprocessing and dataset cleaning.
        and the parameters are:
        '''.format(round(silhouette*100, 2)))    
        print('the assigned bandwidth is: ', bandwidth)
    elif silhouette >= 0 and silhouette < 0.1:
        print('''
        The score of clustring is {}%.
        ""Overlapping clusters""
        You should consider preprocessing.
        and the parameters are:
        '''.format(round(silhouette*100, 2)))
        print('the assigned bandwidth is: ', bandwidth)
    elif silhouette > 0.1 and silhouette <= 0.5:
        print('''
        The score of clustring is {}%.
        Datapoints have been approximately assigned to the right clusters
        and the parameters are:
        '''.format(round(silhouette*100, 2)))
        print('the assigned bandwidth is: ', bandwidth)
    elif silhouette > 0.5:
        print('''
        The score of clustring is {}%.
        Good clustering
        and the parameters are:
        '''.format(round(silhouette*100, 2)))
        print('The assigned bandwidth is: ', bandwidth)
