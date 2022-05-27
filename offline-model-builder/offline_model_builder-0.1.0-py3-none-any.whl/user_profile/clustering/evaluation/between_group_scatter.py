from pandas import DataFrame, read_csv
from numpy import subtract, array, linalg, load
from offline_model_builder.user_profile.clustering.evaluation.constants import \
    NPZ_EXTENSION, NON_FEATURES, CENTROIDS_IR1_PATH, \
    EVAL_SCORES_IR2_PATH, BETWEEN_GROUP_SCATTER_LABEL, \
    ROOT_PATH, LOGGING_BETWEENGROUPSCATTER
from offline_model_builder.user_profile.clustering.evaluation.utils import \
    EvaluationUtils
from offline_model_builder.user_profile.constants import CUSTOMER_ID, \
    INTERMEDIATE_RESULTS_DIRECTORY, BIRCH_ENSEMBLE_FEATURE
import logging
logging.basicConfig(level=logging.INFO)

class BetweenGroupScatter(EvaluationUtils):

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

    def compute_cluster_dispersion(
            self,
            centroids: dict,
            global_centroid: array,
            label_weights: dict
    ) -> float:
        """
        Calculate Dispersion between vectors
        :param centroids: centroid vectors
        :param global_centroid: global
        centroid vector
        :param label_weights: product
        weight term
        :return:
        """
        weighted_sum = 0
        for label, centroid in centroids.items():
            weight = label_weights[int(label)]
            # because Counter creates key of
            # integer type
            weighted_sum += (weight * (
                    linalg.norm(
                        subtract(
                            centroid,
                            global_centroid
                        )
                    ) ** 2))

        return weighted_sum

    def controller(
            self
    ):
        """
        Driver Function for Between Group
        Scatter Evaluation Score
        :return: final scores for each
        clustering method
        """
        NON_FEATURES.remove(CUSTOMER_ID)
        NON_FEATURES.append(BIRCH_ENSEMBLE_FEATURE)
        scores = {}

        for method in NON_FEATURES:
            label_weights = \
                self.compute_label_weights(
                    self.data[method]
                )

            # loading the centroids computed for
            # each method during calculation of
            # inter_centroid_distance
            centroids = load(
                INTERMEDIATE_RESULTS_DIRECTORY +
                "/" + CENTROIDS_IR1_PATH + "/" +
                method + NPZ_EXTENSION
            )

            global_centroid = \
                self.get_global_centroid(
                    centroids
                )

            scores[method] = \
                self.compute_cluster_dispersion(
                centroids,
                global_centroid,
                label_weights
            )

        self.save_intermediate_results(
            subdirectory=EVAL_SCORES_IR2_PATH,
            filename=BETWEEN_GROUP_SCATTER_LABEL,
            result=scores
        )
        return scores

if __name__ == '__main__':
    data = read_csv(ROOT_PATH+"all_clusters.csv")
    bg_scatter = BetweenGroupScatter(data=data)
    bg_scatter.retrieve_ensemble_results()
    bg_scatter.merge_ensemble_results()

    logging.info(LOGGING_BETWEENGROUPSCATTER)
    bg_scatter.controller()
