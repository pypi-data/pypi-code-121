import pytest
from ewoksorange.bindings import OWWIDGET_TASKS_GENERATOR
from ewokscore.task import TaskInputError
from ewokscore.inittask import instantiate_task


@pytest.mark.parametrize(
    "widget_qualname",
    [
        "orangecontrib.ewoks_example_supercategory.ewoks_example_subcategory.adder1.Adder1",
        "orangecontrib.ewoks_example_supercategory.ewoks_example_subcategory.adder2.Adder2",
        "orangecontrib.evaluate.ewoks_example_submodule.adder1.Adder1",
        "orangecontrib.evaluate.ewoks_example_submodule.adder2.Adder2",
        "orangecontrib.ewoks_example_category.adder1.Adder1",
        "orangecontrib.ewoks_example_category.adder2.Adder2",
    ],
)
def test_adder_missing_inputs(widget_qualname, register_ewoks_example_1_addon):
    node_attrs = {
        "task_type": "generated",
        "task_identifier": widget_qualname,
        "task_generator": OWWIDGET_TASKS_GENERATOR,
    }
    with pytest.raises(TaskInputError):
        instantiate_task("node_id", node_attrs)


@pytest.mark.parametrize(
    "widget_qualname",
    [
        "orangecontrib.ewoks_example_supercategory.ewoks_example_subcategory.adder1.Adder1",
        "orangecontrib.ewoks_example_supercategory.ewoks_example_subcategory.adder2.Adder2",
        "orangecontrib.evaluate.ewoks_example_submodule.adder1.Adder1",
        "orangecontrib.evaluate.ewoks_example_submodule.adder2.Adder2",
        "orangecontrib.ewoks_example_category.adder1.Adder1",
        "orangecontrib.ewoks_example_category.adder2.Adder2",
    ],
)
def test_adder_all_inputs(widget_qualname, register_ewoks_example_1_addon):
    node_attrs = {
        "task_type": "generated",
        "task_identifier": widget_qualname,
        "task_generator": OWWIDGET_TASKS_GENERATOR,
    }
    task = instantiate_task("node_id", node_attrs, inputs={"a": 1, "b": 2})
    task.execute()
    assert task.output_values == {"result": 3}
