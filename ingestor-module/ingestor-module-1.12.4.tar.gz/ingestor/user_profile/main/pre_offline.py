from ingestor.user_profile.preprocessing.behaviour import PreprocessBehaviour
from ingestor.user_profile.preferences.generate_preferences import PreferenceGenerator
from ingestor.common.constants import CUSTOMER_ID, CSV_EXTENSION, \
    FINAL_MERGED_DF, SOLO_FEATURE_LIST, FEATURE_DICT
from pandas import DataFrame, merge
from functools import reduce
from ingestor.common.read_write_from_s3 import ConnectS3

class MainImplementation:
    def __init__(
            self,
            df1: DataFrame,
            df2: DataFrame
    ):
        """
        :param df1: dataframe object pandas
        :param df2: dataframe object pandas
        """
        self.df1 = df1
        self.df2 = df2

    def controller(
            self,
            resource=None,
            bucket_name=None,
            object_name=None,
    ) -> DataFrame:
        """
        Driver method for class MainImplementation which produces
        final_merged_df after complete preprocessing and
        preferences generation for user profile part.
        :return: preprocessed and user preference dataframe object pandas
        """
        appended_data = []

        behaviour = PreprocessBehaviour()
        demo = self.df1
        conn = ConnectS3()

        solo_features = behaviour.controller(
            data=self.df2,
            to_explode=False
        )
        for feature in SOLO_FEATURE_LIST:
            print("Generating User Preferences for the feature ---> ", feature)
            preference = PreferenceGenerator(
                feature=feature,
                feature_cutoff=2,
                user_cutoff=2
            )
            temp = preference.controller(
                data=solo_features,
                resource=resource,
                bucket_name=bucket_name,
                object_name=object_name,
            )
            conn.write_csv_to_s3(
                bucket_name=bucket_name,
                object_name=object_name + feature + CSV_EXTENSION,
                df_to_upload=temp,
                resource=resource)
            appended_data.append(temp)

        for features, value in FEATURE_DICT.items():
            print("Generating User Preferences for the feature ---> ", features)
            pref = PreferenceGenerator(
                feature=features,
                feature_cutoff=2,
                user_cutoff=2)
            temp = behaviour.controller(
                data=self.df2,
                to_explode=True,
                feature=features,
                key=value
            )
            temp = pref.controller(
                data=temp,
                resource=resource,
                bucket_name=bucket_name,
                object_name=object_name,
            )
            conn.write_csv_to_s3(
                bucket_name=bucket_name,
                object_name=object_name + features + CSV_EXTENSION,
                df_to_upload=temp,
                resource=resource)
            appended_data.append(temp)

        print("Merging VDB and UBD Data on customer_id....")
        merged_df = reduce(
            lambda l, r: merge(l, r, on=CUSTOMER_ID, how='inner'),
            appended_data
        )

        return merged_df
