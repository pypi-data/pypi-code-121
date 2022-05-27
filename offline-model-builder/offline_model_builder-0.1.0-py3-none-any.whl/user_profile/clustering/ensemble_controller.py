import logging
from offline_model_builder.user_profile.clustering.config import TENDENCY_CUTOFF, TOP_N_MEMBERS_COUNT
from offline_model_builder.user_profile.clustering.ensemble_model import EnsembleModel
from pandas import DataFrame
from os import listdir

from offline_model_builder.user_profile.constants import CUSTOMER_ID, BIRCH_FEATURE, \
    INTERMEDIATE_RESULTS_DIRECTORY, ENSEMBLE_IR1_PATH, CLUSTERING_NOISE_PT, \
    ENSEMBLE_IR2_PATH, ENSEMBLE_IR3_PATH, ENSEMBLE_IR4_PATH, TEMP_FILE

logging.basicConfig(level=logging.INFO)


class EnsembleController(EnsembleModel):

    def __init__(
            self,
            data=DataFrame
    ):
        EnsembleModel.__init__(self, clusters=data)

    def get_cluster_mappings(
            self
    ):
        """
        For a clustering method, prepare mapping
        of type {cluster_id: [user1, user2, ..]}
        :return: None
        """
        for feature in self.clusters.columns:

            # for Birch Algorithm results, the mapping
            # in a different format for easier
            # interpretability
            if feature in [CUSTOMER_ID, BIRCH_FEATURE]:
                continue

            members = self.get_cluster_wise_members(
                cluster_results=feature
            )
            self.save_intermediate_results(
                subdirectory=ENSEMBLE_IR1_PATH,
                filename=feature,
                result=members
            )

        birch_results = self.get_birch_user_wise_subclusters()
        self.save_intermediate_results(
            subdirectory=ENSEMBLE_IR1_PATH,
            filename=BIRCH_FEATURE,
            result=birch_results
        )

    def get_user_members_for_method(
            self,
            cluster: int,
            clusters: dict
    ):
        """
        return members for a specified cluster id
        :param cluster: cluster id
        :param clusters: {cluster: user} mapping
        :return: list of members
        """
        return clusters[str(cluster)]

    def get_all_clustering_members_for_user(
            self,
            user_index: int
    ):
        """
        Retrieve all cluster members from all
        the methods for a given user
        :param user_index: integer index in dataframe
        object pandas
        :return: members dictionary, customer_id at
        the passed dataframe index
        """
        method_wise_members = {}
        user_clusters = self.filter_cluster_members_by_index(
            user_index
        )

        for method in user_clusters.columns:

            # common cluster members are to be ignored
            # for Birch Algorithm results
            if method in [CUSTOMER_ID, BIRCH_FEATURE]:
                continue

            # if in case the user is not assigned any cluster,
            # i.e. identified as a noise point by any of the
            # density-based clustering algorithms
            if user_clusters.loc[0, method] == CLUSTERING_NOISE_PT:
                method_wise_members[method] = []
                continue

            clusters = self.load_intermediate_results(
                subdirectory=ENSEMBLE_IR1_PATH,
                filename=method
            )
            method_wise_members[method] = \
                self.get_user_members_for_method(
                    user_clusters.loc[0, method],
                    clusters
                )

        return method_wise_members, user_clusters.loc[0, CUSTOMER_ID]

    def get_user_cluster_members(
            self,
            user_df: DataFrame
    ):
        """
        Iterate through each user and identify
        the frequency of common cluster ids
        with other users
        :param user_df: dataframe object pandas
        :return: None
        """
        user_indices = user_df.index
        for index in user_indices:
            members, customer_id = \
                self.get_all_clustering_members_for_user(
                    index
                )

            self.save_intermediate_results(
                subdirectory=ENSEMBLE_IR2_PATH,
                filename=str(customer_id),
                result=members
            )

    def compute_tendency(
            self
    ):
        """
        Compute Tendency Score i.e. number of times a
        user has shared the same cluster with another
        user across all the clustering methods.
        :return: None, the results computed are stored
        as intermediate results
        """
        users = listdir(
            INTERMEDIATE_RESULTS_DIRECTORY + "/"
            + ENSEMBLE_IR2_PATH + "/"
        )
        for user in users:
            # .DS_Store is an invisible file created on macOS.
            # when reading intermediate clustering results using
            # the os module, this file also gets read.
            if user == TEMP_FILE:
                continue
            scores = self.get_user_tendency_frequencies(user)
            top_scores = self.get_top_frequencies(
                TENDENCY_CUTOFF,
                scores
            )
            self.save_intermediate_results(
                subdirectory=ENSEMBLE_IR3_PATH,
                filename=user.split('.')[0],
                result=top_scores
            )

    def get_birch_cluster_for_users(
            self,
            birch_results: dict
    ) -> dict:
        """
        BIRCH ensemble sub-pipeline:
        Use the tendency scores to assign
        new cluster labels for users.
        :param birch_results:
        :return: updated cluster label
        mapping
        """
        users = listdir(INTERMEDIATE_RESULTS_DIRECTORY
                        + "/" + ENSEMBLE_IR3_PATH + "/")
        result = {}
        for index, user in enumerate(users):
            if user == TEMP_FILE:
                continue
            user_id = user.split('.')[0]
            cluster_freq = self.get_birch_cluster_counts(
                user_id,
                birch_results
            )
            sorted_cluster_freq = self.sort_frequencies(
                cluster_freq,
                to_reverse=True
            )
            top_cluster_freq = self.get_top_n_pairs(
                TOP_N_MEMBERS_COUNT,
                sorted_cluster_freq.items()
            )
            deviation = self.get_deviation(
                list(top_cluster_freq.values())
            )
            new_cluster = self.assign_new_cluster(
                deviation,
                top_cluster_freq
            )
            result[user_id] = new_cluster

        return result

    def birch_ensemble(
            self
    ):
        """
        BIRCH ensemble pipeline driver function:
        updates the BIRCH algorithm results
        based on the tendency scores obtained
        from the rest of the algorithms.
        :return: None, the result is saved as an
        intermediate result
        """
        birch_results = self.load_intermediate_results(
            subdirectory=ENSEMBLE_IR1_PATH,
            filename=BIRCH_FEATURE
        )
        result = self.get_birch_cluster_for_users(
            birch_results
        )
        for key in result:
            birch_results[key] = result[key]
        self.save_intermediate_results(
            subdirectory=ENSEMBLE_IR4_PATH,
            filename=BIRCH_FEATURE,
            result=birch_results)

    def controller(
            self
    ):
        """
        Driver function for EnsembleController class
        :return: None, the results are stored as
        intermediate files under
        intermediate_results/ensemble_<*>
        """
        logging.info("Applying Clustering Algorithms...")
        self.get_cluster_mappings()

        logging.info("Finding smallest BIRCH sub-clusters...")
        small_clusters = self.find_small_clusters()
        small_members = self.filter_cluster_members(
            cluster=small_clusters,
            cluster_results=BIRCH_FEATURE,
            results=self.clusters,
            members_only=False
        )
        self.get_user_cluster_members(small_members)

        logging.info("Computing Tendency Scores...")
        self.compute_tendency()

        logging.info("Computing BIRCH ensemble results...")
        self.birch_ensemble()