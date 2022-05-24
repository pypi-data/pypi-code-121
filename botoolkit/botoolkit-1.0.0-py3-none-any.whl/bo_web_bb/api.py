from json.decoder import (
    JSONDecodeError,
)

import requests
from requests.exceptions import (
    ConnectionError,
    ReadTimeout,
)
from simplejson.errors import (
    JSONDecodeError as SimpleJSONDecodeError,
)
from urllib3.exceptions import (
    MaxRetryError,
    NewConnectionError,
)

from botoolkit.bo_web_bb.exceptions import (
    AppConfigUUIDCanNotGetFromServer,
    AppConfigUUIDNotFound,
)


class WebBBAPI:
    def __init__(
        self,
        stand_url: str,
    ):
        self._stand_url = stand_url

    def get_app_config_uuid(self):
        config_uuid_url = f'{self._stand_url}config-uuid/'

        try:
            response = requests.get(
                url=config_uuid_url,
                timeout=10,
            )
            data = response.json()
            app_config_uuid = data.get('app_config_uuid')
        except (
            JSONDecodeError,
            SimpleJSONDecodeError,
            ConnectionError,
            ReadTimeout,
            NewConnectionError,
            MaxRetryError,
        ):
            raise AppConfigUUIDCanNotGetFromServer(
                f'Can not get UUID from server by url - {config_uuid_url}'
            )

        if not app_config_uuid:
            raise AppConfigUUIDNotFound(
                f'Can not get UUID from server by url - {config_uuid_url}'
            )

        return app_config_uuid
