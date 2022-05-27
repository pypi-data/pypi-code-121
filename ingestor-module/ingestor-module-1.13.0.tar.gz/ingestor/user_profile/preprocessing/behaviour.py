from pandas import DataFrame
from ingestor.common.preprocessing_utils import Utils
from ingestor.common.constants import CUSTOMER_ID, DURATION, ATTRIBUTE1, VOD, CHANNEL_LIVE, CATCHUP, \
    DEFAULT_FEATURE_VALUES


class PreprocessBehaviour:

    def preprocess_customer_id(
            self,
            data: DataFrame
    ) -> DataFrame:
        """
        This function type casts customer_id to string.
        :param data: dataframe object pandas
        :return: preprocessed dataframe object pandas
        """
        data[CUSTOMER_ID] = data[CUSTOMER_ID].astype(str)
        return data

    def attribute1_substitution(
            self,
            data: DataFrame
    ) -> DataFrame:
        """
        This function substitutes the values in attribute1 with custom values

        :param data: dataframe object pandas
        :return: dataframe object pandas
        """
        data.loc[data[ATTRIBUTE1].str.contains(
            CHANNEL_LIVE, case=False),
                 ATTRIBUTE1] = CHANNEL_LIVE
        data.loc[data[ATTRIBUTE1].str.contains(
            CATCHUP, case=False),
                 ATTRIBUTE1] = CATCHUP
        data.loc[data[ATTRIBUTE1].str.contains(
            VOD, case=False),
                 ATTRIBUTE1] = VOD

        return data

    def preprocess_features(
            self,
            data: DataFrame,
    ) -> DataFrame:
        """
        This function takes dict of features and their default nan values
        and calls fillna_and_cast_lower function for preprocessing.

        :param data: dataframe object pandas
        :return: dataframe object pandas
        """
        for feature, value in DEFAULT_FEATURE_VALUES.items():
            data = Utils.fillna_and_cast_lower(
                data,
                feature=feature,
                default_val=value
            )

        return data

    def preprocess_and_explode(
            self,
            data: DataFrame,
            feature: str,
            key: str
    ) -> DataFrame:
        """
        This function transforms each element of a
        list-like to a row, replicating index values.

        :param data: dataframe object pandas
        :param feature: feature name
        :param key: dict key to be used
        :return: preprocessed dataframe object pandas
        """
        data = data[[CUSTOMER_ID, DURATION, feature]]
        mask = data[feature].apply(
            lambda d: d if isinstance(d, list) else []
        )
        result_list = [[x[key] for x in list_dict]
                       for list_dict in mask]
        data = data.drop([feature], axis=1)
        data[feature] = result_list

        return data.explode(feature).fillna('nan')

    def controller(
            self,
            data: DataFrame,
            to_explode: bool,
            feature='',
            key=''
    ) -> DataFrame:
        """
        The driver function for PreprocessBehaviour class.
        Returns preprocessed dataframe and also breaks the list of
        feature values specified in feature parameter in
        multiple rows, as per the value specified for 'to_explode'

        :param data: dataframe object pandas
        :param to_explode: if True, split the list of value into
        separate records, ignore otherwise
        :param feature: feature to be exploded
        :param key: dict key to be used
        :return: preprocessed dataframe object pandas
        """

        data = self.preprocess_customer_id(data)

        if to_explode:
            print("Preprocessing {}...".format(feature))
            data = self.preprocess_and_explode(data, feature, key)

        else:
            print("Substituting values in Attribute1...")
            data = self.attribute1_substitution(data)

            print("Preprocessing User Behaviour Features...")
            data = self.preprocess_features(data)

            print("Finished Preprocessing User Behaviour Data...")

        return data
