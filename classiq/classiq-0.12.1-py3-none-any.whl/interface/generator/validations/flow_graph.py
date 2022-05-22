from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import chain
from typing import Dict, List, Optional

import networkx as nx

from classiq.interface.generator.function_call import FunctionCall
from classiq.interface.helpers.custom_pydantic_types import pydanticNonEmptyString

IO_MULTI_USE_ERROR_MSG = "Input and output names can only be used once"
UNCONNECTED_WIRES_ERROR_MSG = "Wires connected only on one end"
UNCONNECTED_FLOW_IO_ERROR_MSG = (
    "Composite function inputs/outputs not connected to inner calls"
)
CYCLE_ERROR_MSG = "Inputs and outputs cannot form a cycle"
UNKNOWN_ERROR_MSG = "Unknown error in the flow graph"
RECURRING_NAMES_ERROR_MSG = "Recurring wire names"


@dataclass
class Wire:
    start: Optional[pydanticNonEmptyString] = None
    end: Optional[pydanticNonEmptyString] = None


def _parse_call_inputs(
    function_call: FunctionCall, wires: Dict[str, Wire], flow_input_names: List[str]
) -> None:
    if not function_call.non_zero_input_wires:
        return

    for wire_name in function_call.non_zero_input_wires:
        if wire_name in flow_input_names:
            continue

        wire = wires[wire_name]

        if wire.end:
            raise ValueError(
                IO_MULTI_USE_ERROR_MSG
                + f". The name {wire_name} is used multiple times."
            )
        wire.end = function_call.name


def _parse_call_outputs(
    function_call: FunctionCall, wires: Dict[str, Wire], flow_output_names: List[str]
) -> None:
    if not function_call.non_zero_output_wires:
        return

    for wire_name in function_call.non_zero_output_wires:
        if wire_name in flow_output_names:
            continue

        wire = wires[wire_name]

        if wire.start:
            raise ValueError(
                IO_MULTI_USE_ERROR_MSG
                + f". The name {wire_name} is used multiple times."
            )
        wire.start = function_call.name


def _create_flow_graph(
    logic_flow: List[FunctionCall],
    flow_input_names: List[str],
    flow_output_names: List[str],
    allow_one_ended_wires: bool = False,
) -> nx.DiGraph:
    wires: Dict[str, Wire] = defaultdict(Wire)
    for function_call in logic_flow:
        _parse_call_inputs(
            function_call=function_call, wires=wires, flow_input_names=flow_input_names
        )
        _parse_call_outputs(
            function_call=function_call,
            wires=wires,
            flow_output_names=flow_output_names,
        )

    edges = [(wire.start, wire.end) for wire in wires.values()]
    if allow_one_ended_wires:
        edges = list(
            filter(lambda edge: edge[0] is not None and edge[1] is not None, edges)
        )

    graph = nx.DiGraph()

    graph.add_nodes_from(
        [
            (function_call.name, {"function_call": function_call})
            for function_call in logic_flow
        ]
    )
    graph.add_edges_from(edges)

    return graph


def validate_legal_wiring(
    logic_flow: List[FunctionCall],
    allow_one_ended_wires: bool = False,
    flow_input_names: Optional[List[str]] = None,
    flow_output_names: Optional[List[str]] = None,
    should_raise: bool = True,
) -> List[str]:
    flow_input_names = list() if flow_input_names is None else flow_input_names
    flow_output_names = list() if flow_output_names is None else flow_output_names

    call_input_names: List[str] = list(
        chain(*(function_call.non_zero_input_wires for function_call in logic_flow))
    )
    call_output_names: List[str] = list(
        chain(*(function_call.non_zero_output_wires for function_call in logic_flow))
    )

    if (
        len(set(call_input_names)) == len(call_input_names)
        and len(set(call_output_names)) == len(call_output_names)
        and (
            allow_one_ended_wires
            or sorted(call_input_names + flow_output_names)
            == sorted(call_output_names + flow_input_names)
        )
    ):
        return list()

    error_messages = list()

    recurring_names: List[str] = _recurring_names(
        call_input_names + flow_output_names
    ) + _recurring_names(call_output_names + flow_input_names)

    if recurring_names:
        error_messages.append(f"{RECURRING_NAMES_ERROR_MSG}: {recurring_names}")

    if allow_one_ended_wires:
        if should_raise:
            raise ValueError(_join_errors(error_messages))
        return list()

    unconnected_flow_ios = [
        name for name in flow_input_names if name not in call_input_names
    ] + [name for name in flow_output_names if name not in call_output_names]
    if unconnected_flow_ios:
        error_messages.append(
            f"{UNCONNECTED_FLOW_IO_ERROR_MSG}: {unconnected_flow_ios}"
        )

    unconnected_wires = [
        name
        for name in call_input_names
        if name not in call_output_names and name not in flow_input_names
    ] + [
        name
        for name in call_output_names
        if name not in call_input_names and name not in flow_output_names
    ]
    if unconnected_wires:
        error_messages.append(f"{UNCONNECTED_WIRES_ERROR_MSG}: {unconnected_wires}")

    if should_raise:
        raise ValueError(_join_errors(error_messages))
    return unconnected_wires


def _join_errors(error_messages: List[str]) -> str:
    if not error_messages:
        error_messages.append(f"{UNKNOWN_ERROR_MSG}")

    return "\n".join(error_messages)


def _recurring_names(name_list: List[str]) -> List[str]:
    name_counter = Counter(name_list)
    return [name for name, appearances in name_counter.items() if appearances > 1]


def validate_acyclic_logic_flow(
    logic_flow: List[FunctionCall],
    allow_one_ended_wires: bool = False,
    flow_input_names: List[str] = None,
    flow_output_names: List[str] = None,
) -> nx.DiGraph:
    flow_input_names = list() if flow_input_names is None else flow_input_names
    flow_output_names = list() if flow_output_names is None else flow_output_names

    graph = _create_flow_graph(
        logic_flow=logic_flow,
        allow_one_ended_wires=allow_one_ended_wires,
        flow_input_names=flow_input_names,
        flow_output_names=flow_output_names,
    )

    if not nx.algorithms.is_directed_acyclic_graph(graph):
        cycles = list(nx.algorithms.simple_cycles(graph))
        raise ValueError(CYCLE_ERROR_MSG + ". Cycles are: " + str(cycles))

    return graph


def validate_acyclicity_and_topologically_sort_logic_flow(
    logic_flow: List[FunctionCall],
    flow_input_names: List[str] = None,
    flow_output_names: List[str] = None,
) -> List[FunctionCall]:

    graph = validate_acyclic_logic_flow(
        logic_flow=logic_flow,
        flow_input_names=flow_input_names,
        flow_output_names=flow_output_names,
    )

    return [
        graph.nodes[call_name].get("function_call")
        for call_name in nx.topological_sort(graph)
    ]
