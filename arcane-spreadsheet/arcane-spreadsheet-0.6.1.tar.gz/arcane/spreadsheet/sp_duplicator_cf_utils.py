import json
import backoff
import requests
from typing import Dict
from arcane import requests as _requests
from arcane.core import UserRightsEnum, RightsLevelEnum

def request_spreadsheet_duplicator_cf(
    data: Dict[str, str],
    firebase_api_key: str,
    CF_SPREADSHEET_DUPLICATOR_URL: str,
    adscale_key: str
    ):
    try:
        response = _requests.request_service(
            method='POST',
            url=CF_SPREADSHEET_DUPLICATOR_URL,
            firebase_api_key=firebase_api_key,
            claims={'features_rights': {UserRightsEnum.AMS_LAB: RightsLevelEnum.VIEWER}},
            credentials_path=adscale_key,
            retry_decorator=backoff.on_exception(
                                                    backoff.expo,
                                                    (ConnectionError, requests.HTTPError, requests.Timeout),
                                                    3
                                                ),
            data=json.dumps(data)
        )
    except requests.exceptions.HTTPError as e:
        error_code = e.response.status_code
        if error_code in [404, 403, 401]: # error code corresponding to filenotfound et bad authorization
            response_data = json.loads(e.response.content)
            return response_data, error_code
        return e
    return response.json()
