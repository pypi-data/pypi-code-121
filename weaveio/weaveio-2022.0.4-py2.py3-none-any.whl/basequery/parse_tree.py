from collections import defaultdict
from functools import reduce
from operator import and_
from typing import List

import networkx as nx

from weaveio.basequery.tree import Branch
from weaveio.basequery.actions import DataReference, Alignment
from weaveio.writequery import CypherQuery
from weaveio.writequery.base import Statement, CypherData


def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def print_nested_list(nested, tab=0):
    for entry in nested:
        if isinstance(entry, list):
            print_nested_list(['--'] + entry, tab+1)
        else:
            print('    '*tab, entry)


def shared_hierarchy_branch(graph, branch: Branch):
    branches = reduce(and_, [set(p.find_hierarchy_branches()) for p in branch.parents])
    distances = [(b, nx.shortest_path_length(graph, b, branch)) for b in branches]
    try:
        return max(distances, key=lambda x: x[1])[0]
    except ValueError:
        return branch.handler.entry  # no shared parents means going back to the beginning


def parse(graph) -> List:
    aligns = [i for i in graph.nodes if isinstance(i.action, Alignment)][::-1]
    shared_aligns = defaultdict(list)
    for align in aligns:
        shared_aligns[shared_hierarchy_branch(graph, align)].append(align)
    query = []
    todo = list(nx.algorithms.topological_sort(graph))
    while todo:
        node = todo.pop(0)
        if node in shared_aligns:
            align_list = shared_aligns[node][:1]
            query.append(node)
            for align in align_list:
                inputs = align.action.branches
                inputs += (align.action.reference, )
                subqueries = []
                for input_node in inputs:
                    before = list(nx.descendants(graph, node)) + [node]
                    after = list(nx.ancestors(graph, input_node)) + [input_node]
                    newgraph = nx.subgraph_view(graph, lambda n: n in before and n in after)
                    subquery = parse(newgraph)[1:]
                    subqueries.append(subquery)
                done = list(set(flatten(subqueries)))
                for d in done:
                    if d in todo:
                        del todo[todo.index(d)]
                # if align.action.continues_on:
                #     reference_subquery = subqueries.pop(-1)
                query += subqueries
                # if align.action.continues_on:
                #     query += reference_subquery
        else:
            query.append(node)
    return query

class OpenSubquery(Statement):
    def __init__(self, input_variables, output_variables, hidden_variables=None):
        super().__init__(input_variables, output_variables, hidden_variables)

    def to_cypher(self):
        inputs = ', '.join(map(str, ['time0'] + self.input_variables))
        return f"CALL {{with {inputs}"


class CloseSubquery(Statement):
    def __init__(self, input_variables, output_variables, hidden_variables=None):
        super().__init__(input_variables, output_variables, hidden_variables)

    def to_cypher(self):
        inputs = ', '.join(map(str, self.output_variables))
        return f"RETURN {inputs}\n}}"


def write_tree(parsed_tree):
    query = CypherQuery.get_context()  # type: CypherQuery
    if isinstance(parsed_tree, list):
        if len(parsed_tree) == 0:
            return
        inputs = [i for n in flatten(parsed_tree) for i in n.action.input_variables]
        outputs = [i for n in flatten(parsed_tree) for i in n.action.output_variables]
        subquery_inputs = list({i for i in inputs if getattr(i, 'parent', i) not in outputs and not isinstance(i, CypherData)})

        open = OpenSubquery(subquery_inputs, [])
        query.add_statement(open, safe=False)
        for node in parsed_tree:
            subquery_output = write_tree(node)
        subquery_output = list({v for v in subquery_output if v not in subquery_inputs})
        close = CloseSubquery(subquery_output, subquery_output)
        query.add_statement(close)
        return subquery_output
    else:
        query.add_statement(parsed_tree.action, safe=False)
        return parsed_tree.find_variables()

def branch2query(branch) -> CypherQuery:
    graph = branch.relevant_graph
    subqueries = parse(graph)
    with CypherQuery() as query:
        for node in graph.nodes:
            if isinstance(node.action, DataReference):
                query.data += node.action.input_variables
        for s in subqueries:
            write_tree(s)
    return query