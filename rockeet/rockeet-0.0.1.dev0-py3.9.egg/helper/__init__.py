"""
Copyright (c) 2022 Philipp Scheer
"""


import json
import re
import requests
from rockeet import getToken, baseUrl, logger


class Response:
    def __init__(self, data, sourceUrl: str, sourceBody, sourceMethod: str, raw: bool = False) -> None:
        self.data = data
        self.sUrl = sourceUrl
        self.sBody = sourceBody
        self.sMethod = sourceMethod
        if not raw and not self.success:
            raise ValueError(f"request failed: {self.sMethod}@{self.sUrl} ({self.sBody}) -> {self.data}")
    
    @property
    def success(self):
        return self.data["success"]
    
    @property
    def result(self):
        return self.data["result"]

    def unpack(self, *params):
        if isinstance(self.result, dict):
            return { k:v for k,v in self.result.items() if k in params }
        elif isinstance(self.result, list):
            raise ValueError("cannot unpack list")
        return { k: self.result for k in params }
    
    def __str__(self) -> str:
        return json.dumps(self.data, indent=4)



def isFileId(tester):
    return bool(re.match(r'^(f_|p_)[a-fA-F0-9]+$', tester))

def isLocalFile(tester):
    return not isFileId(tester)

def endpoint(url, body, method: str = "post", raw: bool = False) -> Response:
    logger.debug(f"endpoint {url} method={method}, body={json.dumps(body, indent=4)}")
    if raw:
        return Response(requests.request(method.lower(), baseUrl + url, 
            json=body,
            headers={ "Authorization": getToken() }
        ), url, body, method, raw)
    else:
        return Response(requests.request(method.lower(), baseUrl + url, 
            json=body,
            headers={ "Authorization": getToken() }
        ).json(), url, body, method, raw)
