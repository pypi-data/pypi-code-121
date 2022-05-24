from pg_to_evalscript.evalscript import Evalscript
from pg_to_evalscript.process_graph_utils import (
    get_dependencies,
    get_dependents,
    get_execution_order,
    find_all_descendants,
    find_all_ancestors,
    generate_subgraph,
)

from pg_to_evalscript.node import Node, ProcessDefinitionMissing


def validate_nodes(
    execution_order,
    process_graph,
    dependency_graph,
    dependents,
    temporal_dimension_name,
    bands_dimension_name,
    user_defined_processes,
):
    valid_subgraphs = []
    all_nodes_valid = True
    for node_id in execution_order:
        process_id = process_graph[node_id]["process_id"]
        arguments = process_graph[node_id]["arguments"]

        valid = True

        if process_id == "reduce_dimension" and arguments["dimension"] not in [
            temporal_dimension_name,
            bands_dimension_name,
        ]:
            valid = False

        try:
            node = Node(
                node_id,
                process_id,
                arguments,
                [],
                dependency_graph[node_id],
                dependents[node_id],
                0,
                user_defined_processes=user_defined_processes,
            )
        except ProcessDefinitionMissing as e:
            valid = False

        if not valid:
            all_nodes_valid = False
            all_descendants = find_all_descendants(node_id, dependents)
            all_ancestors = find_all_ancestors(node_id, dependency_graph)
            subgraph = generate_subgraph(node_id, dependency_graph, process_graph)
            valid_subgraphs.append({"node": node_id, "graph": subgraph})

    return all_nodes_valid, valid_subgraphs


def check_validity_and_subgraphs(
    process_graph, temporal_dimension_name, bands_dimension_name, user_defined_processes={}
):
    dependency_graph = get_dependencies(process_graph)
    dependents = get_dependents(dependency_graph)
    execution_order = get_execution_order(dependency_graph, dependents)
    return validate_nodes(
        execution_order,
        process_graph,
        dependency_graph,
        dependents,
        temporal_dimension_name,
        bands_dimension_name,
        user_defined_processes,
    )


def convert_from_process_graph(
    process_graph,
    user_defined_processes={},
    n_output_bands=1,
    sample_type="FLOAT32",
    units=None,
    bands_dimension_name="bands",
    temporal_dimension_name="t",
    encode_result=True,
    bands_metadata=[],
):
    all_nodes_valid, subgraphs = check_validity_and_subgraphs(
        process_graph, temporal_dimension_name, bands_dimension_name, user_defined_processes=user_defined_processes
    )
    if all_nodes_valid:
        nodes, input_bands, initial_data_name = generate_nodes_from_process_graph(
            process_graph,
            bands_dimension_name,
            temporal_dimension_name,
            user_defined_processes=user_defined_processes,
            level=1,
        )
        evalscript = Evalscript(
            input_bands,
            nodes,
            initial_data_name,
            n_output_bands=n_output_bands,
            sample_type=sample_type,
            units=units,
            encode_result=encode_result,
            bands_metadata=bands_metadata,
        )
        output_dimensions = evalscript.determine_output_dimensions()
        evalscript.set_output_dimensions(output_dimensions)
        return [
            {
                "evalscript": evalscript,
                "invalid_node_id": None,
            }
        ]
    else:
        evalscripts = []
        for subgraph in subgraphs:
            nodes, input_bands, initial_data_name = generate_nodes_from_process_graph(
                subgraph["graph"],
                bands_dimension_name,
                temporal_dimension_name,
                user_defined_processes=user_defined_processes,
                level=1,
            )
            evalscript = Evalscript(
                input_bands,
                nodes,
                initial_data_name,
                n_output_bands=n_output_bands,
                sample_type=sample_type,
                units=units,
                encode_result=encode_result,
                bands_metadata=bands_metadata,
            )
            output_dimensions = evalscript.determine_output_dimensions()
            evalscript.set_output_dimensions(output_dimensions)
            evalscripts.append(
                {
                    "evalscript": evalscript,
                    "invalid_node_id": subgraph["node"],
                }
            )
        return evalscripts


def generate_nodes_from_process_graph(
    process_graph, bands_dimension_name, temporal_dimension_name, user_defined_processes={}, level=1
):
    dependency_graph = get_dependencies(process_graph)
    dependents = get_dependents(dependency_graph)
    execution_order = get_execution_order(dependency_graph, dependents)
    all_nodes_valid, subgraphs = validate_nodes(
        execution_order,
        process_graph,
        dependency_graph,
        dependents,
        temporal_dimension_name,
        bands_dimension_name,
        user_defined_processes,
    )

    nodes = []
    input_bands = None
    initial_data_name = None

    for node_id in execution_order:
        process_id = process_graph[node_id]["process_id"]
        arguments = process_graph[node_id]["arguments"]
        child_nodes = None

        if process_id == "load_collection":
            input_bands = arguments.get("bands")
            initial_data_name = "node_" + node_id
            continue
        elif process_id == "save_result":
            continue
        elif process_id == "reduce_dimension":
            child_nodes, _, _ = generate_nodes_from_process_graph(
                arguments["reducer"]["process_graph"],
                bands_dimension_name,
                temporal_dimension_name,
                user_defined_processes=user_defined_processes,
                level=level + 1,
            )
        elif process_id == "apply" or process_id == "apply_dimension":
            child_nodes, _, _ = generate_nodes_from_process_graph(
                arguments["process"]["process_graph"],
                bands_dimension_name,
                temporal_dimension_name,
                user_defined_processes=user_defined_processes,
                level=level + 1,
            )
        elif process_id == "count":
            if "condition" in arguments and arguments["condition"] is not None:
                child_nodes, _, _ = generate_nodes_from_process_graph(
                    arguments["condition"]["process_graph"],
                    bands_dimension_name,
                    temporal_dimension_name,
                    user_defined_processes=user_defined_processes,
                    level=level + 1,
                )
        elif process_id == "array_apply":
            child_nodes, _, _ = generate_nodes_from_process_graph(
                arguments["process"]["process_graph"],
                bands_dimension_name,
                temporal_dimension_name,
                user_defined_processes=user_defined_processes,
                level=level + 1,
            )
        elif process_id == "array_filter":
            child_nodes, _, _ = generate_nodes_from_process_graph(
                arguments["condition"]["process_graph"],
                bands_dimension_name,
                temporal_dimension_name,
                user_defined_processes=user_defined_processes,
                level=level + 1,
            )
        elif process_id == "aggregate_temporal_period":
            child_nodes, _, _ = generate_nodes_from_process_graph(
                arguments["reducer"]["process_graph"],
                bands_dimension_name,
                temporal_dimension_name,
                user_defined_processes=user_defined_processes,
                level=level + 1,
            )
        elif process_id == "aggregate_temporal":
            child_nodes, _, _ = generate_nodes_from_process_graph(
                arguments["reducer"]["process_graph"],
                bands_dimension_name,
                temporal_dimension_name,
                user_defined_processes=user_defined_processes,
                level=level + 1,
            )
        elif process_id in user_defined_processes:
            child_nodes, _, _ = generate_nodes_from_process_graph(
                user_defined_processes[process_id],
                bands_dimension_name,
                temporal_dimension_name,
                user_defined_processes=user_defined_processes,
                level=level + 1,
            )
        node = Node(
            node_id,
            process_id,
            arguments,
            child_nodes,
            dependency_graph[node_id],
            dependents[node_id],
            level,
            user_defined_processes=user_defined_processes,
        )
        nodes.append(node)
    return nodes, input_bands, initial_data_name
