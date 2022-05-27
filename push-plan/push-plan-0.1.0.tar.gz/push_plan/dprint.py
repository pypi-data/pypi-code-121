# Debug printing for config object

import json
from json.encoder import JSONEncoder
from pathlib import Path
from types import SimpleNamespace

# Json default encoder is unable to encode path and namespace
# A custom encoder is used instead


class ConfigEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SimpleNamespace):
            return obj.__dict__
        elif isinstance(obj, Path):
            return str(obj)
        else:
            return JSONEncoder.default(self, obj)


def dprint(config):
    """Print config on terminal as json"""
    conf_encoded = json.dumps(config, cls=ConfigEncoder)
    print(conf_encoded)
