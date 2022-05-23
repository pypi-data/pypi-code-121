try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources
import pytest
from ewoksorange.bindings import ows_to_ewoks
from ewoksorange.bindings import ewoks_to_ows
from ewoksorange.bindings import graph_is_supported
from ewokscore import load_graph
from ewokscore.tests.examples.graphs import graph_names
from ewokscore.tests.examples.graphs import get_graph


def test_ows_to_ewoks_example_1(tmpdir, register_ewoks_example_addons):
    """Test conversion of orange worflow files to ewoks and back"""
    from orangecontrib.evaluate.ewoks_example_submodule import tutorials

    with resources.path(tutorials, "sumtask_tutorial2.ows") as filename:
        ewoksgraph = ows_to_ewoks(str(filename))

    destination = str(tmpdir / "ewoksgraph.ows")
    ewoks_to_ows(ewoksgraph, destination, error_on_duplicates=False)
    ewoksgraph2 = ows_to_ewoks(destination)
    assert ewoksgraph == ewoksgraph2


def test_ows_to_ewoks_example_2(tmpdir, register_ewoks_example_addons):
    """Test conversion of orange worflow files to ewoks and back"""
    from orangecontrib.list_operations import tutorials

    with resources.path(tutorials, "sumlist_tutorial.ows") as filename:
        ewoksgraph = ows_to_ewoks(str(filename))

    destination = str(tmpdir / "ewoksgraph.ows")
    ewoks_to_ows(ewoksgraph, destination)
    ewoksgraph2 = ows_to_ewoks(destination)
    assert ewoksgraph == ewoksgraph2


@pytest.mark.parametrize("graph_name", graph_names())
def test_ewoks_to_ows(graph_name, tmpdir):
    """Test conversion of ewoks to orange worflow files and back"""
    graph, _ = get_graph(graph_name)
    ewoksgraph = load_graph(graph)
    for node_id, node_attrs in ewoksgraph.graph.nodes.items():
        node_attrs["label"] = node_id

    destination = str(tmpdir / "ewoksgraph2.ows")
    if not graph_is_supported(ewoksgraph):
        with pytest.raises(RuntimeError):
            ewoks_to_ows(ewoksgraph, destination)
        return

    ewoks_to_ows(ewoksgraph, destination, error_on_duplicates=False)
    ewoksgraph2 = ows_to_ewoks(
        destination, title_as_node_id=True, preserve_ows_info=False
    )
    assert ewoksgraph == ewoksgraph2
