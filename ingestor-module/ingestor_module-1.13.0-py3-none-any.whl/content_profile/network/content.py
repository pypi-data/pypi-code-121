from typing import ClassVar

import pandas as pd
from graphdb import GraphDb, GraphDbConnection
from graphdb.schema import Node, Relationship

# LABEL NODE NAME & VARIABLE NAME
from ingestor.common.constants import LABEL, PROPERTIES, RELATIONSHIP, CATEGORY, SUBCATEGORY, COUNTRY, \
    CONTENT_ID, HOMEPAGE, TAGS, ACTOR, PACKAGE, CONTENT_CORE, HOMEPAGE_ID, \
    IS_CONNECTED, PAY_TV_CONTENT, NO_PAY_TV_CONTENT, YES, CONTENT_NODE, CATEGORY_ID, SUBCATEGORY_ID, COUNTRY_ID, \
    ACTOR_ID, TAGS_ID, PACKAGE_ID, CONTENT_CORE_ID
# RELATIONSHIP NAME
from ingestor.content_profile.config import content_node_properties, HAS_CATEGORY, HAS_SUBCATEGORY, HAS_COUNTRY, \
    HAS_ACTOR, HAS_TAG, HAS_PACKAGE, HAS_HOMEPAGE, HAS_CONTENT_CORE



class ContentNetworkGenerator:

    def __init__(
            self,
            connection_class: GraphDbConnection
    ):
        self.graph = GraphDb.from_connection(connection_class)

    @classmethod
    def from_connection_uri(
            cls,
            connection_uri: str
    ) -> ClassVar:
        """Create new object based on connection uri
        :param connection_uri: string connection uri
        :return: object class
        """
        return cls(GraphDbConnection.from_uri(connection_uri))

    @classmethod
    def from_connection_class(
            cls,
            connection_class: GraphDbConnection
    ) -> ClassVar:
        """Define new class based on object connection
        :param connection_class: object connection class
        :return: object class
        """
        return cls(connection_class)

    @staticmethod
    def build_content_label(home_page):
        if home_page[0].properties[IS_CONNECTED].lower() == YES:
            content_label = PAY_TV_CONTENT
        else:
            content_label = NO_PAY_TV_CONTENT
        return content_label

    def create_content_homepage_network(self, payload, homepage_content_df):
        content_nodes = []

        for index, row in homepage_content_df.iterrows():
            try:
                home_page_node_obj = Node(**{LABEL: HOMEPAGE, PROPERTIES: {HOMEPAGE_ID: int(row[HOMEPAGE_ID])}})
                home_page_node = self.graph.find_node(home_page_node_obj)

                content_label = self.build_content_label(home_page_node)
                print("Generating content to homepage network for content label {0}".format(content_label))

                for property_num, property_val in payload.iterrows():
                    content_node_dict = {}
                    if property_val[CONTENT_ID] and property_val[CONTENT_ID] is not None and \
                            property_val[CONTENT_ID] != '':

                        content_node_property = content_node_properties(property_val)
                        content_node_obj = Node(**{LABEL: content_label, PROPERTIES: content_node_property})
                        content_node = self.graph.create_node(content_node_obj)

                        self.graph.create_relationship_without_upsert(content_node, home_page_node[0], Relationship(
                            **{RELATIONSHIP: HAS_HOMEPAGE}))

                        content_node_dict[LABEL] = content_label
                        content_node_dict[HOMEPAGE_ID] = home_page_node[0].properties[HOMEPAGE_ID]
                        content_node_dict[CONTENT_ID] = content_node.properties[CONTENT_ID]
                        content_node_dict[CONTENT_NODE] = content_node
                        content_nodes.append(content_node_dict)


            except Exception:
                print('Homepage_id is no available for this content_id ', homepage_content_df)
        return content_nodes

    def child_network_generator_category(self, content_id, content_label, payload):
        try:
            for property_num, property_val in payload.iterrows():
                if property_val[CATEGORY_ID] and property_val[CATEGORY_ID] is not None and \
                        property_val[CATEGORY_ID] != '':
                    category_node_obj = Node(
                        **{LABEL: CATEGORY, PROPERTIES: {CATEGORY_ID: int(property_val[CATEGORY_ID])}})
                    category_node = self.graph.find_node(category_node_obj)

                    if len(category_node) > 0:
                        content_node_obj = Node(**{LABEL: content_label, PROPERTIES: {CONTENT_ID: int(content_id)}})
                        content_node_obj_in_graph = self.graph.find_node(content_node_obj)

                        self.graph.create_relationship_without_upsert(content_node_obj_in_graph[0], category_node[0],
                                                                      Relationship(**{RELATIONSHIP: HAS_CATEGORY}))
                    else:
                        print('Category is not available for category id = ', property_val[CATEGORY_ID])

        except Exception:
            print('Not able to add category for content id = ', content_id)

    def child_network_generator_sub_category(self, content_id, content_label, payload):
        try:
            for property_num, property_val in payload.iterrows():
                if property_val[SUBCATEGORY_ID] and property_val[SUBCATEGORY_ID] is not None and \
                        property_val[SUBCATEGORY_ID] != '':
                    sub_category_node_obj = Node(
                        **{LABEL: SUBCATEGORY, PROPERTIES: {SUBCATEGORY_ID: int(property_val[SUBCATEGORY_ID])}})
                    sub_category_node = self.graph.find_node(sub_category_node_obj)

                    if len(sub_category_node) > 0:
                        content_node_obj = Node(**{LABEL: content_label, PROPERTIES: {CONTENT_ID: int(content_id)}})
                        content_node_obj_in_graph = self.graph.find_node(content_node_obj)

                        self.graph.create_relationship_without_upsert(content_node_obj_in_graph[0],
                                                                      sub_category_node[0],
                                                                      Relationship(**{RELATIONSHIP: HAS_SUBCATEGORY}))
                    else:
                        print('Sub Category is not available for subcategory id = ', property_val[SUBCATEGORY_ID])

        except Exception:
            print('Not able to add sub category for content id = ', content_id)

    def child_network_generator_country(self, content_id, content_label, merged_with_country):
        try:
            for country_id in merged_with_country[COUNTRY_ID].values:
                if not pd.isna(country_id):
                    try:
                        country_node_obj = Node(
                            **{LABEL: COUNTRY, PROPERTIES: {COUNTRY_ID: int(country_id)}})
                        country_node = self.graph.find_node(country_node_obj)

                        if len(country_node) > 0:
                            content_node_obj = Node(**{LABEL: content_label, PROPERTIES: {CONTENT_ID: int(content_id)}})
                            content_node_obj_in_graph = self.graph.find_node(content_node_obj)

                            self.graph.create_relationship_without_upsert(content_node_obj_in_graph[0], country_node[0],
                                                                          Relationship(**{RELATIONSHIP: HAS_COUNTRY}))
                        else:
                            print('Country is not available for country id = ', country_id)
                    except Exception as e1:
                        print(e1)
                        print('Not able to add for country id = ', country_id)

        except Exception:
            print('Not able to add country for content id = ', content_id)

    def child_network_generator_actor(self, content_id, content_label, actor_content_df):
        try:
            for actor_id in actor_content_df[ACTOR_ID].values:
                if not pd.isna(actor_id):
                    try:
                        actor_node_obj = Node(
                            **{LABEL: ACTOR, PROPERTIES: {ACTOR_ID: int(actor_id)}})
                        actor_node = self.graph.find_node(actor_node_obj)

                        if len(actor_node) > 0:
                            content_node_obj = Node(**{LABEL: content_label, PROPERTIES: {CONTENT_ID: int(content_id)}})
                            content_node_obj_in_graph = self.graph.find_node(content_node_obj)

                            self.graph.create_relationship_without_upsert(content_node_obj_in_graph[0], actor_node[0],
                                                                          Relationship(**{RELATIONSHIP: HAS_ACTOR}))
                        else:
                            print('Actor is not available for actor id = ', actor_id)
                    except Exception as e1:
                        print(e1)
                        print('Not able to add actor for actor id =', actor_id)

        except Exception:
            print('Not able to add actor for content id = ', content_id)

    def child_network_generator_tag(self, content_id, content_label, tags_content_df):
        try:
            for tag_id in tags_content_df[TAGS_ID].values:
                if not pd.isna(tag_id):
                    try:
                        tag_node_obj = Node(
                            **{LABEL: TAGS, PROPERTIES: {TAGS_ID: int(tag_id)}})
                        tag_node = self.graph.find_node(tag_node_obj)

                        if len(tag_node) > 0:
                            content_node_obj = Node(**{LABEL: content_label, PROPERTIES: {CONTENT_ID: int(content_id)}})
                            content_node_obj_in_graph = self.graph.find_node(content_node_obj)
                            print('Adding relationship for tag id = ', tag_id)
                            self.graph.create_relationship_without_upsert(content_node_obj_in_graph[0], tag_node[0],
                                                                          Relationship(**{RELATIONSHIP: HAS_TAG}))
                        else:
                            print('Tag is not available for tag id = ', tag_id)
                    except Exception as e1:
                        print(e1)
                        print('Not able to add tag for tag id = ', tag_id)

        except Exception as e:
            print(e)
            print('Not able to add tag for content id = ', content_id)

    def child_network_generator_packages(self, content_id, content_label, package_df):
        try:
            package_df = package_df.drop_duplicates(subset=[PACKAGE_ID])
            for content_package_id in package_df[PACKAGE_ID].values:
                if not pd.isna(content_package_id):
                    try:
                        package_node_obj = Node(
                            **{LABEL: PACKAGE, PROPERTIES: {PACKAGE_ID: int(content_package_id)}})
                        print()
                        package_node = self.graph.find_node(package_node_obj)

                        if len(package_node) > 0:
                            content_node_obj = Node(**{LABEL: content_label, PROPERTIES: {CONTENT_ID: int(content_id)}})
                            content_node_obj_in_graph = self.graph.find_node(content_node_obj)
                            print('Adding relationship for package id = ', content_package_id)
                            self.graph.create_relationship_without_upsert(content_node_obj_in_graph[0], package_node[0],
                                                                          Relationship(**{RELATIONSHIP: HAS_PACKAGE}))
                        else:
                            print('Package is not available for package id = ', content_package_id)

                    except Exception as e1:
                        print(e1)
                        print('Not able to add package for package id = ', content_package_id)

        except Exception as e:
            print(e)
            print('Not able to add package for content id = ', content_id)

    def child_network_generator_content_core(self, content_id, content_label, content_core_content_df):
        try:
            for index, row in content_core_content_df.iterrows():
                if not pd.isna(row[CONTENT_CORE_ID]):
                    try:
                        content_core_node_obj = Node(
                            **{LABEL: CONTENT_CORE, PROPERTIES: {CONTENT_CORE_ID: int(row[CONTENT_CORE_ID])}})
                        content_core_node = self.graph.find_node(content_core_node_obj)

                        if len(content_core_node) > 0:
                            content_node_obj = Node(**{LABEL: content_label, PROPERTIES: {CONTENT_ID: int(content_id)}})
                            content_node_obj_in_graph = self.graph.find_node(content_node_obj)
                            print('Adding relationship for content core id = ', row['content_core_id'])
                            self.graph.create_relationship_without_upsert(content_node_obj_in_graph[0],
                                                                          content_core_node[0],
                                                                          Relationship(
                                                                              **{RELATIONSHIP: HAS_CONTENT_CORE}))
                        else:
                            print('Content core is not available for content core id = ', row[CONTENT_CORE_ID])

                    except Exception as e1:
                        print(e1)
                        print('Not able to add content core for content core id = ', row[CONTENT_CORE_ID])

        except Exception as e:
            print(e)
            print('Not able to add content core for content id = ', content_id)

    def content_creator_updater_network(self, payload, merged_with_country, actor_content_df, tags_content_df,
                                        homepage_content_df, content_core_content_df) -> bool:
        print("Generating content node")
        try:
            content_nodes = self.create_content_homepage_network(payload, homepage_content_df)
            if len(content_nodes) > 0:
                temp_storage = []
                for record in content_nodes:
                    content_label = record[LABEL]
                    content_id = record[CONTENT_ID]
                    content_homepage_id = record[HOMEPAGE_ID]
                    content_node = record[CONTENT_NODE]
                    if content_node not in temp_storage:
                        print(
                            "Generating content to category network with content ID = {0}".format(
                                payload[CONTENT_ID].loc[0]))
                        self.child_network_generator_category(content_id, content_label, payload)
                        print(
                            "Generating content to subcategory network with content ID = {0}".format(
                                payload[CONTENT_ID].loc[0]))
                        self.child_network_generator_sub_category(content_id, content_label, payload)
                        print(
                            "Generating content to country network with content ID = {0}".format(
                                payload[CONTENT_ID].loc[0]))
                        self.child_network_generator_country(content_id, content_label, merged_with_country)

                        print(
                            "Generating content to actor network with content ID = {0}".format(
                                payload[CONTENT_ID].loc[0]))
                        self.child_network_generator_actor(content_id, content_label, actor_content_df)

                        print("Generating content to tag network with content ID = {0}".format(
                            payload[CONTENT_ID].loc[0]))
                        self.child_network_generator_tag(content_id, content_label, tags_content_df)
                        print(
                            "Generating content to content core network with content ID = {0}".format(
                                payload[CONTENT_ID].loc[0]))
                        self.child_network_generator_content_core(content_id, content_label, content_core_content_df)

                        temp_storage.append(content_node)
            else:
                print("No content node is available for content ID = {0}".format(payload[CONTENT_ID].loc[0]))
        except Exception as e:
            print(e)
            print('Faced issue while adding content id {0} into network'.format(payload[CONTENT_ID].loc[0]))
        return True

