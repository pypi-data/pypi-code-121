import json

def get_auth(path):

    with open(path, 'r') as f:
        config = json.load(f)

    return config