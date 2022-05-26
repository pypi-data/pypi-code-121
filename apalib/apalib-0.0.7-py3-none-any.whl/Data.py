import pkg_resources
import json

class Data:
    def __init__(self):
        _stream = pkg_resources.resource_stream(__name__, 'data/residues_2.json')
        self._jData = json.load(_stream)

    def GetJson(self):
        return self._jData

    def Map(self, dtype, val):
        return self._jData["Map"][dtype][val]