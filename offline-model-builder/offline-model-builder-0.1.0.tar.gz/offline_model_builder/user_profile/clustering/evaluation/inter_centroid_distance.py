from offline_model_builder.user_profile.clustering.evaluation.constants import NPZ_EXTENSION, \
    CENTROIDS_IR1_PATH, NON_FEATURES, EVAL_SCORES_IR2_PATH, \
    INTER_CENTROID_SCORE_LABEL, ROOT_PATH, LOGGING_INTERCENTROIDDISTANCE
from offline_model_builder.user_profile.clustering.evaluation.utils import EvaluationUtils
from offline_model_builder.user_profile.constants import INTERMEDIATE_RESULTS_DIRECTORY, \
    CUSTOMER_ID, BIRCH_ENSEMBLE_FEATURE
from pandas import DataFrame, read_csv
from numpy import savez, array
import logging
logging.basicConfig(level=logging.INFO)

class InterCentroidDistance(EvaluationUtils):

    def __init__(
            self,
            data=DataFrame
    ):
        """
        Inherits the utils class to forward
        clustering results
        :param data: clustering results
        """
        EvaluationUtils.__init__(
            self,
            data=data
        )

    def find_all_centroids(
            self,
            features: array,
            method: array,
            method_name: str
    ) -> dict:
        """
        Find centroids for all the clusters
        for a given clustering method. This
        result is returned from function and
        saved as an intermediate result as well.
        :param features: feature vectors
        :param method: cluster labels vector
        :param method_name: clustering algorithm
        :return: {cluster: centroid} mapping
        """
        unique_cluster_labels = \
            self.get_unique_cluster_labels(
            method
        )
        centroids = self.get_centroids(
            features, method,
            unique_cluster_labels)
        return centroids

    def get_centroids(
            self,
            features: array,
            method: array,
            unique_cluster_labels: array
    ) -> dict:
        """
        Calculate centroids for all clusters
        :param features: feature vectors
        :param method: cluster labels vector
        :param unique_cluster_labels: vector
        of unique cluster labels
        :return: {cluster: centroid} mapping
        """
        centroids = {}
        for label in unique_cluster_labels:
            indices = self.get_indices(method, label)
            label_features = features[indices]
            label_features = label_features.astype(float)
            centroid = self.calculate_centroid(
                label_features
            )
            centroids[str(label)] = centroid
        return centroids

    def mean_inter_centroid_distance(
            self,
            centroids: list
    ) -> float:
        """
        Calculates average inter centroid
        distance among all the clusters
        :param centroids: cluster centroids
        :return: centroid score
        """
        centroid_count = len(centroids)
        centroid_sum = []
        for index1 in range(centroid_count):
            centroid_distance = 0
            for index2 in range(centroid_count):
                centroid_distance += self.get_distance(
                    centroids[index1],
                    centroids[index2]
                )
            # dividing by centroid_count - 1
            # as one node is considered one itself,
            # so its euclidean distance is zero
            centroid_sum.append(
                centroid_distance / (centroid_count - 1)
            )
        return sum(centroid_sum) / len(centroid_sum)

    def controller(
            self
    ) -> dict:
        """
        Driver function for computing average
        inter-centroid distance score
        :return: final scores for each
        clustering method
        """
        NON_FEATURES.remove(CUSTOMER_ID)
        NON_FEATURES.append(BIRCH_ENSEMBLE_FEATURE)
        scores = {}
        for method in NON_FEATURES:
            centroids = self.find_all_centroids(
                self.features.to_numpy(),
                self.data[method].to_numpy(),
                method
            )
            score = self.mean_inter_centroid_distance(
                list(centroids.values())
            )
            scores[method] = score
        self.save_intermediate_results(
            subdirectory=EVAL_SCORES_IR2_PATH,
            filename=INTER_CENTROID_SCORE_LABEL,
            result=scores
        )
        return scores

if __name__ == '__main__':
    data = read_csv(ROOT_PATH+"all_clusters.csv")
    icd = InterCentroidDistance(data=data)
    icd.retrieve_ensemble_results()
    icd.merge_ensemble_results()

    logging.info(LOGGING_INTERCENTROIDDISTANCE)
    icd.controller()
