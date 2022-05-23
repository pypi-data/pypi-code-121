import pytest
from ewoksorange.bindings import OWWIDGET_TASKS_GENERATOR
from ewokscore.inittask import instantiate_task


@pytest.mark.parametrize(
    "widget_qualname",
    [
        "orangecontrib.list_operations.sumlist_one_thread.SumListOneThread",
        "orangecontrib.list_operations.sumlist_several_thread.SumListSeveralThread",
        "orangecontrib.list_operations.sumlist_stack.SumListWithTaskStack",
    ],
)
def test_sumlist(widget_qualname, register_ewoks_example_2_addon):
    node_attrs = {
        "task_type": "generated",
        "task_identifier": widget_qualname,
        "task_generator": OWWIDGET_TASKS_GENERATOR,
    }
    task = instantiate_task("node_id", node_attrs, inputs={"list": [1, 2, 3]})
    task.execute()
    assert task.output_values == {"sum": 6}


def test_listgenerator(register_ewoks_example_2_addon):
    node_attrs = {
        "task_type": "generated",
        "task_identifier": "orangecontrib.list_operations.listgenerator.ListGenerator",
        "task_generator": OWWIDGET_TASKS_GENERATOR,
    }
    task = instantiate_task("node_id", node_attrs, inputs={"length": [7]})
    task.execute()
    assert len(task.output_values["list"]) == 7


def test_printsum(register_ewoks_example_2_addon):
    node_attrs = {
        "task_type": "generated",
        "task_identifier": "orangecontrib.list_operations.print_sum.PrintSumOW",
        "task_generator": OWWIDGET_TASKS_GENERATOR,
    }
    task = instantiate_task("node_id", node_attrs, inputs={"sum": 99})
    task.execute()
    assert task.succeeded
    assert task.output_values == {}
