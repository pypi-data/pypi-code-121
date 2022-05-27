from typing import List, Any, ClassVar

from graphdb.connection import GraphDbConnection
from graphdb.graph import GraphDb
from graphdb.schema import Node
from ingestor.common.constants import CATEGORY_EN, COUNTRY_DESCRIPTION, COUNTRY_NAME, \
    SUBCATEGORY_EN, LABEL, PROPERTIES, SEASON_NAME, HOMEPAGE_TITLE, HOMEPAGE_TYPE, HOMEPAGE_STATUS, \
    HOMEPAGE_TITLE_EN, DEFAULT_NUM, DEFAULT_NAN, ACTOR_NAME, TAGS_NAME, PAYTVPROVIDER_NAME, PRODUCT_NAME, \
    PRODUCT_NAME_EN, PACKAGE_NAME, PACKAGE_NAME_EN, CONTENT_CORE_TITLE, CONTENT_CORE_EPISODE, CONTENT_CORE_SYNOPSIS
from ingestor.common.preprocessing_utils import Utils
from pandas import DataFrame


class StaticNodeGenerator(Utils):

    def __init__(
            self,
            data: DataFrame,
            label: str,
            graph_connection_class: GraphDbConnection
    ):
        """
        Accept the dataframe such that each
        record represents a node of label
        passed as input and each column is
        it's property

        :param data: dataframe object pandas
        :param label: node label for all
        records in input df
        """
        self.data = data
        self.node_label = label
        self.graph = GraphDb.from_connection(graph_connection_class)

    @classmethod
    def new_connection(
            cls,
            data: DataFrame,
            label: str,
            connection_uri: str
    ) -> ClassVar:
        """Initialize new connection to current class
        :param data: dataframe object pandas
        :param label: node label for all
        :param connection_uri: string connection uri
        :return: current object
        """
        return cls(data, label, GraphDbConnection.from_uri(connection_uri))

    def filter_properties(
            self,
            to_keep: List
    ):
        """
        Filters the input dataframe to keep only
        the specified fields

        :param to_keep: list of attributes
        to proceed with
        :return: None, simply updates the
        instance data member
        """
        self.data = self.data[to_keep]

    def preprocess_property(
            self,
            node_property: str,
            node_default_val: Any
    ) -> bool:
        """
        Preprocess the passed node property
        using the common preprocessing script

        :param node_property: dataframe field name
        :param node_default_val: default value to
        assign in case of missing or NaN/nan values
        :return: None, simply updates the instance
        data member field values
        """
        if node_property not in self.data.columns:
            return False

        self.data = self.fillna_and_cast_lower(data=self.data, feature=node_property, default_val=node_default_val)
        return True

    def dump_nodes(
            self
    ) -> bool:
        """
        Dump the dataframe records as
        individual nodes into GraphDB
        :return: Dumped nodes
        """
        nodes = []
        for record in self.data.to_dict(
                orient="records"):
            node = Node(
                **{
                    LABEL: self.node_label,
                    PROPERTIES: record
                })
            nodes.append(node)

        return self.graph.create_multi_node(
            nodes)

    def category_controller(
            self,
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating category nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=CATEGORY_EN,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def subcategory_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating subcategory nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=SUBCATEGORY_EN,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def homepage_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating homepage nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(node_property=HOMEPAGE_TITLE, node_default_val=DEFAULT_NAN)
        self.preprocess_property(node_property=HOMEPAGE_TITLE_EN, node_default_val=DEFAULT_NAN)
        self.preprocess_property(node_property=HOMEPAGE_STATUS, node_default_val=DEFAULT_NAN)
        self.preprocess_property(node_property=HOMEPAGE_TYPE, node_default_val=DEFAULT_NAN)
        self.dump_nodes()
        return True

    def actor_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating actor nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=ACTOR_NAME,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def tags_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating tags nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=TAGS_NAME,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def country_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating country nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=COUNTRY_NAME,
            node_default_val=DEFAULT_NAN
        )
        self.preprocess_property(
            node_property=COUNTRY_DESCRIPTION,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def paytv_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating PayTV Provider nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=PAYTVPROVIDER_NAME,
            node_default_val=DEFAULT_NUM
        )
        self.dump_nodes()
        return True

    def product_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating product  nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=PRODUCT_NAME,
            node_default_val=DEFAULT_NAN
        )
        self.preprocess_property(
            node_property=PRODUCT_NAME_EN,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def package_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating package nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=PACKAGE_NAME,
            node_default_val=DEFAULT_NAN
        )
        self.preprocess_property(
            node_property=PACKAGE_NAME_EN,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def season_controller(
            self
    ) -> bool:
        """
        Driver function for preparing meta-data
        for creating season nodes
        :return: None, simply updates the
        instance data member
        """
        self.preprocess_property(
            node_property=SEASON_NAME,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def content_core_controller(self) -> bool:
        self.preprocess_property(
            node_property=CONTENT_CORE_TITLE,
            node_default_val=DEFAULT_NAN
        )
        self.preprocess_property(
            node_property=CONTENT_CORE_EPISODE,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

    def content_core_synopsis_controller(self) -> bool:
        self.preprocess_property(
            node_property=CONTENT_CORE_SYNOPSIS,
            node_default_val=DEFAULT_NAN
        )
        self.dump_nodes()
        return True

