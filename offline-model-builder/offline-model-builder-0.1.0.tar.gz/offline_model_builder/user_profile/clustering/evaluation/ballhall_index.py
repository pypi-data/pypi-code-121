from offline_model_builder.user_profile.clustering.evaluation.constants import NON_FEATURES, \
    CENTROIDS_IR1_PATH, NPZ_EXTENSION, EVAL_SCORES_IR2_PATH, \
    BALLHALL_INDEX_LABEL, ROOT_PATH, LOGGING_BALLHALLINDEX
from offline_model_builder.user_profile.clustering.evaluation.utils import EvaluationUtils
from pandas import DataFrame, read_csv
from numpy import load, array
from offline_model_builder.user_profile.constants import CUSTOMER_ID, \
    INTERMEDIATE_RESULTS_DIRECTORY, BIRCH_ENSEMBLE_FEATURE
import logging
logging.basicConfig(level=logging.INFO)

class BallHallIndex(EvaluationUtils):

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

    def get_cluster_sum(
            self,
            centroid: array,
            label: str,
            method: str
    ) -> float:
        """
        Compute cluster sum by calculating
        distance of each point from its centroid
        :param centroid: centroid vector
        :param label: cluster label
        :param method: clustering method
        :return:
        """
        cluster_sum = 0
        indices = self.get_indices(
            self.data[method].to_numpy(),
            int(label)
        )
        cluster_features = (
            self.features.to_numpy()
        )[indices]

        for feature in cluster_features:
            cluster_sum += (self.get_distance(
                feature,
                centroid
            )) ** 2

        return cluster_sum

    def get_weighted_sum(
            self,
            centroids: dict,
            method: str,
            weights: dict
    ) -> float:
        """
        Calculate weighted sum by internally
        computing the cluster sum and computing
        its product with the cluster member count
        :param centroids: cluster centroids
        :param method: clustering method
        :param weights: {cluster_id: count}
        mapping
        :return:
        """
        weighted_sum = 0

        for label, centroid in centroids.items():
            cluster_sum = self.get_cluster_sum(
                centroid, label, method)

            weighted_sum += \
                cluster_sum / weights[int(label)]

        return weighted_sum

    def controller(
            self
    ):
        """
        Driver Function for calculating Dunn
        Validity Index
        :return: final scores for each
        clustering method
        """
        NON_FEATURES.remove(CUSTOMER_ID)
        NON_FEATURES.append(BIRCH_ENSEMBLE_FEATURE)
        scores = {}

        for method in NON_FEATURES:
            cluster_count = \
                self.get_unique_cluster_labels(
                    labels=self.data[method].to_numpy()
                )

            weights = self.compute_label_weights(
                labels=self.data[method]
            )

            centroids = load(
                INTERMEDIATE_RESULTS_DIRECTORY +
                "/" + CENTROIDS_IR1_PATH + "/" +
                method + NPZ_EXTENSION
            )

            weighted_sum = self.get_weighted_sum(
                centroids=centroids,
                method=method,
                weights=weights
            )

            scores[method] = \
                weighted_sum / len(cluster_count)

        self.save_intermediate_results(
            subdirectory=EVAL_SCORES_IR2_PATH,
            filename=BALLHALL_INDEX_LABEL,
            result=scores
        )

        return scores

if __name__ == '__main__':
    data = read_csv(ROOT_PATH+"all_clusters.csv")
    ballhall = BallHallIndex(data=data)
    ballhall.retrieve_ensemble_results()
    ballhall.merge_ensemble_results()

    logging.info(LOGGING_BALLHALLINDEX)
    ballhall.controller()