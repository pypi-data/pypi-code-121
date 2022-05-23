from typing import Optional
from ewoksorange.bindings import ewoks_to_ows
from ewokscore.tests.test_workflow_events import fetch_events
from ewokscore.tests.test_workflow_events import run_succesfull_workfow
from ewokscore.tests.test_workflow_events import run_failed_workfow


def execute_graph(
    graph, tempdir=None, canvas_handler=None, execinfo: Optional[dict] = None
):
    try:
        filename = str(tempdir / "test_graph.ows")
        ewoks_to_ows(graph, filename, execinfo=execinfo, error_on_duplicates=False)
        canvas_handler.load_ows(filename)
        canvas_handler.wait_widgets(timeout=10)
    finally:
        # Manually emit the end workflow and job event
        canvas_handler.scheme.ewoks_finalize()


def test_succesfull_workfow(tmpdir, ewoks_orange_canvas):
    uri = run_succesfull_workfow(
        tmpdir, execute_graph, tempdir=tmpdir, canvas_handler=ewoks_orange_canvas
    )
    events = fetch_events(uri, 14)
    assert_succesfull_workfow_events(events)


def test_failed_workfow(tmpdir, ewoks_orange_canvas):
    uri = run_failed_workfow(
        tmpdir, execute_graph, tempdir=tmpdir, canvas_handler=ewoks_orange_canvas
    )
    events = fetch_events(uri, 8)
    assert_failed_workfow_events(events)


def assert_succesfull_workfow_events(events):
    # TODO: double event are caused by a handleNewSignals call in the widget constructor
    expected = [
        {"context": "job", "node_id": None, "type": "start"},
        {"context": "workflow", "node_id": None, "type": "start"},
        {"context": "node", "node_id": "node1", "type": "start"},
        {"context": "node", "node_id": "node1", "type": "end"},
        {"context": "node", "node_id": "node2", "type": "start"},
        {"context": "node", "node_id": "node2", "type": "end"},
        {"context": "node", "node_id": "node3", "type": "start"},
        {"context": "node", "node_id": "node3", "type": "end"},
        {"context": "node", "node_id": "node2", "type": "start"},  # TODO: double event
        {"context": "node", "node_id": "node2", "type": "end"},  # TODO: double event
        {"context": "node", "node_id": "node3", "type": "start"},  # TODO: double event
        {"context": "node", "node_id": "node3", "type": "end"},  # TODO: double event
        {"context": "workflow", "node_id": None, "type": "end"},
        {"context": "job", "node_id": None, "type": "end"},
    ]
    captured = [
        {k: event[k] for k in ("context", "node_id", "type")} for event in events
    ]
    assert expected == captured


def assert_failed_workfow_events(events):
    # TODO: double event are caused by a handleNewSignals call in the widget constructor
    expected = [
        {"context": "job", "node_id": None, "type": "start", "error_message": None},
        {
            "context": "workflow",
            "node_id": None,
            "type": "start",
            "error_message": None,
        },
        {"context": "node", "node_id": "node1", "type": "start", "error_message": None},
        {"context": "node", "node_id": "node1", "type": "end", "error_message": None},
        {"context": "node", "node_id": "node2", "type": "start", "error_message": None},
        {"context": "node", "node_id": "node2", "type": "end", "error_message": "abc"},
        {
            "context": "node",
            "node_id": "node3",
            "type": "start",
            "error_message": None,
        },  # TODO: caused by clear_downstream
        {
            "context": "node",
            "node_id": "node3",
            "type": "end",
            "error_message": None,
        },  # TODO: caused by clear_downstream
        {
            "context": "node",
            "node_id": "node2",
            "type": "start",
            "error_message": None,
        },  # TODO: double event
        {
            "context": "node",
            "node_id": "node2",
            "type": "end",
            "error_message": "abc",
        },  # TODO: double event
        {
            "context": "node",
            "node_id": "node3",
            "type": "start",
            "error_message": None,
        },  # TODO: double event
        {
            "context": "node",
            "node_id": "node3",
            "type": "end",
            "error_message": None,
        },  # TODO: double event
        {
            "context": "workflow",
            "node_id": None,
            "type": "end",
            "error_message": None,  # TODO: should be "Task 'node2' failed"
        },
        {
            "context": "job",
            "node_id": None,
            "type": "end",
            "error_message": None,  # TODO: should be "Task 'node2' failed"
        },
    ]
    captured = [
        {k: event[k] for k in ("context", "node_id", "type", "error_message")}
        for event in events
    ]
    assert expected == captured
