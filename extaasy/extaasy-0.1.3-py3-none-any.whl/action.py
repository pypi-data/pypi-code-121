#
# This file is part of the Ingram Micro CloudBlue Connect EaaS Extension Library.
#
# Copyright (c) 2022 Ingram Micro. All Rights Reserved.
#

"""
This module implements the objects to deserialize Connect public API Action request object
"""


class Action:
    """
    Deserialization object for action object of Connect public API
    """

    def __init__(self, method, querystring, headers, jwt_payload):
        self.method = method
        self.querystring = Querystring(**querystring)
        self.headers = headers
        self.jwt_payload = JwtPayload(**jwt_payload)


class Querystring:
    """
    Deserialization object for querystring object
    """

    def __init__(self, jwt):
        self.jwt = jwt


class JwtPayload:
    """
    Deserialization object for JWT payload object
    """

    def __init__(self, exp, action_id, api_url, asset_id):
        self.exp = exp
        self.action_id = action_id
        self.api_url = api_url
        self.asset_id = asset_id
