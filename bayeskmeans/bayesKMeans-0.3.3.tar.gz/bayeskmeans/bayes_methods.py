from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score
import numpy as np


class BayesKMeansMethods(object):
    def __init__(self, data, random_state=2022):
        self.data = data
        self.random_state = random_state
        self.function = self.score_function

    def set_score_function(self, function):
        self.function = function

    def silhouette(self, data, predicts):
        return 1 - silhouette_score(self.data, predicts)

    def davies_bouldin(self, data, predicts):
        return davies_bouldin_score(self.data, predicts)

    def score_function(self, n, predicts=None):
        if predicts is not None:
            preds = predicts
        else:
            model = KMeans(n_clusters=n[0], random_state=self.random_state)
            preds = model.fit_predict(np.array(self.data))
        return self.function(self.data, preds)
