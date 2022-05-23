def test_workflow():
    return {
        "graph": {"id": "sleepgraph", "version": "1.0"},
        "nodes": [
            {
                "id": "sleepnode",
                "task_type": "method",
                "task_identifier": "time.sleep",
                "default_inputs": [{"name": 0, "value": 0}],
            }
        ],
    }
