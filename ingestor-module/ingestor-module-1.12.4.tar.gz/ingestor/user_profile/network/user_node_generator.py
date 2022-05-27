from pandas import DataFrame, concat
from graphdb.schema import Node, Relationship
from ingestor.common.constants import (
    LABEL,
    PROPERTIES,
    RELATIONSHIP,
    CUSTOMER_ID,
    PAYTV_PROVIDER,
    PAYTVPROVIDER_ID,
    USER_LABEL,
    BIRTHDAY,
    CUSTOMER_CREATED_ON,
    CUSTOMER_MODIFIED_ON,
)
from ingestor.user_profile.main.config import HAS_PAYTV_PROVIDER


class UserNodeGenerator:
    def __init__(self, data: DataFrame, graph: None):
        """
        Constructor that accepts the dataframe
        object pandas and graphDB connection instance
        :param data: dataframe object pandas
        :param graph: graphDB connection instance
        """
        self.data = data
        self.graph = graph
        self.user_cache = {}
        self.paytv_cache = {}

    def get_relation_data(self):
        """
        Get user and paytv-provider features
        only from the input dataframe object pandas
        :return:
        """
        return self.data[[CUSTOMER_ID, PAYTVPROVIDER_ID]]

    def get_property_data(self):
        """
        Get Dataframe attributes that are to be
        added as properties to the user nodes
        :return:
        """
        return self.data.drop(columns=[PAYTVPROVIDER_ID])

    def dump_user_nodes(self, property_data: DataFrame) -> list:
        """
        Dump the dataframe records as
        individual nodes into GraphDB
        :return: Dumped nodes
        """
        property_data[BIRTHDAY] = property_data[BIRTHDAY].astype(str)
        property_data[CUSTOMER_CREATED_ON] = property_data[CUSTOMER_CREATED_ON].astype(
            str
        )
        property_data[CUSTOMER_MODIFIED_ON] = property_data[
            CUSTOMER_MODIFIED_ON
        ].astype(str)

        error_users = DataFrame()

        for record in property_data.to_dict(orient="records"):
            try:
                node = Node(**{LABEL: USER_LABEL, PROPERTIES: record})

                print("Creating User: ", node)
                _ = self.graph.create_node(node=node)
            except Exception:
                print("!! Error in dumping user !!")
                error_users = concat(
                    [error_users, DataFrame([record])], axis=0
                ).reset_index(drop=True)

        error_users.to_csv("error_user_profile_dump.csv", index=False)

    def plot_relation(self, source: Node, destination: Node):
        """
        Create a relationship between two Node
        objects passed as parameters
        :param source: Source Node
        :param destination: Destination Node
        :return: Relationship object
        """
        self.graph.create_relationship_without_upsert(
            node_from=source,
            node_to=destination,
            rel=Relationship(**{RELATIONSHIP: HAS_PAYTV_PROVIDER}),
        )

    def get_node(self, label: str, properties: dict) -> Node:
        """
        Creates a Node object using the given
        label and property values. This object
        is then created in the GraphDB if it
        does not exist already, otherwise the
        already existing node is returned
        :param label: Node label
        :param properties: Node properties
        :return: Node object
        """
        node = Node(**{LABEL: label, PROPERTIES: properties})
        node_in_graph = self.graph.find_node(node)
        return node_in_graph[0]

    def get_from_user_cache(self, index: int, relation_data: DataFrame):
        customer_id = relation_data.loc[index, CUSTOMER_ID]
        if self.user_cache.get(customer_id, None) is not None:
            return self.user_cache[customer_id]

        self.user_cache[customer_id] = self.get_node(
            label=USER_LABEL,
            properties={CUSTOMER_ID: customer_id},
        )
        return self.user_cache[customer_id]

    def get_from_paytv_cache(self, index: int, relation_data: DataFrame):
        paytv_provider_id = (relation_data.loc[index, PAYTVPROVIDER_ID][0])[
            PAYTVPROVIDER_ID
        ]
        if self.paytv_cache.get(paytv_provider_id, None) is not None:
            return self.paytv_cache[paytv_provider_id]

        self.paytv_cache[paytv_provider_id] = self.get_node(
            label=PAYTV_PROVIDER,
            properties={PAYTVPROVIDER_ID: paytv_provider_id},
        )
        return self.paytv_cache[paytv_provider_id]

    def historical_plot_user_paytv_relations(self, relation_data: DataFrame):
        error_records = DataFrame(columns=relation_data.columns)

        for index in range(len(relation_data)):
            # since paytvprovider_id comes in a list of dict
            try:
                print("Dumping relation ", index + 1, " of ", len(relation_data))
                source_node = self.get_from_user_cache(index, relation_data)
                destination_node = self.get_from_paytv_cache(index, relation_data)
                self.plot_relation(source=source_node, destination=destination_node)
            except Exception:
                print("!! Error Dumping User-PayTV Relation !!")
                error_record = list(relation_data.loc[index, :])
                error_records.loc[len(error_records.index)] = error_record

        error_records.to_csv("error_user_paytv_relations.csv", index=False)

    def plot_user_paytv_relations(self, relation_data: DataFrame):
        """
        Method for plotting relations between
        user and paytv-provider nodes
        :param relation_data: dataframe
        object pandas
        :return: None, the relations are
        dumped into the GraphDB
        """
        error_records = DataFrame(columns=relation_data.columns)

        for index in range(len(relation_data)):
            # since paytvprovider_id comes in a list of dict
            try:
                print("Dumping relation ", index + 1, " of ", len(relation_data))
                source_node = self.get_node(
                    label=USER_LABEL,
                    properties={CUSTOMER_ID: relation_data.loc[index, CUSTOMER_ID]},
                )
                destination_node = self.get_node(
                    label=PAYTV_PROVIDER,
                    properties={
                        PAYTVPROVIDER_ID: (
                            relation_data.loc[index, PAYTVPROVIDER_ID][0]
                        )[PAYTVPROVIDER_ID]
                    },
                )
                self.plot_relation(source=source_node, destination=destination_node)
            except Exception:
                print("!! Error Dumping User-PayTV Relation !!")
                error_record = list(relation_data.loc[index, :])
                error_records.loc[len(error_records.index)] = error_record

        error_records.to_csv("error_user_paytv_relations.csv", index=False)

    def controller(self):
        """
        Driver function for dumping user
        nodes in GraphDB
        :return: None, updates the structural
        state of GraphDB
        """
        print("Retrieving User Node Property Data....")
        property_data = self.get_property_data()
        print("Dumping User Nodes.....")
        self.dump_user_nodes(property_data=property_data)

    def historical_relation_dump_controller(self):
        """
        Driver function to plot user-paytv relations
        in Graphdb
        :return: None, updates the structural
        state of GraphDB
        """

        print("Retrieving User-PayTV Relation Data....")
        relation_data = self.get_relation_data()

        print("Dumping Relations between Users and PayTV Providers")
        self.historical_plot_user_paytv_relations(relation_data=relation_data)

    def relation_dump_controller(self):
        """
        Driver function to plot user-paytv relations
        in Graphdb
        :return: None, updates the structural
        state of GraphDB
        """

        print("Retrieving User-PayTV Relation Data....")
        relation_data = self.get_relation_data()

        print("Dumping Relations between Users and PayTV Providers")
        self.plot_user_paytv_relations(relation_data=relation_data)
