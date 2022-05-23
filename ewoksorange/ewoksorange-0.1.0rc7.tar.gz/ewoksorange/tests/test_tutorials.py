import pytest
from ewoksorange.bindings import ows_to_ewoks
from ewoksorange.orange_version import ORANGE_VERSION
from ewokscore import execute_graph

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources


def test_sumtask_tutorial1_with_qt(ewoks_orange_canvas):
    from orangecontrib.ewoks_example_category import tutorials

    with resources.path(tutorials, "sumtask_tutorial1.ows") as filename:
        assert_sumtask_tutorial_with_qt(ewoks_orange_canvas, filename)


@pytest.mark.skipif(
    ORANGE_VERSION != ORANGE_VERSION.latest_orange, reason="Requires Orange3 widgets"
)
def test_sumtask_tutorial1_without_qt(register_ewoks_example_addons):
    from orangecontrib.ewoks_example_category import tutorials

    with resources.path(tutorials, "sumtask_tutorial1.ows") as filename:
        assert_sumtask_tutorial_without_qt(filename)


def test_sumtask_tutorial2_with_qt(ewoks_orange_canvas):
    from orangecontrib.evaluate.ewoks_example_submodule import tutorials

    with resources.path(tutorials, "sumtask_tutorial2.ows") as filename:
        assert_sumtask_tutorial_with_qt(ewoks_orange_canvas, filename)


def test_sumtask_tutorial2_without_qt(ewoks_orange_canvas):
    from orangecontrib.evaluate.ewoks_example_submodule import tutorials

    with resources.path(tutorials, "sumtask_tutorial2.ows") as filename:
        assert_sumtask_tutorial_without_qt(filename)


def test_sumtask_tutorial3_with_qt(ewoks_orange_canvas):
    from orangecontrib.ewoks_example_supercategory.ewoks_example_subcategory import (
        tutorials,
    )

    with resources.path(tutorials, "sumtask_tutorial3.ows") as filename:
        assert_sumtask_tutorial_with_qt(ewoks_orange_canvas, filename)


def test_sumtask_tutorial3_without_qt(ewoks_orange_canvas):
    from orangecontrib.ewoks_example_supercategory.ewoks_example_subcategory import (
        tutorials,
    )

    with resources.path(tutorials, "sumtask_tutorial3.ows") as filename:
        assert_sumtask_tutorial_without_qt(filename)


def test_list_operations_with_qt(ewoks_orange_canvas):
    from orangecontrib.list_operations import tutorials

    with resources.path(tutorials, "sumlist_tutorial.ows") as filename:
        assert_sumlist_tutorial_with_qt(ewoks_orange_canvas, filename)


def test_list_operations_without_qt(ewoks_orange_canvas):
    from orangecontrib.list_operations import tutorials

    with resources.path(tutorials, "sumlist_tutorial.ows") as filename:
        assert_sumlist_tutorial_without_qt(filename)


@pytest.mark.skipif(
    ORANGE_VERSION != ORANGE_VERSION.latest_orange, reason="Requires Orange3 widgets"
)
def test_mixed_tutorial1_with_qt(ewoks_orange_canvas):
    from orangecontrib.ewoks_example_category import tutorials

    with resources.path(tutorials, "mixed_tutorial1.ows") as filename:
        assert_mixed_tutorial_with_qt(ewoks_orange_canvas, filename)


@pytest.mark.skipif(
    ORANGE_VERSION != ORANGE_VERSION.latest_orange, reason="Requires Orange3 widgets"
)
def test_mixed_tutorial1_without_qt(register_ewoks_example_addons):
    from orangecontrib.ewoks_example_category import tutorials

    with resources.path(tutorials, "mixed_tutorial1.ows") as filename:
        assert_mixed_tutorial_without_qt(filename)


def assert_sumtask_tutorial_with_qt(ewoks_orange_canvas, filename):
    """Execute workflow using the Qt widgets and signals"""
    ewoks_orange_canvas.load_ows(str(filename))
    ewoks_orange_canvas.wait_widgets(timeout=10)
    widgets = list(ewoks_orange_canvas.widgets_from_name("task6"))
    results = widgets[0].task_output_values
    assert results == {"result": 16}


def assert_sumtask_tutorial_without_qt(filename):
    """Execute workflow after converting it to an ewoks workflow"""
    graph = ows_to_ewoks(filename)
    results = execute_graph(graph, output_tasks=True)
    assert results["5"].output_values == {"result": 16}


def assert_sumlist_tutorial_with_qt(ewoks_orange_canvas, filename):
    """Execute workflow using the Qt widgets and signals"""
    ewoks_orange_canvas.load_ows(str(filename))

    # Remove artificial delay for this test
    for widget in ewoks_orange_canvas.iter_widgets():
        if "delay" in widget.default_inputs:
            widget.default_inputs["delay"] = 0

    wgenerator = list(ewoks_orange_canvas.widgets_from_name("List generator"))[0]
    wgenerator.defaultInputsHaveChanged()
    results = wgenerator.task_output_values
    listsum = sum(results["list"])

    ewoks_orange_canvas.wait_widgets(timeout=10)

    widgets = list(ewoks_orange_canvas.widgets_from_name("Print list sum"))
    widgets = list(ewoks_orange_canvas.widgets_from_name("Print list sum (1)"))
    widgets = list(ewoks_orange_canvas.widgets_from_name("Print list sum (2)"))
    for w in widgets:
        results = {name: var.value for name, var in w.task_inputs.items()}
        assert results == {"sum": listsum}


def assert_sumlist_tutorial_without_qt(filename):
    """Execute workflow after converting it to an ewoks workflow"""
    graph = ows_to_ewoks(filename)

    # Remove artificial delay for this test
    for attrs in graph.graph.nodes.values():
        for adict in attrs.get("default_inputs", list()):
            if adict["name"] == "delay":
                adict["value"] = 0

    results = execute_graph(graph, output_tasks=True)
    listsum = sum(results["0"].output_values["list"])
    for i in [4, 5, 6]:
        assert results[str(i)].input_values == {"sum": listsum}


def assert_mixed_tutorial_with_qt(ewoks_orange_canvas, filename):
    """Execute workflow using the Qt widgets and signals"""
    ewoks_orange_canvas.load_ows(str(filename))
    ewoks_orange_canvas.wait_widgets(timeout=10)
    widgets = list(ewoks_orange_canvas.widgets_from_name("Adder2"))
    results = widgets[0].task_output_values
    assert results == {"result": 3}


def assert_mixed_tutorial_without_qt(filename):
    """Execute workflow after converting it to an ewoks workflow"""
    graph = ows_to_ewoks(filename)
    results = execute_graph(graph, output_tasks=True)
    assert results["1"].output_values == {"result": 3}
