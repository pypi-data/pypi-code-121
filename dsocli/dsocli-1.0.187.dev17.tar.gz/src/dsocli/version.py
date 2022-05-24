import os
import json


with open(os.path.join(os.path.dirname(__file__), 'package.json')) as f:
    _info = json.load(f)

__version__ = _info['version']
