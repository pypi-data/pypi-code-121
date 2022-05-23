import os
import sys
import tempfile
from typing import Any, Optional, List

import ewokscore
from ewokscore.graph import TaskGraph
from . import owsconvert
from ..canvas.main import main as launchcanvas


__all__ = [
    "execute_graph",
    "load_graph",
    "save_graph",
    "convert_graph",
]


@ewokscore.execute_graph_decorator(binding="orange")
def execute_graph(
    graph,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    outputs: Optional[List[dict]] = None,
    merge_outputs: Optional[bool] = True,
    **execute_options,
) -> None:
    if outputs:
        raise ValueError("The Orange3 binding cannot return any results")
    if load_options is None:
        load_options = dict()
    representation = _get_representation(graph, options=load_options)
    if representation == "ows":
        ows_filename = graph
        if inputs or load_options or execute_options:
            # Already an .ows file but modify it before launching the GUI
            with tempfile.TemporaryDirectory(prefix="ewoksorange_") as tmpdirname:
                basename = os.path.splitext(os.path.basename(ows_filename))[0]
                ows_filename2 = os.path.join(tmpdirname, f"{basename}.ows")
                graph = owsconvert.ows_to_ewoks(ows_filename)
                owsconvert.ewoks_to_ows(
                    graph,
                    ows_filename2,
                    inputs=inputs,
                    **load_options,
                    **execute_options,
                )
                argv = [sys.argv[0], ows_filename2]
                launchcanvas(argv=argv)
        else:
            # Already an .ows file
            argv = [sys.argv[0], ows_filename]
            launchcanvas(argv=argv)
    else:
        # Convert to an .ows file before launching the GUI
        with tempfile.TemporaryDirectory(prefix="ewoksorange_") as tmpdirname:
            ows_filename = os.path.join(tmpdirname, "graph.ows")
            owsconvert.ewoks_to_ows(
                graph, ows_filename, inputs=inputs, **load_options, **execute_options
            )
            argv = [sys.argv[0], ows_filename]
            launchcanvas(argv=argv)


def load_graph(
    graph: Any,
    inputs: Optional[List[dict]] = None,
    preserve_ows_info: Optional[bool] = True,
    title_as_node_id: Optional[bool] = False,
    **load_options,
) -> TaskGraph:
    representation = _get_representation(graph, options=load_options)
    if representation == "ows":
        load_options.pop("representation", None)
        return owsconvert.ows_to_ewoks(
            graph,
            inputs=inputs,
            preserve_ows_info=preserve_ows_info,
            title_as_node_id=title_as_node_id,
            **load_options,
        )
    else:
        return ewokscore.load_graph(graph, inputs=inputs, **load_options)


def save_graph(graph: TaskGraph, destination, **save_options) -> Optional[str]:
    representation = _get_representation(destination, options=save_options)
    if representation == "ows":
        return owsconvert.ewoks_to_ows(graph, destination, **save_options)
    else:
        return graph.dump(destination, **save_options)


def convert_graph(
    source,
    destination,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    save_options: Optional[dict] = None,
):
    if load_options is None:
        load_options = dict()
    if save_options is None:
        save_options = dict()
    graph = load_graph(source, inputs=inputs, **load_options)
    return save_graph(graph, destination, **save_options)


def _get_representation(graph: Any, options: Optional[dict] = None):
    representation = None
    if options:
        representation = options.get("representation")
    if (
        representation is None
        and isinstance(graph, str)
        and graph.lower().endswith(".ows")
    ):
        representation = "ows"
    return representation
