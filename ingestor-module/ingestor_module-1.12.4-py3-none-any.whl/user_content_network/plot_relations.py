from ingestor.common.constants import USER_CONTENT_RELATIONSHIP_LABEL, \
    CONTENT_ID, CUSTOMER_ID, USER_LABEL, RELATIONSHIP, STATUS, \
    VIEW_COUNT, VIEW_HISTORY, CREATE, UPDATE
from ingestor.user_profile.network.plot_relations import PlotRelations
from graphdb.schema import Node
from ingestor.common.constants import LABEL, PROPERTIES
from pandas import DataFrame
from graphdb.schema import Relationship


class UCNetworkGenerator(PlotRelations):

    def __init__(
            self,
            data: DataFrame,
            connection_uri
    ):
        """
        Calls the parent class used in user profile
        network generation.
        :param data: dataframe object pandas
        :param connection_uri: graphDB connection URI
        """
        PlotRelations.__init__(
            self,
            data=data,
            label=USER_CONTENT_RELATIONSHIP_LABEL,
            connection_uri=connection_uri
        )

    def filter_features(
            self,
            key: str
    ):
        """
        Filters to keep only the required fields
        :param key: Column to be passed
        :return: None, simply updates the state of
        instance data member
        """

        self.data = self.data[[CUSTOMER_ID,
                               key]]

    def get_viewed_relation_count(
            self,
            customer_id: str,
            content_key: str,
            content_id: int
    ):
        """
        Use custom query to retrieve information regarding
        user-content VIEWED relationship for the considered
        customer_id and content_id
        :param customer_id: string customer_id
        :param content_key: paytv status of content
        :param content_id: string content_id
        :return: list of values
        """
        response = self.graph.custom_query(

            query=f'''g.V().hasLabel('{USER_LABEL}')
            .has('{CUSTOMER_ID}','{customer_id}').outE()
            .hasLabel('{USER_CONTENT_RELATIONSHIP_LABEL}')
            .inV().hasLabel('{content_key}')
            .has('{CONTENT_ID}',{content_id})
            .path().by(elementMap())''',

            payload={
                     USER_LABEL: USER_LABEL,
                     CUSTOMER_ID: CUSTOMER_ID,
                     customer_id: customer_id,
                     USER_CONTENT_RELATIONSHIP_LABEL:
                     USER_CONTENT_RELATIONSHIP_LABEL,
                     content_key: content_key,
                     CONTENT_ID: CONTENT_ID,
                     content_id: str(content_id)
                     }
        )
        if len(response) == 0:
            return 0, []
        view_history = list(eval(response[0][0][1][VIEW_HISTORY]))
        return response[0][0][1][VIEW_COUNT], \
            view_history

    def reformat_attribute_datatypes(
            self
    ):
        """
        Manipulate data types of attributes
        to be passed as relationship properties
        :return: None, updates the state of the
        data member of the instance
        """
        self.data[VIEW_HISTORY] = \
            self.data[VIEW_HISTORY].astype(str)

    def identify_create_update_relations(
            self,
            key: str
    ):
        """
        Assign each user-content relation a label
        out of { 'create', 'update' }. If a relation
        already exists in the network, it is labeled
        as update, else create
        :param key: paytv status of the content
        :return: None, updates the state of the
        data member of the instance
        """
        record_count = len(self.data)
        for index in range(record_count):
            print("Checking status of record ",
                  index+1, " of ", record_count)

            customer_id = self.data.loc[index, CUSTOMER_ID]
            content_id = self.data.loc[index, key]

            existing_view_count, existing_view_history = \
                self.get_viewed_relation_count(
                    customer_id=customer_id,
                    content_key=key,
                    content_id=content_id
                )

            self.data.loc[index, VIEW_COUNT] = int(
                self.data.loc[index, VIEW_COUNT] +
                existing_view_count
            )

            if existing_view_count == 0:
                self.data.loc[index, STATUS] = CREATE
            else:
                existing_view_history.extend(self.data.loc[index, VIEW_HISTORY])
                self.data.at[index, VIEW_HISTORY] = existing_view_history
                self.data.loc[index, STATUS] = UPDATE

    def split_relations_on_status(
            self
    ):
        """
        Splits a single dataframe object into 2
        sub-components based on the status of the
        relationship
        :return: A set of two dataframe objects pandas
        """
        create_relations_df = self.data[self.data[STATUS] == CREATE]
        update_relations_df = self.data[self.data[STATUS] == UPDATE]
        return create_relations_df.reset_index(drop=True), \
            update_relations_df.reset_index(drop=True)

    def retrieve_node(
            self,
            label: str,
            properties: dict,
            db_graph
    ):
        """
        Find a node in GraphDB. If that node
        exists, return the corresponding node
        object, else return None
        :param label: node label string
        :param properties: dictionary object
        for node properties
        :param db_graph: graphDB object
        :return: Node object is node exists,
         else None
        """
        node = Node(
            **{
                LABEL: label,
                PROPERTIES: properties
            }
        )
        node_in_graph = \
            db_graph.find_node(node)
        if len(node_in_graph) > 0:
            return node_in_graph[0]
        return None

    def update_existing_relations(
            self,
            data: DataFrame,
            key: str
    ):
        """
        Updates the existing set of relations with
        new respective property values
        :param data: dataframe object pandas
        :param key: paytv status of contents
        :return: None, plots the relationships
        in graphDB
        """
        record_count = len(data)

        for index in range(record_count):
            print("Updating existing relationship record ",
                  index + 1, " of ", record_count)

            user_node = self.retrieve_node(
                label=USER_LABEL,
                properties={CUSTOMER_ID:
                            data.loc[index, CUSTOMER_ID]},
                db_graph=self.graph
            )

            content_node = self.retrieve_node(
                label=key,
                properties={CONTENT_ID:
                            int(data.loc[index, key])},
                db_graph=self.graph
            )

            self.graph.replace_relationship_property(
                rel=Relationship(
                 **{
                    RELATIONSHIP: self.rel_label
                 }),
                update_query={VIEW_COUNT:
                              int(data.loc[index, VIEW_COUNT]),
                              VIEW_HISTORY:
                              data.loc[index, VIEW_HISTORY]
                              },
                node_from=user_node,
                node_to=content_node
            )

    def create_relationships(
            self,
            key: str
    ):
        """
        Generate relationships between user and
        content nodes using the controller function
        of parent class
        :param key: Column to be passed
        :return: None, simply updates the state of graphDB
        """
        #self.filter_features(key=key)
        self.identify_create_update_relations(key=key)
        self.reformat_attribute_datatypes()
        self.data, update_df = self.split_relations_on_status()
        if len(update_df) > 0:
            self.update_existing_relations(
                data=update_df,
                key=key
            )
        self.controller(
            destination_prop_label=CONTENT_ID,
            property_attributes=[VIEW_COUNT, VIEW_HISTORY]
        )
