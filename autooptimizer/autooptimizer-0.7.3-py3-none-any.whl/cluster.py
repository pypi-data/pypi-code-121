from sklearn.cluster import DBSCAN, KMeans, MeanShift, estimate_bandwidth
from sklearn.neighbors import NearestNeighbors
from sklearn import metrics
import numpy as np

def kmeans(x):
    calinski_harabasz_score = np.array([])
    silhouette_score = np.array([])
    for i in range(2,12):
        model = KMeans(n_clusters=i).fit(x)
        label = model.labels_
        silhouette_score = np.append(silhouette_score, metrics.silhouette_score(x, label))
        calinski_harabasz_score = np.append(calinski_harabasz_score, metrics.calinski_harabasz_score(x, label))
    best_score = np.argmax(calinski_harabasz_score)
    best_proba = calinski_harabasz_score[best_score]
    return KMeans(n_clusters = best_score + 2)

def meanshift(x):
    bandwidth = estimate_bandwidth(x, quantile = 0.3, random_state = 2)
    model = MeanShift(bandwidth=bandwidth).fit(x)
    label = model.labels_
    silhouette = metrics.silhouette_score(x,label)
    return model

def dbscan(x):
    silhouette = []
    distances = []
    for i in range(2,10):
        NN = NearestNeighbors(n_neighbors=i).fit(x)
        distance, indice = NN.kneighbors(x)
        eps = distance.max()
        min_sample = x.shape[1] + 1
        model = DBSCAN(eps=eps, min_samples=min_sample).fit(x)
        label = model.labels_
        silhouette = np.append(silhouette, metrics.silhouette_score(x, label))
        distances = np.append(distances, eps)
    best_index = np.argmax(silhouette)
    best_eps = distances[best_index]
    return DBSCAN(eps=best_eps, min_samples=min_sample)
