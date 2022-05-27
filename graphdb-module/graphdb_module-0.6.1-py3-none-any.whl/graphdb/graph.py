import os
import string
from typing import ClassVar, List, Dict, Any, Callable, Optional, Union, Iterator

from gremlin_python.process.graph_traversal import __, GraphTraversalSource
from gremlin_python.process.traversal import T, within

from graphdb.connection import GraphDbConnection
from graphdb.interface.custom_query_iface import CustomQueryInterface
from graphdb.interface.node_create_constraint_iface import NodeCreateConstraintInterface
from graphdb.interface.node_create_iface import NodeCreateInterface
from graphdb.interface.node_create_index_iface import NodeCreateIndexInterface
from graphdb.interface.node_delete_iface import NodeDeleteInterface
from graphdb.interface.node_search_iface import NodeSearchInterface
from graphdb.interface.node_update_iface import NodeUpdateInterface
from graphdb.interface.rel_create_iface import RelationshipCreateInterface
from graphdb.interface.rel_delete_iface import RelationshipDeleteInterface
from graphdb.interface.rel_update_iface import RelationshipUpdateInterface
from graphdb.schema import Node, Relationship
from graphdb.utils import log_execution_time


class GraphDb(
    NodeCreateInterface,
    NodeSearchInterface,
    NodeUpdateInterface,
    NodeDeleteInterface,
    RelationshipCreateInterface,
    RelationshipUpdateInterface,
    RelationshipDeleteInterface,
    NodeCreateConstraintInterface,
    NodeCreateIndexInterface,
    CustomQueryInterface,
):
    """This will inherit to child class
    and sure you can create another method to support your application"""

    def __init__(
        self,
        connection: GraphDbConnection,
        path_data: str = None,
    ):
        self.connection = connection
        self.path_data = path_data
        self.vertex_id = T.id
        self.vertex_label = T.label
        self.default_timeout = int(os.getenv("CUSTOM_QUERY_TIMEOUT", 20))
        NodeCreateInterface.__init__(self)
        NodeSearchInterface.__init__(self)
        NodeUpdateInterface.__init__(self)
        NodeDeleteInterface.__init__(self)
        RelationshipCreateInterface.__init__(self)
        RelationshipDeleteInterface.__init__(self)
        NodeCreateConstraintInterface.__init__(self)
        NodeCreateIndexInterface.__init__(self)
        CustomQueryInterface.__init__(self)

    @classmethod
    def from_connection(
        cls,
        connection: GraphDbConnection,
    ) -> ClassVar:
        """Create class object from object connection class
        :param connection: string connection uru
        :return: current object class
        """
        return cls(connection)

    @log_execution_time
    def custom_query(
        self, query: str, payload: Dict[str, Any] = None, callback_func: Callable = None
    ) -> List[Dict[str, Any]]:
        """Execute string query based on parameters
        :param query: string query
        :param payload: dictionary binding to query
        :param callback_func: callback function to wrap result
        :return: List of dictionary
        """
        # if any drop syntax query
        if (
            "drop" in query.lower()
            or any(p.lower() == "drop" for p in payload.keys())
            or any(p.lower() == "drop" for p in payload.values())
        ):
            raise Exception("custom query doesn't allow drop")

        if payload is None and "limit" not in query.lower():
            raise Exception(
                "please provide parameter for filter in query, at least limit records 😀"
            )

        # if any payload or binding data so it need to replace to template string
        # example is something like this
        # query = "g.V().has("name", ${name}).next()"
        # and payload will be like this payload = {"name": "Andy"}
        if payload is not None and len(payload) > 0:
            query = string.Template(query).safe_substitute(payload)

        res = self.connection.submit_async(query)
        # if client define callback function then passing result to that function
        # please note we need to add proper try catch
        if callback_func is not None:
            # callback function to client
            func = callback_func(res)
            # return result
            return func

        # otherwise use default query and fetch result with default timeout
        try:
            # wait for 10 seconds for response
            result = res.result(timeout=self.default_timeout)
        except TimeoutError:
            result = []

        # return response
        return list(result)

    @log_execution_time
    def create_index(
        self,
        node: Node,
        index_name: str,
    ) -> bool:
        """Create new constraint based on specified properties
        :param node: object node
        :param index_name: string index name
        :return: boolean true or false
        """
        raise NotImplementedError

    @log_execution_time
    def create_constraint(
        self,
        node: Node,
        properties: List[str],
        is_unique: bool = False,
        not_null: bool = False,
    ) -> bool:
        """Create new constraint based on specified properties
        :param node: object node
        :param properties: list of property
        :param is_unique: is constraint is unique
        :param not_null: is constraint is not null
        :return: boolean true or false
        """
        raise NotImplementedError

    def _map_value(self, docs: List[Dict[str, Any]]) -> List[Node]:
        """Convert gremlin query list of object to list of object node
        :param docs: list of dictionary data
        :return: list of nodes
        """
        t = []
        for v in docs:
            _id = v.pop(self.vertex_id, None)
            label = v.pop(self.vertex_label, None)
            t.append(Node.parse_obj({"id": _id, "label": label, "properties": v}))

        return t

    def _get_node_value_from_node_param(self, node: Node) -> GraphTraversalSource.V:
        """Get node object from gremlin from node parameters
        :param node: object node that pass from user parameters
        :return: object gremlin traversal source
        """
        # search node
        sn = self.connection.driver_reader
        if not node.id:
            sn = sn.V()
            if node.label:
                sn = sn.hasLabel(node.label)

            if node.properties:
                for k, v in node.properties.items():
                    sn.has(k, v)
        else:
            # otherwise search based on id
            sn = sn.V(node.id)

        return sn

    @log_execution_time
    def find_node(
        self,
        node: Node,
        limit: int = 100,
    ) -> List[Node]:
        """Find node with specified parameters
        :param node: object node
        :param limit: default limit query
        :return: list of object node
        """
        # if object not provide id then use their property
        s = self._get_node_value_from_node_param(node)
        nodes = self._map_value(s.elementMap().toList())
        return nodes

    @log_execution_time
    def find_node_within(
        self,
        label_name: str,
        key_name: str,
        value: Union[List[str], List[int], List[float]],
    ) -> List[Node]:
        """Find node with specified parameters with multiple filter
        :param label_name: string label name for that node
        :param key_name: string key that we want to search
        :param value: it can be primitive data type, value that we want to search
        :return: list of object node
        """
        # if object not provide id then use their property
        s = self.connection.driver_reader.V()
        # if node doesn't have id then search based on property
        s.hasLabel(label_name).has(key_name, within(*value))
        nodes = self._map_value(s.elementMap().toList())
        return nodes

    @log_execution_time
    def create_node(self, node: Node) -> Node:
        """Create new node with label and properties if set in node class
        it will search node, if exists then update that node only
        see this for example
        # http://www.kelvinlawrence.net/book/PracticalGremlin.html#upsert
        :param node: object node
        :return: object node
        """
        s = self.connection.driver_writer.V().hasLabel(node.label)
        # doing upsert when node is exists then update otherwise is create
        update_val = __.unfold()
        create_val = __.addV(node.label)
        # if any property then assign to it
        if node.properties:
            for k, v in node.properties.items():
                s.has(k, v)
                update_val.property(k, v)
                create_val.property(k, v)

        res = s.fold().coalesce(update_val, create_val)
        # assign exists id to current node
        node.id = res.next().id
        return node

    @staticmethod
    def _chunks(lst: List[Node], n: int) -> Iterator[List[Node]]:
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    @log_execution_time
    def create_multi_node(self, nodes: List[Node]) -> bool:
        """Create multiple node with label and properties if set in node class,
        this will doing upsert value
        :param nodes: list of object node
        :return: boolean value
        """
        g = self.connection.driver_writer
        # define maximum chunking value
        max_chunking_value = int(os.getenv("MAX_CHUNKS", 100))
        # adding all chunking value to queue
        for data in self._chunks(nodes, max_chunking_value):
            # loop one by one inside data
            while data:
                node = data.pop()
                g = g.V().hasLabel(node.label)

                # doing upsert when node is exists then update otherwise is create
                update_val = __.unfold()
                create_val = __.addV(node.label)
                # if any property then assign to it
                if node.properties:
                    for k, v in node.properties.items():
                        g.has(k, v)
                        update_val.property(k, v)
                        create_val.property(k, v)

                g = g.fold().coalesce(update_val, create_val)
            # save to database
            g.iterate()

        return True

    @log_execution_time
    def update_node_property(self, node: Node, update_query: Dict[str, Any]) -> Node:
        """Update node with specified properties
        :param node: object class node
        :param update_query: dictionary filter query
        :return: object node
        """
        s = self._get_node_value_from_node_param(node)
        for k, v in update_query.items():
            s.property(k, v)

        s = s.next()
        # assign node id to current object
        node.properties.update(update_query)
        node.id = s.id
        return node

    @log_execution_time
    def replace_node_property(self, node: Node, update_query: Dict[str, Any]) -> Node:
        """Replace node properties with new properties
        :param node: object class node
        :param update_query: dictionary filter query
        :return: object node
        """
        # get node id
        node = self._get_node_value_from_node_param(node)
        # get node id
        node_id = node.next().id
        # remove properties
        self.connection.driver_writer.V(node_id).properties().drop().iterate()
        # assign new property
        new_prop = self.connection.driver_writer.V(node_id)
        for k, v in update_query.items():
            new_prop.property(k, v)

        new_prop = new_prop.next()

        # assign node id to current object
        node.properties = update_query
        node.id = new_prop.id
        return node

    @log_execution_time
    def remove_node_property(self, node: Node, properties: List[str]) -> Node:
        """Remove specified property from node
        :param node: object node
        :param properties: list of property you want to remove from this node
        :return: object node
        """
        s = self._get_node_value_from_node_param(node)
        # get node id
        node_id = s.next().id
        # delete specified properties
        self.connection.driver_writer.V(node_id).properties(
            *properties
        ).drop().iterate()
        # remove property from payload
        if node.properties:
            _ = [node.properties.pop(val, None) for val in properties]
        # assign object node to early id
        node.id = node_id
        return node

    @log_execution_time
    def remove_all_node_property(self, node: Node) -> Node:
        """Remove all property from this node
        :param node: object node
        :return: object node
        """
        s = self._get_node_value_from_node_param(node)
        # get node id
        node_id = s.next().id
        # delete all properties
        self.connection.driver_writer.V(node_id).properties().drop().iterate()
        # assign node id to current object node
        node.id = node_id
        # set current property to null
        node.properties = None
        return node

    @log_execution_time
    def delete_node_with_relationship(self, node: Node) -> Node:
        """Delete for specified node object, please note this will remove node with all relationship on it
        :param node: object node that we want to delete
        :return: object node
        """
        return self.delete_node(node)

    @log_execution_time
    def delete_node(self, node: Node) -> Node:
        """Delete for specified node object, it will leave relationship as it is
        :param node: object node that we want to delete
        :return: object node
        """
        s = self._get_node_value_from_node_param(node)
        # get node id
        node_id = s.next().id
        # delete current node
        self.connection.driver_writer.V(node_id).drop().iterate()
        # assign node id to current object node
        node.id = node_id
        # set current property to null
        node.properties = None
        return node

    @log_execution_time
    def create_relationship_without_upsert(
        self, node_from: Node, node_to: Node, rel: Relationship
    ) -> Relationship:
        """Create new relationship between 2 nodes
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship with name
        :return: object relationship
        """
        # node from
        f = self._get_node_value_from_node_param(node_from)
        # get node from id
        n_f = f.next().id

        # node to
        t = self._get_node_value_from_node_param(node_to)
        # get node to id
        n_t = t.next().id

        # get result
        res = (
            self.connection.driver_writer.V(n_f)
            .addE(rel.relationship_name)
            .to(__.V(n_t))
        )

        # if any property then assign to it edge
        if rel.properties:
            for k, v in rel.properties.items():
                res.property(k, v)

        rel.id = res.next().id
        return rel

    @log_execution_time
    def create_relationship_with_upsert(
        self, node_from: Node, node_to: Node, rel: Relationship
    ) -> Relationship:
        """Create new relationship between 2 nodes
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship with name
        :return: object relationship
        """
        # node from
        f = self._get_node_value_from_node_param(node_from)
        # get node from id
        n_f = f.next().id

        # node to
        t = self._get_node_value_from_node_param(node_to)
        # get node to id
        n_t = t.next().id

        # check if relationships is exists
        e = self.connection.driver_writer.V(n_f).outE().hasLabel(rel.relationship_name)
        update_val = __.unfold()
        create_val = __.V(n_f).addE(rel.relationship_name).to(__.V(n_t))
        # if any property then assign to it edge
        if rel.properties:
            for k, v in rel.properties.items():
                e.has(k, v)
                update_val.property(k, v)
                create_val.property(k, v)

        res = e.where(__.V().hasId(n_t)).fold().coalesce(update_val, create_val)
        rel.id = res.next().id
        return rel

    @log_execution_time
    def update_relationship_property(
        self,
        rel: Relationship,
        update_query: Dict[str, Any],
        node_from: Node = None,
        node_to: Node = None,
    ) -> Relationship:
        """Update relationship with specified properties
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object class relationship
        :param update_query: dictionary filter query
        :return: object relationship
        """
        # if we want to delete relationship by id then search only relationship id
        if rel.id is not None:
            # update current property with new property
            n_e = self.connection.driver_writer.E(rel.id)
            for k, v in update_query.items():
                n_e.property(k, v)
            n_e.iterate()
            rel.properties.update(update_query)
            return rel

        # otherwise search based in node from and node to
        # node from
        f = self._get_node_value_from_node_param(node_from)
        # get node from id
        n_f = f.next().id

        # node to
        t = self._get_node_value_from_node_param(node_to)
        # get node to id
        n_t = t.next().id

        # search edge based on name
        # node relationship
        n_rel = (
            self.connection.driver_writer.V(n_f).outE().hasLabel(rel.relationship_name)
        )

        # if edge has property then filter based on specified property
        if rel.properties:
            for k, v in rel.properties.items():
                n_rel.has(k, v)

        n_rel.where(__.V().hasId(n_t))
        # get rel id
        rel_id = n_rel.next().id
        # update old property with current property
        n_e = self.connection.driver_writer.E(rel_id)
        for k, v in update_query.items():
            n_e.property(k, v)
        # update query
        n_e.iterate()
        # set relationship id
        rel.id = rel_id
        # set property to new property
        rel.properties.update(update_query)
        return rel

    @log_execution_time
    def replace_relationship_property(
        self,
        rel: Relationship,
        update_query: Dict[str, Any],
        node_from: Optional[Node] = None,
        node_to: Optional[Node] = None,
    ) -> Relationship:
        """Replace relationship properties with new properties
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object class relationship
        :param update_query: dictionary filter query
        :return: object relationship
        """
        # if we want to delete relationship by id then search only relationship id
        if rel.id is not None:
            self.connection.driver_writer.E(rel.id).properties().drop().iterate()
            # set new property
            n_e = self.connection.driver_writer.E(rel.id)
            for k, v in update_query.items():
                n_e.property(k, v)
            n_e.iterate()
            rel.properties = update_query
            return rel

        # otherwise search based in node from and node to
        # node from
        f = self._get_node_value_from_node_param(node_from)
        # get node from id
        n_f = f.next().id

        # node to
        t = self._get_node_value_from_node_param(node_to)
        # get node to id
        n_t = t.next().id

        # search edge based on name
        n_rel = (
            self.connection.driver_writer.V(n_f).outE().hasLabel(rel.relationship_name)
        )

        # if edge has property then filter based on specified property
        if rel.properties:
            for k, v in rel.properties.items():
                n_rel.has(k, v)

        n_rel.where(__.V().hasId(n_t))
        # get rel id
        rel_id = n_rel.next().id
        # delete current edge based on specified properties
        self.connection.driver_writer.E(rel_id).properties().drop().iterate()
        # create new property from current rel id
        n_e = self.connection.driver_writer.E(rel_id)
        for k, v in update_query.items():
            n_e.property(k, v)
        # update query
        n_e.iterate()
        # assign id to current relationship
        rel.id = rel_id
        # set property to new property
        rel.properties = update_query
        return rel

    @log_execution_time
    def remove_all_relationship_property(
        self,
        rel: Relationship,
        node_from: Optional[Node] = None,
        node_to: Optional[Node] = None,
    ) -> Relationship:
        """Remove all property from this relationship
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object node
        :return: object relationship
        """
        # if we want to delete relationship by id then search only relationship id
        if rel.id is not None:
            self.connection.driver_writer.E().hasId(
                rel.id
            ).properties().drop().iterate()
            # set current property to null
            rel.properties = None
            return rel

        # otherwise search based in node from and node to
        # node from
        f = self._get_node_value_from_node_param(node_from)
        # get node from id
        n_f = f.next().id

        # node to
        t = self._get_node_value_from_node_param(node_to)
        # get node to id
        n_t = t.next().id

        # search edge based on name
        n_rel = (
            self.connection.driver_writer.V(n_f).outE().hasLabel(rel.relationship_name)
        )

        # if edge has property then filter based on specified property
        if rel.properties:
            for k, v in rel.properties.items():
                n_rel.has(k, v)

        n_rel.where(__.V().hasId(n_t))
        # get rel id
        rel_id = n_rel.next().id
        # delete current edge based on specified properties
        self.connection.driver_writer.E(rel_id).properties().drop().iterate()
        # assign rel id to current object rel
        rel.id = rel_id
        # set current property to null
        rel.properties = None
        return rel

    @log_execution_time
    def remove_relationship_property(
        self,
        rel: Relationship,
        properties: List[str],
        node_from: Optional[Node] = None,
        node_to: Optional[Node] = None,
    ) -> Relationship:
        """Remove specified property from relationship
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship
        :param properties: list of property you want to remove from this relationship
        :return: object relationship
        """
        # if we want to delete relationship by id then search only relationship id
        if rel.id is not None:
            self.connection.driver_writer.E(rel.id).hasId(rel.id).properties(
                *properties
            ).drop().iterate()
            # remove property from payload
            if rel.properties:
                _ = [rel.properties.pop(val, None) for val in properties]
            return rel

        # otherwise search based in node from and node to
        # node from
        f = self._get_node_value_from_node_param(node_from)
        # get node from id
        n_f = f.next().id

        # node to
        t = self._get_node_value_from_node_param(node_to)
        # get node to id
        n_t = t.next().id

        # search edge based on name
        n_rel = (
            self.connection.driver_writer.V(n_f).outE().hasLabel(rel.relationship_name)
        )

        # if edge has property then filter based on specified property
        if rel.properties:
            for k, v in rel.properties.items():
                n_rel.has(k, v)

        n_rel.where(__.V().hasId(n_t))
        # get rel id
        n_id = n_rel.next().id
        # delete current edge based on specified properties
        self.connection.driver_writer.E(n_id).properties(*properties).drop().iterate()
        # remove property from payload
        if rel.properties:
            _ = [rel.properties.pop(val, None) for val in properties]
        # assign rel id to current object rel
        rel.id = n_id
        # return node
        return rel

    @log_execution_time
    def delete_relationship(
        self,
        rel: Relationship,
        node_from: Optional[Node] = None,
        node_to: Optional[Node] = None,
    ) -> Relationship:
        """Delete only relationship from specified node
        :param node_from: object node from
        :param node_to: object node to
        :param rel: object relationship with name
        :return: object relationship
        """
        # if we want to delete relationship by id then search only relationship id
        if rel.id is not None:
            self.connection.driver_writer.E(rel.id).drop().iterate()
            # remove edges from database
            rel.properties = None
            return rel

        # node from
        f = self._get_node_value_from_node_param(node_from)
        # get node from id
        n_f = f.next().id

        # node to
        t = self._get_node_value_from_node_param(node_to)
        # get node to id
        n_t = t.next().id

        # search edge based on name
        # node relationships
        n_rel = (
            self.connection.driver_writer.V(n_f).outE().hasLabel(rel.relationship_name)
        )

        # if edge has property then filter based on specified property
        if rel.properties:
            for k, v in rel.properties.items():
                n_rel.has(k, v)

        n_rel.where(__.V().hasId(n_t))
        # get rel id
        n_id = n_rel.next().id
        # delete current node
        self.connection.driver_writer.E(n_id).drop().iterate()
        # assign rel id to current object rel
        rel.id = n_id
        # set current property to null
        rel.properties = None
        return rel
