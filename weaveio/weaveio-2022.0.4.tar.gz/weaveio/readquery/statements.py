from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from weaveio.readquery.parser import QueryGraph


class Statement:
    default_ids = ['inputs', '__class__']
    ids = []

    def __init__(self, input_variables, graph: 'QueryGraph'):
        self.inputs = input_variables
        self.output_variables = []
        self._edge = None
        self.graph = graph

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return hash(self) == hash(o)

    def __hash__(self):
        ids = self.ids + self.default_ids
        obs = (getattr(self, i) for i in ids)
        obs = map(lambda x: tuple(x) if isinstance(x, list) else x, obs)
        return hash(tuple(map(hash, obs)))

    @property
    def edge(self):
        return self._edge

    @edge.setter
    def edge(self, value):
        self._edge = value
        self.graph.G.nodes[self._edge[1]]['variables'] = self.output_variables

    def make_variable(self, name):
        out = self.graph.get_variable_name(name)
        self.output_variables.append(out)
        return out

    def make_cypher(self, ordering: list) -> Optional[str]:
        raise NotImplementedError

    def __repr__(self):
        r = self.make_cypher(list(self.graph.G.nodes))
        if r is None:
            return 'Nothing'
        return f'{r}'


class StartingMatch(Statement):
    ids = ['to_node_type', 'unwound']

    def __init__(self, to_node_type, unwound, graph):
        super(StartingMatch, self).__init__([], graph)
        self.to_node_type = to_node_type
        self.unwound = unwound
        self.to_node = self.make_variable(to_node_type)

    def make_cypher(self, ordering: list) -> Optional[str]:
        return f"MATCH ({self.to_node}:{self.to_node_type})"


class Traversal(Statement):
    ids = ['to_node_type', 'path', 'from_variable', 'unwound']

    def __init__(self, from_variable, to_node_type, path, unwound, graph):
        super().__init__([from_variable], graph)
        self.from_variable = from_variable
        self.to_node_type = to_node_type
        self.path = path
        self.to_node = self.make_variable(to_node_type)
        self.using_edge = self.make_variable('edge')
        self.unwound = unwound

    def make_cypher(self, ordering: list) -> str:
        path = self.path.format(name=self.using_edge)
        return f'OPTIONAL MATCH ({self.from_variable}){path}({self.to_node}:{self.to_node_type})'


class UnionTraversal(Statement):
    ids = ['to_node_type', 'path_names', 'path_values', 'from_variable', 'unwound']

    def __init__(self, from_variable, paths, to_node_type, unwound, graph):
        super().__init__([from_variable], graph)
        self.from_variable = from_variable
        self.to_node_type = to_node_type
        self.paths = paths
        self.path_names = list(paths.keys())
        self.path_values = list(paths.values())
        self.to_node = self.make_variable('node')
        self.using_edge = self.make_variable('edge')
        self.unwound = unwound

    def make_cypher(self, ordering: list) -> str:
        paths = [(n, path.format(name=self.using_edge)) for n, path in self.paths.items()]
        matches = 'UNION\n'.join([f'OPTIONAL MATCH ({self.from_variable}){path}({self.to_node}:{n})' for n, path in paths])
        return f"CALL {{WITH {self.from_variable}\n{matches}\nRETURN {self.to_node}\n}}"


class NullStatement(Statement):
    def __init__(self, input_variables, graph: 'QueryGraph'):
        super().__init__(input_variables, graph)
        self.output_variables = input_variables

    def make_cypher(self, ordering: list):
        return


class Operation(Statement):
    ids = ['op_string', 'op_name']

    def __init__(self, input_variable, dependency_variables, op_string, op_name, graph: 'QueryGraph'):
        super().__init__([input_variable]+dependency_variables, graph)
        self.op_string = op_string
        self.op_name = op_name
        self.op = f'({self.op_string.format(*self.inputs)})'
        self.output_variables.append(self.op)

    def make_cypher(self, ordering: list):
        return


class GetItem(Operation):
    ids = ['name']

    def __init__(self, input_variable, name, graph: 'QueryGraph'):
        super().__init__(input_variable, [], f'{{}}.`{name}`', f'.`{name}`', graph)
        self.name = name


class GetProduct(Operation):
    """
    Products are binary data that are not stored in the database.
    They are represented as a a relation between the parent node and an HDU of a fits file
    The relationship in neo4j will have the following properties: (product_name, column_name, index)
    Therefore, we return those properties after matching (node)<-[:PRODUCT {product_name:product_name}]-(hdu)
    """
    def __init__(self, input_variable, name, graph: 'QueryGraph'):
        super().__init__(input_variable, [], self.make_op_string(name), f'.{name}', graph)
        self.name = name

    def make_op_string(self, name):
        rel = f"({{}})<-[rel:product {{{{name: '{name}'}}}}]-(hdu: HDU)<--(file: File)"
        found = f"[{rel} | [file.path, hdu.extn, rel.index, rel.column_name, False]][0]"
        return found


class AssignToVariable(Statement):
    def __init__(self, input_variable, graph: 'QueryGraph'):
        super().__init__([input_variable], graph)
        self.input = input_variable
        self.output = self.make_variable('variable')

    def make_cypher(self, ordering: list) -> Optional[str]:
        return f"WITH *, {self.input} as {self.output}"


class Filter(Statement):
    def __init__(self, to_filter_variable, predicate_variable, graph: 'QueryGraph'):
        super().__init__([to_filter_variable, predicate_variable], graph)
        self.to_filter_variable = to_filter_variable
        self.predicate_variable = predicate_variable


class DirectFilter(Filter):
    def __init__(self, to_filter_variable, predicate_variable, graph: 'QueryGraph'):
        super().__init__(to_filter_variable, predicate_variable, graph)
        self.output = to_filter_variable
        self.output_variables = [to_filter_variable]

    def make_cypher(self, ordering: list) -> str:
        return f"WHERE {self.predicate_variable}"


class CopyAndFilter(Filter):
    def __init__(self, to_filter_variable, predicate_variable, graph: 'QueryGraph'):
        super().__init__(to_filter_variable, predicate_variable, graph)
        self.output = self.make_variable(to_filter_variable)

    def make_cypher(self, ordering: list) -> str:
        return f"WITH *, CASE WHEN {self.predicate_variable} THEN {self.to_filter_variable} ELSE null END as {self.output}"


class Slice(Statement):
    ids = ['slc']

    def __init__(self, input_variable, slc, graph: 'QueryGraph'):
        super().__init__([input_variable], graph)
        self.slc = slc

    def make_cypher(self, ordering: list) -> str:
        raise NotImplementedError


class Aggregate(Statement):
    ids = ['agg_func', 'name']

    def __init__(self, input, wrt_node, agg_func: str, name, graph: 'QueryGraph'):
        super().__init__([input, wrt_node], graph)
        self.agg_func = agg_func
        self.input = input
        self.wrt_node = wrt_node
        self.name = name
        self.output = self.make_variable(name)

    @property
    def conserve(self):
        above = self.graph.above_state(self.wrt_node)
        to_conserve = []
        for c in above:
            if not self.graph.node_holds_type(c, 'operation'):
                if self.graph.node_is_null_statement(c):
                    # this bit excludes fake aggregations where we have folded back along a single path (for consistency)
                    continue
                to_conserve.append(c)
        return to_conserve

    def make_cypher(self, ordering) -> str:
        conserve = {i for i in self.conserve if i in ordering}
        conserve = {self.graph.G.nodes[c]['variables'][0] for c in conserve if self.graph.G.nodes[c]['variables']}
        variables = ', '.join(conserve) + ', ' if conserve else ''
        agg_string = self.agg_func.format(self.input)
        return f"WITH {variables}{agg_string} as {self.output}"


class Return(Statement):
    ids = ['index_variable', 'dropna']

    def __init__(self, column_variables, index_variable, dropna, graph: 'QueryGraph'):
        super().__init__(column_variables, graph)
        if index_variable is not None:
            self.inputs.append(index_variable)
        self.index_variable = index_variable
        self.column_variables = column_variables
        self.dropna = dropna

    def make_cypher(self, ordering: list) -> Optional[str]:
        cols = self.column_variables if self.index_variable is None else self.column_variables[:-1]
        cols = ', '.join(cols)
        if self.dropna is not None:
            return f"WITH * WHERE {self.dropna} is not null RETURN {cols}"
        return f"RETURN {cols}"


class Unwind(Statement):
    ids = ['parameter']

    def __init__(self, wrt, parameter, name, graph: 'QueryGraph'):
        super().__init__([wrt], graph)
        self.parameter = parameter
        self.output = self.make_variable(name)

    def make_cypher(self, ordering: list) -> Optional[str]:
        return f"UNWIND {self.parameter} as {self.output}"