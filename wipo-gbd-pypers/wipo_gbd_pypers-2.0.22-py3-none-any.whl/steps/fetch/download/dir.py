from pypers.steps.base.fetch_step import FetchStep


class Dir(FetchStep):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch archives from either a local dir"
        ],
    }

    def specific_process(self):
        return
