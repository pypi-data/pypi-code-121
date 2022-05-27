from pandas import DataFrame, concat, read_csv
from numpy import ones, min, linalg, zeros, max, array
from offline_model_builder.user_profile.clustering.evaluation.config import \
    DUNN_DELTA_INIT, DUNN_DELTA_DISTANCE_INIT
from offline_model_builder.user_profile.clustering.evaluation.constants import \
    NON_FEATURES, EVAL_SCORES_IR2_PATH, DUNN_INDEX_LABEL, ROOT_PATH, \
    LOGGING_DUNNINDEX
from offline_model_builder.user_profile.clustering.evaluation.utils import \
    EvaluationUtils
from offline_model_builder.user_profile.constants import CUSTOMER_ID, BIRCH_ENSEMBLE_FEATURE
import logging
logging.basicConfig(level=logging.INFO)


class DunnIndex(EvaluationUtils):

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

    def delta(
            self,
            feature1: array,
            feature2: array
    ):
        """
        Calculate the Euclidean Distance
        between two feature vectors belonging
        to different clusters.
        :param feature1: feature vector set
        from first cluster
        :param feature2: feature vector set
        from second cluster
        :return: Minimum Euclidean Distance
        """
        distance = ones(
            [len(feature1),
             len(feature2)]
            ) * \
            DUNN_DELTA_DISTANCE_INIT

        for i in range(0, len(feature1)):
            for j in range(0, len(feature2)):
                distance[i, j] = linalg.norm(
                    feature1[i] - feature2[j]
                )

        return min(distance)

    def big_delta(
            self,
            cluster_features: array
    ):
        """
        Calculate the Euclidean Distance
        between two feature vectors belonging
        to same clusters.
        :param cluster_features:
        :return:
        """
        size_features = len(cluster_features)
        distance = zeros(
            [size_features,
             size_features])

        for i in range(0, size_features):
            for j in range(0, size_features):
                if i > j:
                    continue
                distance[i, j] = linalg.norm(
                    cluster_features[i] -
                    cluster_features[j]
                )
                distance[j, i] = distance[i, j]

        return max(distance)

    def instantiate_deltas(
            self,
            cluster_size: list
    ):
        """
        Initialize variable for calculating
        evaluation score
        :param cluster_size: number of
        cluster members
        :return: instantiated variables
        """
        deltas = ones(
            [cluster_size,
             cluster_size]
        ) * DUNN_DELTA_INIT

        big_deltas = zeros(
            [cluster_size, 1])

        indices = list(
            range(0, cluster_size)
        )

        return big_deltas, deltas, indices

    def compute_dunn_index(
            self,
            cluster_vectors: list
    ) -> float:
        """
        Calculates and returns Dunn Index
        :param cluster_vectors: list of np.arrays
            A list containing a numpy array
            for each cluster
            |c| = number of clusters c[K]
            is np.array([N, p])
            (N : number of samples in cluster K,
            p : sample dimension)
        :return: Dunn Index Score
        """
        big_deltas, deltas, indices = \
            self.instantiate_deltas(
                len(cluster_vectors))

        for index_cluster1 in indices:
            for index_cluster2 in (
                    indices[0:index_cluster1] +
                    indices[index_cluster1 + 1:]):

                if index_cluster1 > index_cluster2:
                    continue

                deltas[index_cluster1, index_cluster2] = \
                    self.delta(
                    cluster_vectors[index_cluster1],
                    cluster_vectors[index_cluster2])

                deltas[index_cluster2, index_cluster1] = \
                    deltas[index_cluster1, index_cluster2]

            big_deltas[index_cluster1] = self.big_delta(
                cluster_vectors[index_cluster1])

        return min(deltas) / max(big_deltas)

    def get_method_input_df(
            self,
            method: str
    ) -> DataFrame:
        """
        Returns features and cluster label
        merged df
        :param method: cluster method
        :return: merged dataframe
        """
        cluster_df = DataFrame(
            self.data[method],
            columns=[method]
        )
        input_set = concat(
            [self.features, cluster_df],
            axis=1
        )
        return input_set

    def prepare_dunn_input(
            self,
            input_set: DataFrame,
            method: str,
            unique_cluster_labels: list
    ):
        """
        For each cluster label, prepare the
        input feature set
        :param input_set:
        :param method:
        :param unique_cluster_labels:
        :return:
        """
        dunn_input = []
        for label in unique_cluster_labels:
            label_df = self.get_feature_label_df(
                input_set, label, method
            )
            dunn_input.append(label_df.values)
        return dunn_input

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
            unique_cluster_labels = \
                self.get_unique_cluster_labels(
                    self.data[method].to_numpy())

            input_set = self.get_method_input_df(
                method)

            dunn_input = self.prepare_dunn_input(
                input_set, method,
                unique_cluster_labels)

            scores[method] = self.compute_dunn_index(
                dunn_input)

        self.save_intermediate_results(
            subdirectory=EVAL_SCORES_IR2_PATH,
            filename=DUNN_INDEX_LABEL,
            result=scores)

        return scores

if __name__ == '__main__':
    data = read_csv(ROOT_PATH+"all_clusters.csv")
    dunn_index = DunnIndex(data=data)
    dunn_index.retrieve_ensemble_results()
    dunn_index.merge_ensemble_results()

    logging.info(LOGGING_DUNNINDEX)
    dunn_index.controller()
