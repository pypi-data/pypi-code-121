import json
import os

def readJsonFileOrDict(jsonInput):
    if isinstance(jsonInput, str):
        try:
            with open(jsonInput) as fh:
                return json.load(fh)
        except FileNotFoundError as e:
            print('input file {0} does not exist.'.format(jsonInput), flush=True)
            raise
        except json.decoder.JSONDecodeError as e:
            print('Invalid json:', e)
            raise
    elif isinstance(jsonInput, dict):
        return jsonInput
    else:
        raise TypeError('Input file has wrong type.')
