from flask import request, json
from typing import *

from ...libs.json_lib import load_json

class AlphaRequest:
    @staticmethod
    def get_gets() -> Dict[str, object]:
        """returns GET value as a dict.

        Returns:
            Dict[str, object]: [description]
        """
        return {x: y for x, y in request.args.items()}
    
    @staticmethod
    def get_json():
        data = {} #TODO: modify
        try:
            data = request.get_json()
        except:
            raw_data = request.data
            if isinstance(raw_data, bytes):
                raw_data = raw_data.decode()
            data = load_json(raw_data)
        if data is None or len(data) == 0:
            data = {}
        return data

    @staticmethod
    def get_uuid():
        data = AlphaRequest.get_json()
        request_uuid = request.full_path + "&" + "&".join("%s=%s" % (x, y) for x, y in data.items())
        return request_uuid
    
    @staticmethod
    def get_token():
        token = None
        # Get token from authorization bearer
        auth = request.headers.get("Authorization", None)
        if auth is not None:
            if "bearer" in auth.lower():
                parts = auth.split()
                if len(parts) > 1:
                    token = parts[1]

        # Token from get have priority if present
        token_from_get = request.args.get("token", None)
        if token_from_get is not None:
            token = token_from_get

        # Token from post
        dataPost = AlphaRequest.get_json()
        if dataPost is not None and "token" in dataPost:
            token = dataPost["token"]
        return token