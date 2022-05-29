import collections.abc
from flask import jsonify

def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class APISuccess():
    def __init__(self, d={}):
        self.d = d
        self.d.update({"success": True})
    
    def json(self):
        return jsonify(self.d)
    
class APIError():
    def __init__(self, message=""):
        self.d = {
            "success": False,
            "message": message
        }
    
    def json(self):
        return jsonify(self.d)
