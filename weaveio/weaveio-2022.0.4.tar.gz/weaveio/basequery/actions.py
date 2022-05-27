from functools import reduce, wraps
from operator import xor, and_
from typing import List, Dict, Union

import networkx as nx

from weaveio.writequery import CypherVariable, CypherData
from weaveio.writequery.base import BaseStatement, CypherVariableItem

def typeerror_is_false(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            return False
    return inner


def sort_rooted_dag(graph):
    for n, d in graph.in_degree():
        if d == 0:
            break
    return nx.algorithms.traversal.dfs_tree(graph, n)


class Step:
    def __init__(self, direction: str, label: str = 'is_required_by', properties: Dict = None):
        if isinstance(direction, Step):
            self.direction = direction.direction
            self.label = direction.label
            self.properties = direction.properties
        elif direction in ['->', '<-']:
            self.direction = direction
            self.label = label
            self.properties = properties
        else:
            raise ValueError(f"Direction {direction} is not supported")

    @typeerror_is_false
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.direction == other.direction and self.properties == other.properties and self.label == other.label

    def __str__(self):
        if self.properties is None:
            mid = f'-[:{self.label}]-'
        else:
            mid = f'-[:{self.label} {self.properties}]-'
        if self.direction == '->':
            return f"{mid}>"
        elif self.direction == '<-':
            return f"<{mid}"
        else:
            return mid


class TraversalPath:
    def __init__(self, *path: Union[Step, str]):
        self._path = path
        self.nodes = []
        self.steps = []
        self.path = []
        self.end = CypherVariable(str(path[-1])) if len(path) > 1 else None
        self.repr_path = ''.join(path)
        for i, entry in enumerate(path[:-1]):
            if not i % 2:  # even number
                step = Step(entry)
                self.steps.append(step)
                self.path.append(step)
            else:
                self.nodes.append(str(entry))
                self.path.append(f'(:{entry})')

    def __len__(self):
        return len(self.nodes) + 1

    def __str__(self):
        if self.end is None:
            return ''
        end = f'({self.end}:{self.end.namehint})'
        return ''.join(map(str, self.path)) + end

    def __repr__(self):
        return f'<TraversalPath({str(self.repr_path)})>'

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self._path == other._path

    def __hash__(self):
        return hash(self._path)


class Action(BaseStatement):
    compare = None
    shape = None
    is_filter = False

    def to_cypher(self):
        raise NotImplementedError

    def __getitem__(self, item: CypherVariable):
        if isinstance(item, CypherVariableItem):
            return self.transformed_variables[item.parent].get(item.args)
        return self.transformed_variables[item]

    def __init__(self, input_variables: List[CypherVariable], output_variables: List[CypherVariable],
                 hidden_variables: List[CypherVariable] = None, transformed_variables: Dict[CypherVariable, CypherVariable] = None, target: CypherVariable = None):
        super(Action, self).__init__(input_variables, output_variables, hidden_variables)
        self.transformed_variables = {} if transformed_variables is None else transformed_variables
        self.target = target

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        base = set(self.input_variables) == set(other.input_variables) and self.__class__ is other.__class__
        for c in self.compare:
            selfthing = getattr(self, c, None)
            otherthing = getattr(other, c, None)
            base &= selfthing == otherthing
        return base

    def __hash__(self):
        base = reduce(xor, map(hash, [tuple(self.input_variables), self.__class__.__name__]))
        for c in self.compare:
            base ^= hash(getattr(self, c))
        return base

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return f'<{str(self)}>'


class EntryPoint(Action):
    compare = []

    def __init__(self):
        super().__init__([], [])

    def to_cypher(self):
        return ''

    def __str__(self):
        return 'EntryPoint'


class StartingPoint(Action):
    compare = ['labels']

    def __init__(self, *labels):
        self.labels = labels
        self.hierarchy = CypherVariable(self.labels[-1])
        super().__init__([], [self.hierarchy], target=self.hierarchy)

    def to_cypher(self):
        s = f"OPTIONAL MATCH ({self.hierarchy}:{self.labels[0]})"
        if len(self.labels) == 1:
            return s
        condition = ' OR '.join([f'{self.hierarchy}:{l}' for l in self.labels[1:]])
        return s + f" WHERE {condition}"

    def __str__(self):
        return '|'.join(self.labels)


class DataReference(Action):
    compare = ['hashes']

    def __init__(self, *data):
        import numpy as np
        self.hashes = reduce(xor, [hash(np.array(a).tobytes()) for a in data])
        ins = [CypherData(datum, delay=True) for datum in data]
        super().__init__(ins, [])

    def to_cypher(self):
        return '// added data here'

    def __str__(self):
        return 'DataReference'


class Traversal(Action):
    """
    Traverse from one hierarchy level to another. This extends the branch and
    potentially increases the cardinality.
    Given a `source` branch and one or more `paths` of form (minnumber, maxnumber, direction),
     traverse to the nodes described by the `paths`.
    For example:
        >>> Traversal(branch, TraversalPath(['->', 'Exposure', '->', 'OB', '->', 'OBSpec']))
        results in `OPTIONAL MATCH (run)-[]->(:Exposure)-[]->(:OB)-[]->(obspec:OBSpec)`
    To traverse multiple paths at once, we use unions in a subquery
    """
    compare = ['paths', 'source']

    def __init__(self, source: CypherVariable, *paths: TraversalPath, name=None):
        if name is None:
            name = ''.join(getattr(p.end, 'namehint', source.namehint) for p in paths[:2])
        self.out = CypherVariable(name)
        # if there is an empty path, then we just refer to the source node
        self.ends = [p.end if p.end is not None else source for p in paths]
        super(Traversal, self).__init__([source], [self.out], [i for i in self.ends if i is not source], target=self.out)
        self.source = source
        self.paths = paths

    def to_cypher(self):
        if len(self.paths) > 1:
            lines = [f'OPTIONAL MATCH ({self.source}){p}' for p in self.paths]
            lines = '\n\nUNION\n\n'.join([f'\tWITH {self.source}\n\t{l}\n\tRETURN {end} as {self.out}' for l, end in zip(lines, self.ends)])
            return f"""CALL {{\n{lines}\n}}"""
        return f'OPTIONAL MATCH ({self.source}){self.paths[0]}\nWITH *, {self.ends[0]} as {self.out}'

    def __str__(self):
        return f'{self.source.namehint}->{self.out.namehint}'


class Return(Action):
    compare = ['branch', 'varnames']  # just compare input_variables

    def __init__(self, branch: 'Branch', *varnames):
        self.branch = branch
        self.varnames = varnames
        super(Return, self).__init__([branch.hierarchies[-1]], [])

    def to_cypher(self):
        proj = ', '.join([f'{self.branch.hierarchies[-1].get(v)}' for v in self.varnames])
        return f"RETURN {proj}"

    def __str__(self):
        return f'return {self.varnames}'


class Collection(Action):
    shape = 'rect'
    compare = ['_singles', '_multiples', '_reference']

    def __init__(self, reference: 'Branch', singles: List['Branch'], multiples: List['Branch']):
        self._singles = tuple(singles)
        self._multiples = tuple(multiples)
        self._reference = reference

        self.references = reference.find_hierarchies()
        self.references += [v for v in reference.find_variables() if v not in self.references and not isinstance(v, CypherData)]
        self.insingle_hierarchies = [h for x in singles for h in x.find_hierarchies() if h not in self.references and not isinstance(h, CypherData)]
        self.insingle_variables = [v for x in singles for v in x.find_variables() if v not in self.insingle_hierarchies
                                   and v not in self.references and not isinstance(v, CypherData)]
        self.inmultiple_hierarchies = [h for x in multiples  for h in x.find_hierarchies() if h not in self.references and not isinstance(h, CypherData)]
        self.inmultiple_variables = [v for x in multiples for v in x.variables if v not in self.insingle_hierarchies
                                     and v not in self.references and not isinstance(v, CypherData)]

        self.outsingle_hierarchies = [CypherVariable(s.namehint) for s in self.insingle_hierarchies]
        self.outsingle_variables = [CypherVariable(s.namehint) for s in self.insingle_variables]
        self.outmultiple_hierarchies = [CypherVariable(s.namehint+'_list') for s in self.inmultiple_hierarchies]
        self.outmultiple_variables = [CypherVariable(s.namehint+'_list') for s in self.inmultiple_variables]
        inputs = self.insingle_hierarchies + self.insingle_variables + self.inmultiple_variables + self.inmultiple_hierarchies
        outputs = self.outsingle_hierarchies + self.outsingle_variables + self.outmultiple_variables + self.outmultiple_hierarchies
        super().__init__(inputs + self.references, outputs, [], transformed_variables={i: o for i, o in zip(inputs, outputs)})

    def to_cypher(self):
        base = [f'{r}' for r in self.references + ['time0']]
        single_hierarchies = [f'{i} as {o}' for i, o in zip(self.insingle_hierarchies, self.outsingle_hierarchies)]
        multiple_hierarchies = [f'collect({i}) as {o}' for i, o in zip(self.inmultiple_hierarchies, self.outmultiple_hierarchies)]
        single_variables = [f'{i} as {o}' for i, o in zip(self.insingle_variables, self.outsingle_variables)]
        multiple_variables = [f'collect({i}) as {o}' for i, o in zip(self.inmultiple_variables, self.outmultiple_variables)]
        return 'WITH ' + ', '.join(base + single_hierarchies + single_variables + multiple_hierarchies + multiple_variables)

    def __str__(self):
        return f'collect'


class Aggregation(Action):
    shape = 'rect'
    compare = ['string_function', 'variable', 'branch', 'reference']

    def __init__(self, string_function: str, variable: CypherVariable, branch: 'Branch', reference: 'Branch', namehint: str):
        self.string_function = string_function
        self.variable = variable
        self.branch = branch
        self.reference = reference
        ins = self.reference.find_variables() + [self.variable]
        self.output = CypherVariable(f"{namehint}_{variable.namehint}")
        transformed_variables = {i: i for i in ins[:-1]}
        transformed_variables[self.variable] = self.output
        super().__init__(ins, [self.output], [], transformed_variables, self.output)

    def to_cypher(self):
        string_function = self.string_function.format(x=self.variable)
        statics = ", ".join(map(str, ['time0'] + self.input_variables[:-1]))
        return f'WITH {statics}, {string_function} as {self.output}'

    def __str__(self):
        return f"{self.string_function}"


class Operation(Action):
    compare = ['string_functions', 'hashable_inputs']

    def __init__(self, *string_functions: str, namehint=None, **inputs):
        self.string_functions = string_functions
        if not isinstance(namehint, (list, tuple)):
            namehint = [namehint] * len(string_functions)
        self.outputs = [CypherVariable(nh) for _, nh in zip(string_functions, namehint)]
        self.inputs = inputs
        self.hashable_inputs = tuple(self.inputs.items())
        super().__init__(list(inputs.values()), self.outputs, target=self.outputs[0])

    def to_cypher(self):
        assignments = [f"{func.format(**self.inputs)} as {out}" for func, out in zip(self.string_functions, self.outputs)]
        return f"WITH *, {', '.join(assignments)}"

    def __str__(self):
        return ', '.join(self.string_functions)


class Filter(Operation):
    shape = 'diamond'
    is_filter = True

    def __init__(self, string_function, **inputs):
        super().__init__(string_function, **inputs)
        self.string_function = string_function

    def to_cypher(self):
        return f"WHERE {self.string_function.format(**self.inputs)}"


def shared_branch(*branches: 'Branch'):
    """
    Find the ancestral branch of two or more branches
    """
    newbranches = reduce(and_, [set(p.find_hierarchy_branches()) for p in branches])
    distances = [(ancestor, sum(nx.shortest_path_length(branch.relevant_graph, ancestor, branch) for branch in branches)) for ancestor in newbranches]
    try:
        return max(distances, key=lambda x: x[1])[0]
    except ValueError:
        return branches[0].handler.entry  # no shared parents means going back to the beginning


def shared_branch_without_filters(a: 'Branch', b: 'Branch'):
    shared = shared_branch(a, b)
    if shared is a.handler.entry:
        return shared  # cant go back beyond the start
    afilters = any(i.action.is_filter for i in nx.shortest_path(a.accessible_graph, shared, a))
    bfilters = any(i.action.is_filter for i in nx.shortest_path(b.accessible_graph, shared, b))
    if afilters or bfilters:
        try:
            return shared.find_hierarchy_branches(True)[-2]
        except IndexError:
            return a.handler.entry
    return shared


# class Alignment(Action):
#     compare = ['reference', 'branches']
#
#     def __init__(self, reference: 'Branch', *branches):
#         assert isinstance(reference.action, Collection)
#         for branch in branches:
#             assert isinstance(branch.action, Collection)
#         self.reference = reference
#         self.branches = branches
#         self.ins = list(set(i for x in (reference, ) + branches for i in x.find_variables()))
#         self.outs = [CypherVariable(i.namehint) for i in self.ins]
#         self.indexer = CypherVariable('i')
#         transformed_variables = {i: o for i, o in zip(self.ins, self.outs)}
#         super(Alignment, self).__init__(self.ins, self.outs, [self.indexer], transformed_variables)
#
#     def to_cypher(self):
#         # unwind = f'UNWIND range(0, apoc.coll.max([x in {self.ins} | size(x)])-1) as {self.indexer}'
#         # get = [f'{i}[{self.indexer}] as {o}' for i, o in zip(self.ins, self.outs)]
#         # return f"{unwind}\nWITH *, {', '.join(get)}"
#         return ''
#
#     def __str__(self):
#         return 'align'

class Alignment(Action):
    compare = ['reference', 'branches']
    continues_on = False

    def __str__(self):
        return f'{self.__class__.__name__}'


class Slice(Action):
    compare = []
    is_filter = True

    def __init__(self, slc):
        self.slc = slc
        self.skip = slc.start
        self.limit = slc.stop - slc.start
        super().__init__([], [], [])

    def __str__(self):
        return f'{self.slc}'

    def to_cypher(self):
        return f'WITH * SKIP {self.skip} LIMIT {self.limit}'


class Results(Action):
    compare = ['branches']

    def __init__(self, branch_attributes):
        self.branch_attributes = branch_attributes
        self.branches = tuple(branch_attributes.keys())
        ins = [j for i in self.branch_attributes.values() for j in i]
        super(Results, self).__init__(ins, [], [], {}, None)

    def to_cypher(self):
        return 'RETURN {}'.format(', '.join(map(str, self.input_variables)))

    def __str__(self):
        names = [i.namehint for i in self.input_variables]
        return 'return {}'.format(', '.join(names))


class DifferentLevelAlignment(Alignment):
    compare = ['reference', 'branches']
    continues_on = False

    def __init__(self, reference, branches):
        self.reference = reference
        self.branches = tuple(branches)
        self.shared_variables = reference.find_variables()
        self.to_unwind = [v for branch in branches for v in branch.find_variables() if v not in self.shared_variables]
        ins = self.shared_variables + self.to_unwind
        self.outs = [CypherVariable(v.namehint) for v in self.to_unwind]
        self.indexer = CypherVariable('i')
        transformed = {v: o for v, o in zip(self.to_unwind, self.outs)}
        transformed.update({v: v for v in self.shared_variables})
        super().__init__(ins, self.outs, [self.indexer], transformed)

    def to_cypher(self):
        unwind = f'UNWIND range(0, size({self.to_unwind[0]})-1) as {self.indexer}'
        unzip = [f'{v}[{self.indexer}] as {o}' for v, o in zip(self.to_unwind, self.outs)]
        static = [f'{v}' for v in self.shared_variables]
        get = f'WITH {", ".join(["time0"] + static + unzip)}'
        return f'{unwind}\n{get}'


class ScalarAlignment(Alignment):
    continues_on = True

    def __init__(self, reference, branches):
        self.reference = reference
        self.branches = tuple(branches)
        self.outs = []
        super().__init__([], [])

    def to_cypher(self):
        return f""
