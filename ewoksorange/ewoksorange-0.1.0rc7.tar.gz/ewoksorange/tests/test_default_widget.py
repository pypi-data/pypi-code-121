from ewokscore import Task
from ewokscore.utils import qualname
from ewoksorange.bindings import ewoks_to_ows


class Dummy(Task, input_names=["a"], output_names=["b"]):
    def run(self):
        self.outputs.b = self.inputs.a + 1
        print(self.inputs.a, "->", self.outputs.b)


def test_default_widgets(tmpdir, ewoks_orange_canvas):
    nodes = [
        {
            "id": "task1",
            "task_type": "class",
            "task_identifier": qualname(Dummy),
            "default_inputs": [{"name": "a", "value": 1}],
        },
        {
            "id": "task2",
            "task_type": "class",
            "task_identifier": qualname(Dummy),
        },
    ]

    links = [
        {
            "source": "task1",
            "target": "task2",
            "data_mapping": [{"source_output": "b", "target_input": "a"}],
        }
    ]

    # Create an Orange workflows
    graph = {"graph": {"id": "test_graph"}, "nodes": nodes, "links": links}
    destination = str(tmpdir / "ewoksgraph.ows")
    ewoks_to_ows(graph, destination)

    # Load and execute the orange workflow
    ewoks_orange_canvas.load_ows(destination)
    ewoks_orange_canvas.wait_widgets(timeout=10)
    results = dict(ewoks_orange_canvas.iter_output_values())

    assert results == {"task1": {"b": 2}, "task2": {"b": 3}}
