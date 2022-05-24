from pypers.steps.fetch.download.ua import ua_specific_api_process
from pypers.steps.base.fetch_step_api import FetchStepAPI


class Designs(FetchStepAPI):
    spec = {
        "version": "2.0",
        "descr": [
            "Fetch using REST API"
        ],
        "args":
        {
            "params": [
                {
                    "name": "api",
                    "type": "str",
                    "descr": "the api end-point"
                },
                {
                    "name": "page",
                    "type": "int",
                    "value": 1
                }
            ],
            'outputs': [
                {
                    "name": 'last_date',
                    "type": "str",
                    "descr": "the download date from the feed"
                }
            ]
        }
    }

    def get_intervals(self):
        return []

    def _process_from_local_folder(self):
        return False

    def specific_api_process(self, session):
        return ua_specific_api_process(self, session)
