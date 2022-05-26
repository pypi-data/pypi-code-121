# -*- coding: future_fstrings -*-
"""
constellations type class
"""

import json
import requests
from emcommon.common import esi_request


class Constellation:
    """ An eve online system type"""
    def __init__(self, constellation_id):
        self.constellation_id = constellation_id

    def info(self, field):
        """ Return the typeName for a given type_id"""
        request_url = f"https://esi.evetech.net/latest/universe/constellations/{self.constellation_id}/?datasource=tranquility&language=en"
        data = json.loads(esi_request(request_url, "GET"))
        if field is not None:
            return data[field]
        return data
