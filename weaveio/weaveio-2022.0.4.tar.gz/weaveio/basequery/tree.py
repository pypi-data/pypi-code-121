from collections import defaultdict
from functools import reduce
from operator import xor
from typing import List, Dict, Optional

import networkx as nx
from networkx import OrderedDiGraph

from weaveio.basequery.actions import Action, EntryPoint, StartingPoint, DataReference, Traversal, Collection, Aggregation, Operation, Filter, shared_branch_without_filters, Results, TraversalPath, ScalarAlignment, DifferentLevelAlignment
from weaveio.writequery.base import CypherVariable, CypherData


class BranchHandler:
    def __init__(self):
        self.graph = OrderedDiGraph()
        self.class_counter = defaultdict(int)
        self.entry = self.new(EntryPoint(), [], [], None, [], [], [])
        self.data_objects = {}

    def new(self, action: Action, accessible_parents: List['Branch'], inaccessible_parents: List['Branch'],
            current_hierarchy: Optional[CypherVariable], current_variables: List[CypherVariable],
            variables: List[CypherVariable], hierarchies: List[CypherVariable], name: str = None):
        parents = accessible_parents + inaccessible_parents
        parent_set = set(parents)
        successors = {s for p in parents for s in self.graph.successors(p) if set(self.graph.predecessors(s)) == parent_set}
        candidates = {s for s in successors if s.action == action}
        assert len(candidates) <= 1
        if candidates:
            return successors.pop()
        if name is None:
            self.class_counter[action.__class__] += 1
            name = action.__class__.__name__ + str(self.class_counter[action.__class__])
        instance = Branch(self, action, accessible_parents, inaccessible_parents, current_hierarchy, current_variables,
                          variables=variables, hierarchies=hierarchies, name=name)
        attrs = {}
        if action.shape is not None:
            attrs['shape'] = action.shape
        self.graph.add_node(instance, action=action, name=name, **attrs)
        for parent in parents:
            self.graph.add_edge(parent, instance, accessible=parent in accessible_parents)
        self.current_hierarchy = current_hierarchy
        return instance

    def begin(self, *labels):
        action = StartingPoint(*labels)
        return self.new(action, [self.entry], [], action.hierarchy, [action.hierarchy], [], [action.hierarchy])

    def relevant_graph(self, branch):
        return nx.subgraph_view(self.graph, lambda n: nx.has_path(self.graph, n, branch) or n is branch)

    def deepest_common_ancestor(self, *branches: 'Branch'):
        common = set()
        for i, branch in enumerate(branches):
            ancestors = set(nx.algorithms.dag.ancestors(self.graph, branch))
            if i == 0:
                common = ancestors
            else:
                common &= ancestors
        if not len(common):
            return None
        distances = [(sum(nx.shortest_path_length(self.graph, ancestor, b) for b in branches), ancestor) for ancestor in common]
        return distances[distances.index(min(distances, key=lambda x: x[0]))][1]

    def _align_scalar(self, shared: 'Branch', vector: 'Branch', scalar: 'Branch'):
        scalar_collected = shared.collect([scalar], [])
        action = ScalarAlignment(vector, [scalar_collected])
        action.transformed_variables = scalar_collected.action.transformed_variables
        return self.new(action, [vector], [scalar_collected], None, action.outs, [], [])

    def _align_different_level(self, shared: 'Branch', branch1: 'Branch', branch2: 'Branch'):
        """
        1. collect the vector back to the shared level
        2. coalesce the scalar back to the shared level
        3. unwind the vector
        """
        collected1 = shared.collect([], [branch1])
        collected2 = shared.collect([], [branch2])
        action = DifferentLevelAlignment(shared, [collected1, collected2])
        transformed_variables = {}
        shared_variables = {v: v for v in shared.find_variables()}
        for v in branch1.find_variables():
            if v not in shared_variables and not isinstance(v, CypherData):
                transformed_variables[v] = action.transformed_variables[collected1.action.transformed_variables[v]]
        for v in branch2.find_variables():
            if v not in shared_variables and not isinstance(v, CypherData):
                try:
                    transformed_variables[v] = action.transformed_variables[collected2.action.transformed_variables[v]]
                except KeyError:
                    pass
        transformed_variables.update(shared_variables)
        action.transformed_variables = transformed_variables
        return self.new(action, [shared], [collected1, collected2], None, action.outs, [], [])



def plot(graph, fname):
    from networkx.drawing.nx_agraph import to_agraph
    A = to_agraph(graph)
    A.layout('dot')
    A.draw(fname)


class Branch:
    def __init__(self, handler: BranchHandler, action: Action,
                 accessible_parents: List['Branch'], inaccessible_parents: List['Branch'],
                 current_hierarchy: Optional[CypherVariable], current_variables: List[CypherVariable],
                 hierarchies: List[CypherVariable],
                 variables: List[CypherVariable], name: str = None):
        """
        A branch is an object that represents all the Actions (query statements) in a query.
        It contains both a node (Action) and references to all actions (other Branches) preceeding it (parents).
        If a branch is created in the same way more than once, only one object is actually instantiated, this is to optimize performance
        when writing to cypher query language. The user shouldn't care about this quirk.
        :param handler: The handler object which oversees query uniqueness for a particular dataset.
        :param action: The action that this branch will execute at the end. These are generally (but not always) Cypher statements.
        :param parents: The branches that must be executed before this one (i.e. the dependencies of this branch)
        """
        self.handler = handler
        self.action = action
        self.parents = accessible_parents + inaccessible_parents
        self.accessible_parents = accessible_parents
        self.inaccessible_parents = inaccessible_parents
        self.current_hierarchy = current_hierarchy
        self.current_variables = current_variables
        self.name = name
        self.hierarchies = hierarchies
        self.variables = variables
        self._relevant_graph = None
        self._accessible_graph = None
        self._hash = None

    def __hash__(self):
        if self._hash is None:
            self._hash = reduce(xor, map(hash, self.parents + [self.current_hierarchy, tuple(self.current_variables), self.action, self.handler]))
        return self._hash

    def __eq__(self, other):
        if self.__class__ is not other.__class__:
            return False
        return self.handler == other.handler and self.action == other.action and set(self.parents) == set(other.parents) \
               and self.current_hierarchy == other.current_hierarchy and set(self.current_variables) == set(other.current_variables)

    def __repr__(self):
        return f'<Branch {self.name}: {str(self.action)}>'

    @property
    def relevant_graph(self):
        if self._relevant_graph is None:
            self._relevant_graph = self.handler.relevant_graph(self)
        return self._relevant_graph

    @property
    def accessible_graph(self):
        if self._accessible_graph is None:
            g = nx.subgraph_view(self.relevant_graph, filter_edge=lambda a, b: self.relevant_graph.edges[(a, b)]['accessible'])
            self._accessible_graph = nx.subgraph_view(g, filter_node=lambda x: nx.has_path(g, x, self))
        return self._accessible_graph

    def iterdown(self, graph=None, start=None):
        if graph is None:
            graph = self.relevant_graph
        if start is None:
            start = self.handler.entry
        return nx.algorithms.traversal.dfs_tree(graph, start)

    def find_hierarchies(self):
        hierarchies = []
        for branch in self.iterdown(self.accessible_graph):
            if branch.current_hierarchy is not None:
                hierarchies.append(branch.current_hierarchy)
        return hierarchies

    def find_variables(self):
        variables = []
        for branch in self.iterdown(self.accessible_graph):
            variables += branch.current_variables
        return variables

    def find_hierarchy_branches(self, entry=False):
        branches = []
        for branch in self.iterdown(self.accessible_graph):
            if branch.current_hierarchy is not None or (branch is self.handler.entry and entry):
                branches.append(branch)
        return branches

    def get_variables(self, variables: List[CypherVariable]):
        squeeze = False
        if not isinstance(variables, (list, tuple)):
            variables = [variables]
            squeeze = True
        accessible_variables = self.find_variables()
        for branch in self.iterdown(self.relevant_graph):
            for i, variable in enumerate(variables):
                if variable in accessible_variables:
                    pass
                if variable in branch.current_variables:
                    pass
                else:
                    try:
                        variables[i] = branch.action.transformed_variables[variable]
                    except (AttributeError, KeyError):
                        pass
        if squeeze and len(variables) == 1:
            return variables[0]
        return variables


    def add_data(self, *data) -> 'Branch':
        action = DataReference(*data)
        return self.handler.new(action, [self], [], current_hierarchy=None, current_variables=action.input_variables,
                         variables=self.variables + action.input_variables, hierarchies=self.hierarchies)

    def traverse(self, *paths: TraversalPath) -> 'Branch':
        """
        Extend the branch from the most recent hierarchy to a new hierarchy(s) by walking along the paths
        If more than one path is given then we take the union of all the resultant nodes.
        """
        action = Traversal(self.find_hierarchies()[-1], *paths)
        return self.handler.new(action, [self], [], current_hierarchy=action.out, current_variables=[action.out],
                                variables=self.variables, hierarchies=self.hierarchies+[action.out])

    # def align(self, branch: 'Branch') -> 'Branch':
    #     """
    #     Join branches into one, keeping the highest cardinality.
    #     This is used to to directly compare arrays:
    #         * ob1.runs == ob2.runs  (unequal sizes are zipped up together)
    #         * ob1.runs == run1  (array to single comparisons are left as is)
    #         * run1 == run2  (single to single comparisons are left as is)
    #     zip ups and unwinds take place relative to the branch's shared ancestor
    #     """
    #     shared = join_branches(self, branch)
    #     a = shared.collect([self], [])
    #     b = shared.collect([branch], [])
    #     action = Alignment(a, b)
    #     return self.handler.new(action, [a], [b], None, current_variables=action.outs,
    #                             variables=a.variables, hierarchies=a.hierarchies)

    def align(self, branch: 'Branch') -> 'Branch':
        """
        Aligning a scalar (1 of them is at the level of the shared hierarchy):
        =======================================================================================
            To align things like: data.obs.targets.ra == max(data.obs.runids, wrt=data.obs),
            we find the shared parent (data.obs)
            for each:
                if hierarchy level is above the shared parent, collect the results
                if hierarchy level is at the shared parent, do nothing
                if hierarchy level is below the shared parent, raise error
            we are now at the level of the shared parent
            zip up and unwind the variables together so they are aligned (using the length of variable which was collected)

        Aligning two different branches (neither of them are at the level of shared hierarchy):
        =======================================================================================
            To align things like data.obs[all(data.obs.targets[x].runs == data.obs.targets[y].runs)]
                i.e. this thing:  data.obs.targets[x].runs == data.obs.targets[y].runs
            we find the shared parent (data.obs)
            for each:
                collect the results
            we are now at the level of the shared parent
            zip up and unwind the variables together so they are aligned (using the length of variable which was collected)

        Aligning on the same branch:
        =======================================================================================
            To align things like:
                1) data.obs.runs == data.obs.runs
                    they share the exact same tree, so `.align` does nothing
                2) data.obs.runs == max(data.obs.runs.target.ra, wrt=data.obs.runs)
                    the share the same tree but since the right-hand-side splits off and aggregates back,
                    we do nothing but return the split off branch
        """
        shared = shared_branch_without_filters(self, branch)
        branch_is_scalar = branch.find_hierarchy_branches(True)[-1] is shared
        self_is_scalar = self.find_hierarchy_branches(True)[-1] is shared
        if branch_is_scalar and self_is_scalar:
            return self.handler._align_different_level(shared, self, branch)
        if branch_is_scalar:
            return self.handler._align_scalar(shared, self, branch)
        elif self_is_scalar:
            return self.handler._align_scalar(shared, branch, self)
        else:
            return self.handler._align_different_level(shared, self, branch)



    def collect(self, singular: List['Branch'], multiple: List['Branch']) -> 'Branch':
        """
        Join branches into one, reducing the cardinality to this branch.
        `singular` contains branches that will be coalesced (i.e. only the first result is taken)
        `multiple` contains branches that will be collected (i.e. all results are presented in a list)
        This is used in predicate filters:
            ob1.runs[any(ob1.runs.l1singlespectra.snr > 10)]
            0. branch `ob1.runs` is created
            1. branch `ob1.runs.l1singlespectra.snr > 10` is created
            2. branch `ob1.runs.l1singlespectra.snr > 10` is collected with respect to `ob1.runs`
            3. A filter is applied on the collection at the `ob1.runs` level
        After a collection, only
        """
        action = Collection(self, singular, multiple)
        variables = action.outsingle_variables + action.outmultiple_variables
        hierarchies = action.outsingle_hierarchies + action.outmultiple_hierarchies
        return self.handler.new(action, [self], singular + multiple, None, variables + hierarchies,
                                variables=self.variables + variables, hierarchies=self.hierarchies + hierarchies)

    def aggregate(self, string_function: str, variable: CypherVariable, branch: 'Branch', namehint: str) -> 'Branch':
        action = Aggregation(string_function, variable, branch, self, namehint)
        return self.handler.new(action, [self], [branch], None, [action.target], [action.target], [])

    def operate(self, *string_functions, namehint=None, **inputs: CypherVariable) -> 'Branch':
        """
        Adds a new variable to the namespace
        e.g. y = x*2 uses extant variable x to define a new variable y which is then subsequently accessible
        """
        # missing = [k for k, v in inputs.items() if getattr(v, 'parent', v) not in self.variables + self.hierarchies]
        # if missing:
        #     raise ValueError(f"inputs {missing} are not in scope for {self}")
        op = Operation(*string_functions, namehint=namehint, **inputs)
        return self.handler.new(op, [self], [], None, op.output_variables,
                                variables=self.variables + op.output_variables, hierarchies=self.hierarchies)

    def filter(self, logical_string, **boolean_variables: CypherVariable) -> 'Branch':
        """
        Reduces the cardinality of the branch by using a WHERE clause.
        .filter can only use available variables
        """
        # missing = [k for k, v in boolean_variables.items() if getattr(v, 'parent', v) not in self.variables + self.hierarchies]
        # if missing:
        #     raise ValueError(f"inputs {missing} are not in scope for {self}")
        action = Filter(logical_string, **boolean_variables)
        return self.handler.new(action, [self], [], None, [],
                                variables=self.variables, hierarchies=self.hierarchies)

    def results(self, branch_attributes: Dict['Branch', List[CypherVariable]]):
        """
        Returns the rows of results.
        All other branches which are not this branch will have their results collected
        """
        branch_attributes = {k: v if isinstance(v, (list, tuple)) else [v] for k, v in branch_attributes.items()}
        action = Results(branch_attributes)
        return self.handler.new(action, [self], [], None, [], self.variables, self.hierarchies)
