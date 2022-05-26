import json


def as_json(data, default='[]'):
    if data is None:
        return json.loads(default)
    if len(data) == 0:
        return json.loads(default)
    return json.loads(data)


def as_pretty_json(json_data, indent=4):
    return json.dumps(json_data, indent=indent, sort_keys=True)
