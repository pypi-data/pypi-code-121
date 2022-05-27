import json
import os

import pandas as pd
import requests
from IPython.core.magic import Magics, line_cell_magic, magics_class, needs_local_scope

from thanosql.exceptions import (
    ThanoSQLConnectionError,
    ThanoSQLInternalError,
    ThanoSQLSyntaxError,
)
from thanosql.parse import *
from thanosql.spinner import Spinner
from thanosql.utils import print_audio, print_image, print_video

DEFAULT_API_URL = "https://engine.thanosql.ai/api/v1/query"
spinner = Spinner()


@magics_class
class ThanosMagic(Magics):
    @needs_local_scope
    @line_cell_magic
    def thanosql(self, line: str = None, cell: str = None, local_ns={}):
        if line:
            if is_url(line):
                # Set API URL
                api_url = line.strip()
                os.environ["API_URL"] = api_url
                print(f"API URL is changed to {api_url}")
                return

            elif is_api_token(line):
                # Set API Token
                api_token = line.strip().split("API_TOKEN=")[-1]
                os.environ["API_TOKEN"] = api_token
                print(f"API Token is set as '{api_token}'")
                return

            # 'line' will treat as same as 'cell'
            else:
                cell = line

        if not cell:
            return

        api_url = os.getenv("API_URL", DEFAULT_API_URL)
        api_token = os.getenv("API_TOKEN", None)

        if not api_token:
            raise ThanoSQLConnectionError(
                "An API Token is requierd. Set the API Token by running the following: %thanosql API_TOKEN=<API_TOKEN>"
            )
        header = {"Authorization": "Bearer " + api_token}

        query_string = cell
        if is_multiple_queries(query_string):
            raise ThanoSQLSyntaxError("Multiple Queries are not supported.")

        res = None
        if query_string:
            query_string = convert_local_ns(query_string, local_ns)

            data = {"query_string": query_string}
            try:
                spinner.start()
                res = requests.post(api_url, data=json.dumps(data), headers=header)
            except:
                raise ThanoSQLConnectionError(
                    "ThanoSQL Engine is not ready for connection."
                )
            finally:
                spinner.stop()

            if res.status_code == 200:
                data = res.json().get("data")
                query_result = data.get("df")
                if query_result:
                    result = pd.read_json(query_result, orient="split")

                    print_type = data.get("print")
                    print_option = data.get("print_option")
                    if print_type:
                        if print_type == "print_image":
                            return print_image(result, print_option)
                        elif print_type == "print_audio":
                            return print_audio(result, print_option)
                        elif print_type == "print_video":
                            return print_video(result, print_option)
                    return result

                print("Success")
                return

            elif res.status_code == 500:
                data = res.json()
                reason = data.get("message")
                if reason:
                    raise ThanoSQLInternalError(reason)
        return


# In order to actually use these magics, you must register them with a
# running IPython.
def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(ThanosMagic)
