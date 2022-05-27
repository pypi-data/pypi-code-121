

class tsne:
    """
    tsne class is the implementation of sklearn tsne
    it has two functions for applying tsne on image and mesh datasets
    and a function to show the result thorugh zetane and show the dataset"""


    def tsne(dataset, dataset_channels=3, n_components=2, perplexity=30, early_exaggeration=12.0, learning_rate=200.0, n_iter=1000, n_iter_without_progress=300, min_grad_norm=1e-7, metric="euclidean", init="random", verbose=0, random_state=None, method="barnes_hut", angle=0.5, n_jobs=None):
        """
        image funstion takes a dataset of images and send each image to zetane based on the position returned from tsne
        Args:
            dataset : {numpyArray} -- shape(n_samples , n_features)
            dataset_channels = {int} -- indicates the number of channels of each image , default = 3
            all TSNE arguments and their default values https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html

        Returns:
            tsne_results: {NumpyArray} -- shape(n_samples , n_components)
        """
        return None
