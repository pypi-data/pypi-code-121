from pandas import DataFrame, get_dummies, concat
from ingestor.common.constants import CUSTOMER_ID, DURATION, \
    DURATION_WEIGHT, CLICK_COUNT_WEIGHT
from sklearn.feature_extraction.text import CountVectorizer
import re
from ingestor.common.read_write_from_s3 import ConnectS3


class PreferenceGenerator:

    def __init__(
            self,
            feature=None,
            feature_cutoff=None,
            user_cutoff=None
    ):
        """
        :param feature: feature from the data
        for which preference needs to be computed
        :param feature_cutoff: All rankings in the lower
        1/feature_cutoff of a given feature's values
        would not be considered for preference generation.
        :param user_cutoff: All rankings in the lower
        1/user_cutoff of a given user's values
        would not be considered for preference generation.
        """
        self.feature = feature
        self.feature_cutoff = feature_cutoff
        self.user_cutoff = user_cutoff

    def filter_features(
            self,
            df: DataFrame,
    ) -> DataFrame:
        """
        Filter the feature set from the provided DataFrame
        to comprise of features important for preference
        generation. (identifier and duration features being
        the mandatory components)

        :param df: dataframe object pandas
        :return: filtered dataframe object pandas
        """
        return df[[CUSTOMER_ID, DURATION, self.feature]]

    def get_dummy_attributes(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        Generate dummy attributes for the considered feature

        :param df: dataframe object pandas
        :return: Binary encoded dataframe object pandas
        """

        return get_dummies(df, columns=[self.feature])

    @staticmethod
    def get_dense_rank(
            df: DataFrame
    ) -> DataFrame:
        """
        compute the ranking of the features and replace
        against its constituent values.
        :param df: dataframe object pandas
        :return:  weighted dataframe object pandas
        """

        for feature in df.columns:
            if feature in [CUSTOMER_ID, DURATION]:
                continue
            df[feature] = df[feature].rank(method="dense")

        return df

    def prepare_feature(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        Replace unnecessary characters from the feature to be
        passed in count vectorizer function
        :param df: Dataframe object pandas
        :return: processed dataframe object pandas
        """
        df[self.feature] = df[self.feature].apply(str)
        df[self.feature] = df[self.feature].apply(lambda x: x.replace("[", ""))
        df[self.feature] = df[self.feature].apply(lambda x: x.replace("]", ""))
        df[self.feature] = df[self.feature].apply(lambda x: x.replace(",", ""))
        df[self.feature] = df[self.feature].apply(lambda x: x.replace("'", ""))

        return df

    def my_tokenizer(
            self,
            text
    ):
        """
        Tokenizer to split a string into a sequence of tokens
        :param text: text to be split
        :return: split text
        """

        return re.split("\\s+", text)

    def compute_weighted_click_count(
            self,
            df: DataFrame,
            resource=None,
            bucket_name=None,
            object_name=None,
    ) -> DataFrame:
        """
        Get view count/click count of features using
        count vectorizer method and then
        :param object_name: s3 object path
        :param bucket_name: s3 bucket name
        :param resource: boto connection resource
        :param df: dataframe object pandas
        :return: Binary encoded dataframe object pandas
        """
        grouped_df = df.groupby([CUSTOMER_ID])
        df = DataFrame(grouped_df[self.feature].apply(list))
        df[CUSTOMER_ID] = df.index
        df = df.reset_index(drop=True)
        df = self.prepare_feature(df)
        count_vect = CountVectorizer(tokenizer=self.my_tokenizer)
        df[self.feature] = df[self.feature].apply(str)
        temp_df = count_vect.fit_transform(df[self.feature])
        print("Vocabulary of {}_{} : ".format(self.feature, count_vect.vocabulary_))
        print("Saving {} vocabulary pickle in s3...")
        ConnectS3().write_pkl_to_s3(bucket_name=bucket_name,
                                    object_name=object_name + self.feature + "_vocab.pkl",
                                    resource=resource)
        column_list = [self.feature + "_" + str(i) for i in count_vect.get_feature_names_out()]
        count_vect_df = DataFrame(temp_df.todense(), columns=column_list).reset_index(drop=True)
        df = concat([df.reset_index(drop=True), count_vect_df], axis=1)
        df = df.drop(columns=self.feature)
        for column in df.columns:
            if column == CUSTOMER_ID:
                continue
            df[column] = CLICK_COUNT_WEIGHT * df[column]

        df = PreferenceGenerator.get_dense_rank(df)

        return df

    @staticmethod
    def compute_weighted_duration(
            df: DataFrame,
    ) -> DataFrame:
        """
        Computes weights for each dummy attribute using
        duration values from the data.

        :param df: dataframe object pandas
        :return: weighted dataframe object pandas
        """

        for feature in df.columns:
            if feature in [CUSTOMER_ID, DURATION]:
                continue
            df[feature] = df[feature] * df[DURATION] * DURATION_WEIGHT

        df.drop(columns=DURATION, inplace=True)
        weighted_df = df.groupby([CUSTOMER_ID]).sum()
        weighted_df = weighted_df.reset_index()
        weighted_df = PreferenceGenerator.get_dense_rank(weighted_df)

        return weighted_df

    def add_dataframe_columns(
            self,
            df_duration: DataFrame,
            df_count: DataFrame
    ):
        """
        Function to add columns of two dataframes
        :param df_duration: dataframe object pandas
        :param df_count: dataframe object pandas
        :return: dataframe object pandas
        """
        new_df = DataFrame()
        new_df[CUSTOMER_ID] = df_duration[CUSTOMER_ID]
        cols = df_duration.columns.difference([CUSTOMER_ID])
        temp = df_duration[cols].add(df_count[cols])
        new_df = concat([new_df, temp], axis=1)

        return new_df

    @staticmethod
    def compute_feature_level_ranking(
            df: DataFrame
    ) -> DataFrame:
        """
        For each weighted dummy attribute in the dataset,
        compute the ranking and replace against its
        constituent values.

        :param df: dataframe object pandas
        :return: weighted dataframe object pandas
        """
        for feature in df.columns:

            if feature == CUSTOMER_ID:
                continue

            df[feature] = df[feature].rank(method='min')
            df[feature] = df[feature].astype(int)

        return df

    @staticmethod
    def obtain_preference_candidates(
            values: list,
            cutoff: int
    ) -> list:
        """
        Return values that lie beyond the specified
        cutoff range.

        :param values: list of duration values
        :param cutoff: integer threshold
        :return: list of candidate duration values
        """
        values.sort()
        candidates = len(values) // cutoff

        return values[candidates:]

    def rank_attribute_values(
            self,
            df: DataFrame,
            feature: str
    ) -> DataFrame:
        """
        Rank the duration values for the
        considered feature.

        :param df: dataframe object pandas
        :param feature: attribute name
        :return: binary encoded preference
        indicative values for the feature
        """
        values = list(df[feature].unique())
        values = self.obtain_preference_candidates(
            values=values,
            cutoff=self.feature_cutoff
        )

        df[feature] = [1 if value in values else 0
                       for value in df[feature]]

        return df

    def rank_record_values(
            self,
            df: DataFrame,
            record: int
    ) -> DataFrame:
        """
        Rank the duration values for the considered
        user record.

        :param df: dataframe object pandas
        :param record: user record
        :return: binary encoded preference indicative
        values for the user record.
        """

        # ignoring identifier attribute at 0th index
        record_v = df.iloc[record, 1:]

        unique_v = list(set(record_v.values))
        unique_v = self.obtain_preference_candidates(
            values=unique_v,
            cutoff=self.user_cutoff
        )

        # updating all attributes except the identifier
        df.iloc[record, 1:] = [1 if value in unique_v else 0
                               for value in record_v]

        return df

    def get_feature_preference_encodings(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        For the weighted duration feature values, find the
        preference candidates.

        :param df: dataframe object pandas
        :return: preference encoded dataframe object pandas
        """
        for feature in df.columns:

            if feature == CUSTOMER_ID:
                continue
            df = self.rank_attribute_values(df, feature)

        return df

    def get_user_preference_encodings(
            self,
            df: DataFrame
    ) -> DataFrame:
        """
        For the weighted duration user record values, find
        the preference candidates.

        :param df: dataframe object pandas
        :return: preference encoded dataframe object pandas
        """
        for index in range(len(df)):
            df = self.rank_record_values(df, index)

        return df

    @staticmethod
    def get_preferences(
            cat_data: DataFrame,
            user_data: DataFrame
    ) -> DataFrame:
        """
        Computing feature preference values for the user by
        replicating boolean OR operation over the feature
        preference candidates and user preference candidates.

        :param cat_data: dataframe object pandas
        :param user_data: dataframe object pandas
        :return:
        """
        preferences = DataFrame(columns=user_data.columns)
        preferences[CUSTOMER_ID] = user_data[CUSTOMER_ID]

        for feature in preferences.columns:

            if feature == CUSTOMER_ID:
                continue

            preferences[feature] = user_data[feature] + cat_data[feature]
            preferences[feature] = [1 if pref_feature > 0 else 0
                                    for pref_feature in preferences[feature]]

        return preferences

    def controller(
            self,
            data: DataFrame,
            resource=None,
            bucket_name=None,
            object_name=None,
    ) -> DataFrame:
        """
        The driver method for member functions in
        PreferenceGenerator class. Uses the input path
        to read raw feature set to generate
        user-wise preferences for each of them.
        :param object_name: s3 object path
        :param bucket_name: s3 bucket name
        :param resource: boto connection resource
        :param data: dataframe object pandas
        :return: preference encoded dataframe object
        """
        for column in data.columns:

            if column in [CUSTOMER_ID, DURATION]:
                continue

            data = self.filter_features(data)
            click_data = self.compute_weighted_click_count(df=data,
                                                           resource=resource,
                                                           bucket_name=bucket_name,
                                                           object_name=object_name)
            data = self.get_dummy_attributes(data)
            data = self.compute_weighted_duration(data)
            data = self.add_dataframe_columns(data, click_data)
            cat_d = self.compute_feature_level_ranking(data.copy())
            cat_d = self.get_feature_preference_encodings(cat_d)
            user_d = self.get_user_preference_encodings(data.copy())

            return self.get_preferences(cat_d, user_d)