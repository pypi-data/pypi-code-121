__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

import compspec.entity as entity


class GraphGroup:
    """
    A graph group is intended to hold and yield named graphs.
    """

    def __init__(self):
        self.graphs = {}
        self.extract()

    def __contains__(self, name):
        return name in self.graphs

    def __iter__(self):
        for group, graph in self.graphs.items():
            yield group, graph

    def __getitem__(self, name):
        return self.graphs.get(name)

    def extract(self):
        raise NotImplementedError


class Graph:
    """
    A graph implicitly is scoped to one namespace
    """

    def __init__(self):

        # A counter to keep track of ids in this space
        self.count = entity.get_counter()
        self.ids = {}
        self.nodes = {}
        self.lookup = {}
        self.relations = []

    def to_dict(self):
        """
        Output dictionary representation of nodes and relations.
        """
        return {
            "nodes": [v.to_dict() for _, v in self.nodes.items()],
            "relations": [x.to_dict() for x in self.relations],
        }

    @classmethod
    def from_dict(self, obj):
        """
        Return a new graph loaded from a dictionary.
        """
        nodes = obj.get("nodes", [])
        relations = obj.get("relations", [])
        g = Graph()
        [g.new_node(**x) for x in nodes]
        [g.new_relation(**x) for x in relations]
        return g

    def next(self):
        """
        Return next id in the counter.
        """
        return next(self.count)

    def add_node(self, node):
        """
        Add an already generated node.
        """
        self.nodes[f"{node.nodeid}"] = node

    def add_relation(self, relation):
        """
        Add an already generated relation.
        """
        # We keep a full "identifier" for each, to provide meaning later
        # The toid should not be in the lookup, each node has only one parent
        toid = self.nodes[relation.toid].describe()
        if relation.fromid in self.lookup:
            fromid = self.lookup[relation.fromid]
        else:
            fromid = self.nodes[relation.fromid].describe()

        toid = f"{fromid}->{toid}"
        self.lookup[relation.toid] = toid
        self.relations.append(relation)

    def new_node(self, name, value, nodeid=None, is_connector=False):
        """
        Generate a node with a name (type) and value

        is_connector is a flag that indicates the node is included in the graph,
        but itself should not be assessed for add/change/remove.
        """
        if not nodeid:
            nodeid = self.next()
        node = entity.node(nodeid, name=name, value=value, is_connector=is_connector)
        self.add_node(node)
        return node

    def new_relation(self, fromid, relation, toid):
        """
        Generate a relation between parent (fromid) and child (toid).
        The relation here does not hard code a namespace, but it will
        be required to compare between two graphs.
        """
        relation = entity.relation(fromid=fromid, toid=toid, relation=relation)
        self.add_relation(relation)
        return relation

    def gen(self, name, value, parent, nodeid=None, relation="has", is_connector=False):
        """
        Generate a node and relation in one swoop!
        A parent is required.
        """
        if not nodeid:
            nodeid = self.next()
        node = entity.node(
            nodeid=nodeid, name=name, value=value, is_connector=is_connector
        )
        self.add_node(node)
        relation = self.new_relation(fromid=parent, toid=node.nodeid, relation=relation)
        self.add_relation(relation)
        return node, relation

    def iter_connectors(self):
        """
        Yield connector nodes only
        """
        for _, node in self.nodes.items():
            if node.is_connector:
                yield node.args[0]

    def iter_nodes(self):
        """
        Yield nodes. If a comparison is being done, a namespace needs to be
        added (e.g., node, namespace, *args)
        """
        for _, node in self.nodes.items():
            yield node.args

    def iter_relations(self):
        """
        Yield relations in the same manner.
        """
        for relation in self.relations:
            yield relation.args
