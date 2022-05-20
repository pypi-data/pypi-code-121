import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
from bayeskmeans.bayes_kmeans import BayesKMeans


class BayesKMeansVisualize(object):
    def __init__(self, bayesKMeans: BayesKMeans):
        self.bayesKMeans = bayesKMeans

    def showData(self):
        plt.scatter(self.bayesKMeans.data[:, 0], self.bayesKMeans.data[:, 1])
        plt.show()

    def showColoredData(self):
        clusterer = KMeans(n_clusters=self.bayesKMeans.found_k, random_state=self.bayesKMeans.method.random_state)
        preds = clusterer.fit_predict(np.array(self.bayesKMeans.data))
        plt.scatter(self.bayesKMeans.data[:, 0], self.bayesKMeans.data[:, 1], c=preds)
        plt.show()

    def show_bayesian_plot(self, line=True):
        d = {}
        for i in range(len(self.bayesKMeans.x_iters)):
            d[self.bayesKMeans.x_iters[i]] = self.bayesKMeans.func_vals[i]

        x_asc = sorted(self.bayesKMeans.x_iters)
        y_asc = []
        for x in x_asc:
            y_asc.append(d[x])

        if line:
            plt.plot(x_asc, y_asc, label=self.bayesKMeans.method_name)

        plt.scatter(x_asc, y_asc, label=self.bayesKMeans.method_name + ' points', marker='x', s=15, c='green')
        plt.scatter(self.bayesKMeans.found_k, d[self.bayesKMeans.found_k], c='red', marker='+',
                    s=35, label='Target = ' + str(self.bayesKMeans.found_k))
        plt.xlabel('n_clusters')
        plt.ylabel('Score')
        plt.legend()
        plt.show()
