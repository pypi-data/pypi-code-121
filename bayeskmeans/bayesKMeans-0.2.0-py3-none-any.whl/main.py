from bayeskmeans.bayes_kmeans import BayesKMeans
from bayeskmeans.bayes_visualize import BayesKMeansVisualize

from sklearn.datasets import make_blobs

'''
if __name__ == '__main__':
    data = make_blobs(n_samples=5000, n_features=2, centers=127, cluster_std=4, center_box=(-300, 300))
    data = data[0]
    bayesKMeans = BayesKMeans(data)
    bayesKMeans.findK()
    print(bayesKMeans.foundK)

    visual = BayesKMeansVisualize(bayesKMeans)
    visual.showBayesianPlot()
'''


def test():
    data = make_blobs(n_samples=5000, n_features=2, centers=127, cluster_std=4, center_box=(-300, 300))
    data = data[0]
    bayesKMeans = BayesKMeans(data)
    bayesKMeans.find_k()
    print(bayesKMeans.found_k)

    visual = BayesKMeansVisualize(bayesKMeans)
    visual.show_bayesian_plot()
