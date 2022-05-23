import os
import io
import requests

from .api import api_put

def upload_dataframe(namespace, df):
    with io.BytesIO() as f:
        df.to_csv(f, index=False)
        response = api_put('api/scratchpad', json=dict(filename = f'{namespace}.csv'))
        requests.put(response['url'], data=f.getvalue())
        return response['key']

def upload_file(filepath):
    with open(filepath, 'rb') as f:
        response = api_put('api/scratchpad', json=dict(filename = os.path.split(filepath)[1]))
        requests.put(response['url'], data=f)
        return response['key']