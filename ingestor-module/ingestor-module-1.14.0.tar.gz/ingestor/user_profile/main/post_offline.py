from ingestor.common.read_write_from_s3 import ConnectS3
from ingestor.common.constants import CSV_EXTENSION, CUSTOMER_ID
from ingestor.user_profile.main.config import \
    TO_READ_FROM_S3_PREFERENCES, TO_READ_FROM_S3_CLUSTERING_LABELS, \
    S3_PAYTV_PREFIX, S3_NONPAYTV_PREFIX
from pandas import DataFrame
import logging
from ingestor.user_profile.network.plot_relations import PlotRelations
from ingestor.user_profile.preferences.relationship_extractor import \
    RelationshipExtractor
logging.basicConfig(level=logging.INFO)

class PostOfflineMain:

    def __init__(
            self,
            s3_resource: None,
            s3_bucket_name: None,
            s3_object_name: None
    ):
        self.s3_resource = s3_resource
        self.s3_bucket_name = s3_bucket_name
        self.s3_object_name = s3_object_name

    def get_file_from_s3(
            self,
            filename: str
    ) -> DataFrame:
        """
        Method to return CSV read from s3
        :param filename: file to obtain
        :return: dataframe object pandas
        """
        return ConnectS3().read_csv_from_s3(
            bucket_name=self.s3_bucket_name,
            object_name=self.s3_object_name + filename + CSV_EXTENSION,
            resource=self.s3_resource
        )

    def filter_users(
            self,
            all_users: DataFrame,
            users_to_keep: list
    ) -> DataFrame:

        all_users[CUSTOMER_ID] = all_users[CUSTOMER_ID].astype(str)
        return all_users[all_users[CUSTOMER_ID].isin(users_to_keep)]\
            .reset_index(drop=True)


    def get_feature_relations(
            self,
            data: DataFrame
    ) -> DataFrame:
        """
        Use the relationship extractor to for
        relationship dataframe object based on
        user's preferences
        :param data: dataframe object pandas
        :return: dataframe object pandas with each
        record representing a relationship between
        a user and a node type.
        """
        re = RelationshipExtractor(
            data=data
        )
        return re.controller()

    def plot_relations(
            self,
            data: DataFrame,
            relation_label: str,
            destination_prop_label: str,
            connection_object,
            is_paytv=None
    ):
        """
        Dump the relations obtained from the
        relationship extractor into the Graph Database.
        The method to create relationship is create
        relationship without upsert
        :return: None, the update is reflected in the
        graph network network state.
        """
        pr = PlotRelations(
            data=data,
            label=relation_label,
            connection_uri=connection_object
        )
        pr.controller(
            destination_prop_label=destination_prop_label,
            is_paytv=is_paytv
        )

    def drop_nan_features(
            self,
            data
    ):
        to_drop = []
        for feature in data.columns:
            if feature[len(feature) - 4:] == '_nan':
                to_drop.append(feature)
        return data.drop(columns=to_drop)

    def preferences_controller(
            self,
            connection_object,
            users: list,
            paytv: str
    ):
        """
        The driver function for the procedure of dumping
        relations into GraphDB
        :return: None, the update is reflected in the
        graph network network state.
        """
        for filename, file_meta in TO_READ_FROM_S3_PREFERENCES.items():
            data = self.get_file_from_s3(
                filename=filename
            )

            data = self.filter_users(
                all_users=data,
                users_to_keep=users
            )

            data = self.drop_nan_features(data)
            if len(data.columns) == 1 \
                    or len(data) == 0:
                continue

            data = self.get_feature_relations(
                data=data
            )
            logging.info(
                "Dumping file " + "mapping_" +
                paytv + filename + CSV_EXTENSION
                )

            ConnectS3().write_csv_to_s3(
                bucket_name=self.s3_bucket_name,
                object_name=self.s3_object_name + "mapping_" +
                paytv + filename + CSV_EXTENSION,
                resource=self.s3_resource,
                df_to_upload=data
            )

    def clustering_controller(
            self,
            connection_object,
            is_paytv: bool,
    ):
        for filename, file_meta in TO_READ_FROM_S3_CLUSTERING_LABELS.items():

            filename = S3_PAYTV_PREFIX + filename if is_paytv \
                else S3_NONPAYTV_PREFIX + filename

            data = self.get_file_from_s3(
                filename=filename
            )

            data = self.drop_nan_features(data)
            if len(data.columns) == 1 \
                    or len(data) == 0:
                continue

            logging.info(
                "Dumping file " + "mapping_" +
                filename + CSV_EXTENSION
            )

            ConnectS3().write_csv_to_s3(
                bucket_name=self.s3_bucket_name,
                object_name=self.s3_object_name + "mapping_" +
                            filename + CSV_EXTENSION,
                resource=self.s3_resource,
                df_to_upload=data
            )