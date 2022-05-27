import numpy
from pandas import DataFrame
from graphdb.connection import GraphDbConnection
from graphdb.graph import GraphDb
from graphdb.schema import Node, Relationship
from ingestor.common.constants import LABEL, PROPERTIES, \
    RELATIONSHIP, CUSTOMER_ID, USER_LABEL
from ingestor.user_profile.main.config import IS_PAYTV_PROPERTY_LABEL


class PlotRelations:

    def __init__(
            self,
            data: DataFrame,
            label: str,
            connection_uri
    ):
        """
        Parameterized constructor that accepts a
        2D df with source and destination node
        information and the edge label that needs
        to be assigned to them
        :param data: dataframe object pandas
        :param label: edge label
        :param connection_uri: Gremlin Server
        connection URI
        """
        self.data = data
        self.rel_label = label
        self.graph = GraphDb.from_connection(
            connection_uri
        )

    def get_node(
            self,
            label: str,
            properties: dict
    ) -> Node:
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
        node = Node(
            **{
                LABEL: label,
                PROPERTIES: properties
            })
        node_in_graph = self.graph.find_node(node)
        if len(node_in_graph) > 0:
            return node_in_graph[0]
        return self.graph.create_node(node)

    def dump_relation(
            self,
            source: Node,
            destination: Node,
            properties={}
    ):
        """
        Create a relationship between two Node
        objects passed as parameters
        :param source: Source Node
        :param destination: Destination Node
        :param properties: relationship properties
        :return: Relationship object
        """
        self.graph.create_relationship_without_upsert(
            node_from=source,
            node_to=destination,
            rel=Relationship(
                **{
                    RELATIONSHIP: self.rel_label,
                    PROPERTIES: properties
                }
            )
        )

    def get_properties(
            self,
            destination_label,
            destination_prop_label,
            index
    ):
        """
        Get node properties for source and destination
        nodes respectively
        :param destination_label: Destination node label
        :param destination_prop_label: Destination node
        property label
        :param index: record number in input dataframe
        :return: Destination and Source node properties
        """
        source_properties = {
            CUSTOMER_ID:
                str(self.data.loc[index, CUSTOMER_ID])
        }

        dest_properties = {
            destination_prop_label:
                self.data.loc[index, destination_label]
        }

        return dest_properties, source_properties

    def get_destination_label(
            self
    ):
        """
        Get label for the destination node
        from the input df
        :return: node label
        """
        labels = list(self.data.columns)
        labels.remove(CUSTOMER_ID)
        destination_label = labels[0]
        return destination_label

    def controller(
            self,
            destination_prop_label: str,
            is_paytv=None,
            property_attributes=[]
    ):
        """
        Driver function for creating non-existent nodes
        and creating relationships as per the input df
        for the construction of user profile network
        :param destination_prop_label: Property name
        for the destination node
        :param is_paytv: if not None, an extra property
        is added to the node related to whether its related
        to a paytv users or not
        :param property_attributes: list of dataframe columns
        to be used for relationship properties
        :return: None, the relationship is dumped into
        Graph Database
        """
        destination_label = \
            self.get_destination_label()

        record_count = len(self.data)

        for index in range(record_count):
            destination_properties, source_properties = \
                self.get_properties(
                    destination_label,
                    destination_prop_label,
                    index
                )
            if is_paytv is not None:
                destination_properties[IS_PAYTV_PROPERTY_LABEL] = \
                    str(is_paytv)

            for feature, val in destination_properties.items():
                if isinstance(val, numpy.integer):
                    destination_properties[feature] = \
                        int(destination_properties[feature])

            source_node = self.get_node(
                label=USER_LABEL,
                properties=source_properties
            )
            destination_node = self.get_node(
                label=destination_label,
                properties=destination_properties
            )

            properties = {}
            for attribute in property_attributes:
                if isinstance(
                        self.data.loc[index, attribute],
                        numpy.integer
                ):
                    properties[attribute] = \
                        int(self.data.loc[index, attribute])
                else:
                    properties[attribute] = \
                        self.data.loc[index, attribute]

            print(
                "Dumping relation ", index+1,
                " of ", record_count
                )

            self.dump_relation(
                source=source_node,
                destination=destination_node,
                properties=properties
            )
