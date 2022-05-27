from pandas import DataFrame

from offline_model_builder.user_profile.clustering.config import SPARSITY_THRESHOLD
from offline_model_builder.user_profile.constants import INTERMEDIATE_RESULTS_DIRECTORY, \
    NAN_DUMMY_FEATURE


class ClusteringUtils:

    def __init__(
            self,
            data=DataFrame,
    ):
        """
        :param data: consolidated user demographics
        and behaviour data
        """
        self.data = data

    def get_feature_sparsity(
            self,
            feature: list
    ) -> int:
        """
        More the frequency of zero in the input,
        greater the sparsity of the feature
        :param feature: input feature list
        :return: number of zeros in input
        """
        return sum(map(lambda val: val == 0, feature))

    def get_sparse_features(
            self,
    ) -> list:
        """
        identify features greater than the specified
        threshold from the complete input feature set
        :return: list of sparse features
        """
        size = len(self.data)
        features_to_drop = []

        for feature in self.data.columns:
            self.data[feature] = self.data[feature].fillna(0)
            values = self.data[feature].tolist()
            sparsity = self.get_feature_sparsity(values) / size
            if sparsity > SPARSITY_THRESHOLD:
                features_to_drop.append(feature)

        return features_to_drop

    def drop_sparse_features(
            self,
    ) -> DataFrame:
        """
        drop sparse features from being considered
        for clustering purposes
        :return:
        """
        sparse_features = self.get_sparse_features()
        #to drop all features representing nan values
        for feature in self.data.columns:
            if feature[len(feature)-4:] == NAN_DUMMY_FEATURE:
                sparse_features.append(feature)
        features = self.data.drop(columns=sparse_features)
        return features

    def remove_attributes(
            self,
            attributes: DataFrame,
            to_drop: list
    ) -> DataFrame:
        """
        removes the specified list of attributes
        from a given dataframe
        :param attributes: dataframe object pandas
        :param to_drop: list of df columns
        :return:
        """
        feature_set = attributes.drop(columns=to_drop)
        return feature_set

    def save_intermediate_results(
            self,
            df: DataFrame,
            filename: str
    ):
        """
        Can be called at any point if in
        case any df result needs to be saved for
        computation or observation purposes
        :param df: dataframe object pandas
        :param filename: df shall be saved with this
        Must include .csv at the end.
        :return:
        """
        df.to_csv(INTERMEDIATE_RESULTS_DIRECTORY+"/"+filename,
                  index=False)




