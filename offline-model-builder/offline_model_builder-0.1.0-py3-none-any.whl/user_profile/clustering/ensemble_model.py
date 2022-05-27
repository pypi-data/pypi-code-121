import json
import random
from pandas import DataFrame
from offline_model_builder.user_profile.clustering.config import MIN_MEMBER_COUNT, ENSEMBLE_SD_CUTOFF
from offline_model_builder.user_profile.constants import CUSTOMER_ID, BIRCH_FEATURE, \
    KMEANS_FEATURE, MINIBATCH_KMEANS_FEATURE, WARDS_HIERARCHICAL_FEATURE, \
    KMEDOIDS_FEATURE, DBSCAN_FEATURE, OPTICS_FEATURE, \
    INTERMEDIATE_RESULTS_DIRECTORY, ENSEMBLE_IR2_PATH, JSON_EXTENSION, ENSEMBLE_IR3_PATH
from collections import Counter, abc
from itertools import islice
from math import sqrt
import os
import logging
logging.basicConfig(level=logging.INFO)

class EnsembleModel:

    def __init__(
            self,
            clusters=DataFrame
    ):
        """
        Instantiating data members.
        Proceeding only with cluster_ids and
        user identifier. Ignoring rest
        :param clusters: dataframe object pandas.
        Result from C1, consisting of cluster_id
        from all considered clustering algorithms.
        """
        self.clusters = clusters[[
            CUSTOMER_ID,
            KMEANS_FEATURE,
            MINIBATCH_KMEANS_FEATURE,
            WARDS_HIERARCHICAL_FEATURE,
            KMEDOIDS_FEATURE,
            DBSCAN_FEATURE,
            BIRCH_FEATURE
        ]]

    def load_intermediate_results(
            self,
            subdirectory: str,
            filename: str,
    ) -> dict:
        """
        Method to read intermediate results
        stored as JSON files.
        :param subdirectory: intermediate results
        sub-directory
        :param filename: string name
        :return: file inputs as dictionary
        """
        with open(
                INTERMEDIATE_RESULTS_DIRECTORY + "/"
                + subdirectory + "/" + filename + JSON_EXTENSION
        ) as infile:
            results = json.load(infile)
        return results

    def save_intermediate_results(
            self,
            subdirectory: str,
            filename: str,
            result: dict
    ):
        """
        Save intermediate results as JSON
        files
        :param subdirectory: intermediate results
        sub-directory
        :param filename: string name used to
        save the result
        :param result: dictionary
        :return: None
        """
        try:
            path = INTERMEDIATE_RESULTS_DIRECTORY + "/" + \
                   subdirectory + "/" + filename + JSON_EXTENSION
            isFile = os.path.isfile(path)
            if not isFile:
                parent_dir = INTERMEDIATE_RESULTS_DIRECTORY + "/"
                directory = subdirectory
                path = os.path.join(parent_dir, directory)
                mode = 0o777
                isdir = os.path.isdir(path)
                if not isdir:
                    os.makedirs(path, mode)
            with open(
                    INTERMEDIATE_RESULTS_DIRECTORY + "/"
                    + subdirectory + "/" + filename
                    + JSON_EXTENSION, "w"
                    ) as outfile:
                json.dump(result, outfile)
        except Exception:
            logging.error("Error in Saving Intermediate Results")

    def filter_cluster_members(
            self,
            cluster: list,
            cluster_results: str,
            results: DataFrame,
            members_only=bool
    ):
        """
        identify all users belonging to the same
        cluster for a specified clustering method
        :param cluster: cluster id to search within
        :param cluster_results: clustering method
        :param results: dataframe object pandas
        :param members_only: if True, return user
        identifiers, else return complete result
        :return: list if members_only==True else
        dataframe object pandas
        """
        members = (results[results[cluster_results]
                   .isin(cluster)])

        if members_only:
            return members[CUSTOMER_ID].tolist()
        return members

    def filter_cluster_members_by_index(
            self,
            indices: list
    ) -> DataFrame:
        """
        identify all users belonging to the same
        cluster using dataframe index
        :param indices: list of indices
        :return: dataframe object pandas
        """
        members = (
            self.clusters[self.clusters.index.isin(
                [indices]
            )
            ]).reset_index(drop=True)
        return members

    def get_cluster_wise_members(
            self,
            cluster_results: str
    ) -> dict:
        """
        Identify unique cluster ids from a clustering
        method result and prepare
        {cluster_id: [user1,user2,....],..} mapping
        :param cluster_results: clustering method name
        :return: dictionary mapping
        """
        results_mapping = {}
        results = self.clusters[[CUSTOMER_ID,
                                 cluster_results]]

        unique_clusters = list(results[cluster_results]
                               .unique())

        # cluster id singleton passed as a list
        # to used generalised called function
        for cluster in unique_clusters:
            members = self.filter_cluster_members(
                [cluster],
                cluster_results,
                results,
                members_only=True
            )
            results_mapping[str(cluster)] = members
        return results_mapping

    def get_birch_user_wise_subclusters(
            self,
    ) -> dict:
        """
        Prepare mapping dictionary of type
        { user1: cluster_idX, user2: cluster_idY,...}
        :return: dictionary mapping
        """
        df_birch = self.clusters[[CUSTOMER_ID, BIRCH_FEATURE]]
        df_birch = df_birch.set_index(CUSTOMER_ID)[BIRCH_FEATURE]
        return df_birch.to_dict()

    def find_small_clusters(
            self
    ) -> list:
        """
        Identify and return cluster ids which
        have member count less than the specified
        threshold
        :return: list of cluster ids with less
        than threshold member count
        """
        member_count = dict(Counter(
            self.clusters[BIRCH_FEATURE]
        ))
        small_clusters = []
        for key, value in member_count.items():
            if value < MIN_MEMBER_COUNT:
                small_clusters.append(key)

        return small_clusters

    def get_user_tendency_frequencies(
            self,
            user_members: str
    ) -> dict:
        """
        Compute user-frequency common cluster id frequencies
        considering all methods except Birch algorithm
        :param user_members: user id string
        :return: dictionary of user-user frequencies
        """
        clustering_wise_members = self.load_intermediate_results(
            subdirectory=ENSEMBLE_IR2_PATH,
            filename=user_members.split('.')[0]
        )

        all_members = []
        for values in list(clustering_wise_members.values()):
            all_members.extend(values)

        return dict(Counter(all_members))

    def get_top_frequencies(
            self,
            cutoff: int,
            frequencies: dict
    ) -> dict:
        """
        From the user-frequency common cluster
        id frequencies, find the users that share
        the same cluster more than a pre-specified
        integer cutoff
        :param cutoff: integer cutoff
        :param frequencies: dictionary of all
        user-frequency common cluster id frequencies
        :return: dictionary of user-frequency
        key-value pairs
        """
        return {key: value
                for key, value in frequencies.items()
                if value > cutoff}

    def get_birch_cluster_counts(
            self,
            user_top_members: str,
            birch_results: dict
    ) -> dict:
        """
        Compute the cluster_id frequency for the
        common cluster members for a given user
        :param user_top_members: user file name
        :param birch_results: birch clusters mapping
        :return: {cluster_id: frequency} mapping
        """
        top_members = self.load_intermediate_results(
            subdirectory=ENSEMBLE_IR3_PATH,
            filename=user_top_members.split('.')[0]
        )
        members_clusters = []
        for user in top_members:
            members_clusters.append(birch_results[user])

        return dict(Counter(members_clusters))

    def sort_frequencies(
            self,
            frequencies: dict,
            to_reverse=True
    ) -> dict:
        """
        Sort the cluster_id frequency mappings
        and return the updated mapping order
        :param frequencies: cluster: frequency
        mappings
        :param to_reverse: if True, sort in
        decreasing order
        :return: sorted dictionary mapping
        """
        return dict(sorted(
            frequencies.items(),
            key=lambda item: item[1],
            reverse=to_reverse
        ))

    def get_top_n_pairs(
            self,
            count: int,
            iterable: abc.ItemsView
    ) -> dict:
        """
        Get top N {cluster_id: frequency} mapping
        pairs
        :param count: N value
        :param iterable: Dictionary items type
        :return: N size subset of input mapping
        """
        return dict(islice(iterable, count))

    def get_deviation(
            self,
            items: list
    ) -> float:
        """
        Calculate Standard Deviation for a
        list of values
        :param items: list of values
        :return: standard deviation for the
        input list
        """
        mean = sum(items) / len(items)
        variance = sum([((value - mean) ** 2)
                        for value in items]) / len(items)
        return sqrt(variance)

    def choose_new_cluster(
            self,
            top_cluster_freq: dict
    ) -> int:
        """
        Choose a random key from the input dictionary
        :param top_cluster_freq: input dictionary
        mapping
        :return: Key at random index
        """
        return random.choice(top_cluster_freq)

    def assign_new_cluster(
            self,
            deviation: float,
            top_cluster_freq: dict
    ) -> int:
        """
        Assign a new cluster label for the
        specified user
        :param deviation: standard deviation
        :param top_cluster_freq:
        { cluster:frequency } mapping
        :return: New Cluster label
        """
        if deviation < ENSEMBLE_SD_CUTOFF:
            new_cluster = self.choose_new_cluster(
                list(top_cluster_freq)
            )
        else:
            new_cluster = max(
                top_cluster_freq,
                key=lambda x: top_cluster_freq[x]
            )
        return new_cluster
