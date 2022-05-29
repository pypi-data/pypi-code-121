from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn import metrics
import numpy as np

def dbscan(x):
    NN=NearestNeighbors(n_neighbors=5).fit(x)
    distance, indice = NN.kneighbors(x)
    eps = distance.max()
    min_samples = x.ndim*2
    silhouette = np.array([])
    model = DBSCAN(eps=eps, min_samples=min_samples).fit(x)
    label = model.labels_
    silhouette=np.append(silhouette, metrics.silhouette_score(x, label))

    if silhouette < 0:
        print('''
        The score of clustring is {}%
        Datapoints have been assigned to the wrong clusters.
        You should consider preprocessing and dataset cleaning.
        and the parameters are:
        '''.format(round(silhouette[0]*100, 2)))
        print('epsilon: ',eps)
        print('number of samples: ',min_samples)
    elif silhouette >= 0 and silhouette < 0.1:
        print('''
        The score of clustring is {}%
        ""overlapping clusters""
        You should consider preprocessing.
        and the parameters are:
        '''.format(round(silhouette[0]*100, 2)))
        print('epsilon: ',eps)
        print('Optimal number of samples: ',min_samples)
    elif silhouette > 0.1 and silhouette < 0.5:
        print('''
        The score of clustring is {}%.
        Datapoints has been approximately assigned to the right clusters.
        and the parameters are:
        '''.format(round(silhouette[0]*100, 2)))
        print('Best epsilon: ',eps)
        print('Optimal number of samples: ',min_samples)
    elif silhouette >= 0.5:
        print('''
        The score of clustring is {}%.
        Good clustering.
        and the parameters are:
        '''.format(round(silhouette[0]*100, 2)))
        print('Best epsilon: ',eps)
        print('Optimal number of samples: ',min_samples)
