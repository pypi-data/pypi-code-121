import json
from collections import defaultdict


def iterate(obj):
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            yield i, v
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v


def get_referenced_nodes(arguments):
    from_nodes = set()
    for k, v in iterate(arguments):
        if isinstance(v, dict) and len(v) == 1 and "process_graph" in v:
            continue
        elif isinstance(v, dict) and len(v) == 1 and "from_node" in v:
            from_nodes.add(v["from_node"])
        elif isinstance(v, dict) or isinstance(v, list):
            from_nodes.update(get_referenced_nodes(v))

    return from_nodes


def get_dependencies(process_graph):
    dependency_graph = defaultdict(set)
    for node_id, node in process_graph.items():
        node_references = get_referenced_nodes(node["arguments"])
        dependency_graph[node_id].update(node_references)
    return dependency_graph


def get_entry_points(dependencies):
    entry_points = []
    for node, node_dependencies in dependencies.items():
        if len(node_dependencies) == 0:
            entry_points.append(node)
    return entry_points


def get_exit_points(all_nodes, dependents):
    exit_points = []
    for node in all_nodes:
        if len(dependents[node]) == 0:
            exit_points.append(node)
    return exit_points


def get_dependents(dependencies):
    dependents = defaultdict(set)
    for node, node_dependencies in dependencies.items():
        for node_dependency in node_dependencies:
            dependents[node_dependency].add(node)
    return dependents


def get_execution_order(dependencies, dependents):
    entry_points = get_entry_points(dependencies)
    execution_order = [entry_point for entry_point in entry_points]
    remaining_nodes = set(dependencies.keys()).difference(execution_order)

    i = 0

    while len(remaining_nodes) > 0:
        if i > 20:
            break
        i += 1
        for node in execution_order:
            for node_dependency in dependents[node]:
                if node_dependency in execution_order:
                    continue
                can_be_executed = all([n in execution_order for n in dependencies[node_dependency]])

                if can_be_executed:
                    execution_order.append(node_dependency)
                    remaining_nodes.remove(node_dependency)

                else:
                    break
    return execution_order


def copy_dictionary(d):
    return json.loads(json.dumps(d))


def find_all_relatives(node_id, relatives):
    all_relatives = set()
    for relative in relatives[node_id]:
        all_relatives.add(relative)
        all_relatives.update(find_all_relatives(relative, relatives))
    return all_relatives


def find_all_descendants(node_id, dependents):
    return find_all_relatives(node_id, dependents)


def find_all_ancestors(node_id, dependencies):
    return find_all_relatives(node_id, dependencies)


def generate_subgraph(node_id, dependency_graph, process_graph):
    subgraph = {}

    all_ancestors = find_all_ancestors(node_id, dependency_graph)

    for ancestor in all_ancestors:
        subgraph[ancestor] = process_graph[ancestor]

    return subgraph
