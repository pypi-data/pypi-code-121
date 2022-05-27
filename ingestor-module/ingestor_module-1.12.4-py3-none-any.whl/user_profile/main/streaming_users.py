from ingestor.common.constants import BIRTHDAY, \
    CUSTOMER_MODIFIED_ON, CUSTOMER_CREATED_ON
from ingestor.user_profile.preprocessing.demographics \
    import PreprocessDemography
from ingestor.user_profile.network.user_node_generator \
    import UserNodeGenerator
from pandas import DataFrame, Timestamp
from graphdb.graph import GraphDb

class StreamingUsers:

    @staticmethod
    def process_date_fields(
            users: DataFrame,
            features: list
    ):
        """
        Convert datetime fields to Timestamp
        Format to avoid any ambiguities
        during node creation and dumping
        :param users: dataframe object pandas
        :param features: list of dataframe
        attributes
        :return: dataframe object pandas
        """
        for feature in features:
            users[feature] = \
                users[feature].apply(
                    lambda x: Timestamp(x)
                )

        return users

    @staticmethod
    def dump_streaming_users(
            users: DataFrame,
            connection_object
    ):
        """
        Static function to perform the following sequence
        of actions on the user dataframe object
        1) Preprocess user dataframe object
        2) Dump User profile nodes and create their
        relationships with paytv-provider nodes, if any.
        3) Assign these newly added users to one of the
        uer profile clusters.
        4) Compute the similarity for each of these newly
        added users with the rest of the existing
        users in the network.
        :param users: dataframe object pandas
        :param connection_object: graph connection object
        :return: None, updates the state of graphDB
        """
        graph = GraphDb.from_connection(
            connection_object
        )

        users = users.reset_index(drop=True)

        # user profile features preprocessing
        ppd = PreprocessDemography()
        preprocessed_users = ppd.controller(
            df=users
        )

        users = StreamingUsers.process_date_fields(
            users=users,
            features=[CUSTOMER_CREATED_ON,
                      CUSTOMER_MODIFIED_ON,
                      BIRTHDAY]
        )
        # dumping user nodes and forming its
        # relationships with paytv-provider nodes
        cls = UserNodeGenerator(
            data=preprocessed_users,
            graph=graph
        )
        cls.controller()

        # assigning newly added users to a cluster
        # label and computing their similarity with
        # their respective cluster members
