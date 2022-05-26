from dataclasses import dataclass
from enum import Enum
import json
import requests
from typing import Optional, Dict, List, Union, Tuple
from pathlib import Path

class ProauthRequestException(Exception):
    status_code = 200

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

class ProauthRequestType(Enum):
    CREATE = 0
    READ = 1
    UPDATE = 2
    DELETE = 3

@dataclass
class ProauthUserAuth:
    refresh_token: str
    access_token: str
    result: str

@dataclass
class ProauthRequestResult:
    data: Optional[Union[Dict, List[Dict], bytes]]
    content: Optional[str]
    status_code: Optional[int]

class ProauthHttpClient:
    def __init__(self, proauth_addr):
        self.base_url = proauth_addr + "/proauth/oauth"

    def send_request(
        self,
        service: str,
        rest: Optional[dict],
        query: Optional[dict],
        data: Union[Optional[dict], Path],
        request_type: ProauthRequestType,
    ) -> ProauthRequestResult:
        headers = {
            "Content-Type": "application/json"
        }

        if rest is None:
            rest = {}

        if query is None:
            query = {}

        if data is None:
            data = {}

        url = self.base_url
        for key, val in rest.items():
            url = url + "/" + str(key) + "/" + str(val)
        if service != "" and service is not None:
            url = url + "/" + service

        if len(query) != 0:
            url += "?"
            for idx, (key, val) in enumerate(query.items()):
                if idx != 0:
                    url += "&"
                url = url + str(key) + "=" + str(val)

        if request_type == ProauthRequestType.READ:
            response = requests.get(url, headers=headers, json=data, verify=False)
        elif request_type == ProauthRequestType.CREATE:
            if isinstance(data, Path):
                headers.pop("Content-Type", None)
                response = requests.post(url, headers=headers, files={"file": open(data, "rb")})
            else:
                response = requests.post(url, headers=headers, json=data, verify=False)
        elif request_type == ProauthRequestType.UPDATE:
            response = requests.put(url, headers=headers, json=data, verify=False)
        elif request_type == ProauthRequestType.DELETE:
            response = requests.delete(url, headers=headers, json=data, verify=False)
        else:
            raise ProauthRequestException(status_code=405, message=f"{request_type} method not allowed.")

        if response.status_code == 200:
            return ProauthRequestException(response.json(), response.status_code)
        else:
            print(
                (
                    f"{service} {request_type.value} failed\n"
                    f"status_code: {response.status_code}.\n"
                    f"reason: {response.text}\n"
                )
            )
            raise ProauthRequestException(response.content.decode(), response.status_code)


    def update_token(self, refresh_token: str) -> Tuple[str, str, str]:
        print("===proauth_http_client update_token()=====")
        result = self.send_request(
            "authenticate",
            {},
            {},
            {"refresh_token" : refresh_token},
            ProauthRequestType.UPDATE
        )
        return result.result, result.refresh_token, result.access_token