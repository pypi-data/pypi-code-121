from pypers.steps.base.fetch_step_api import FetchStepAPI
from pypers.steps.fetch.download.ua import ua_specific_api_process


class Trademarks(FetchStepAPI):
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

    # --------------------------------------------------- #
    # 10 document page: https://sis.ukrpatent.org/api/v0/open-data/
    # ?changed=0&date_from=01.01.2019&date_to=31.12.2019&obj_type=4
    #
    # Individual media files: /media/TRADE_MARKS/2019/m201913737/271844.jpeg
    # (MarkImageFileName node value)
    # => Media URL : https://sis.ukrpatent.org/media/TRADE_MARKS/2019
    # /m201913737/271844.jpeg
    #
    # Trademarks             : obj_type=4
    # Appelations of origin  : obj_type=5
    # Industrial designs     : obj_type=6
    # --------------------------------------------------- #
    def specific_api_process(self, session):
        return ua_specific_api_process(self, session)
