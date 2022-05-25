import requests
import json
import sys
from server.token_generator import tokenGenerator

env = sys.argv[1]
model = json.loads(sys.argv[2])
dataset = json.loads(sys.argv[3])
tag_name = sys.argv[4]

t = tokenGenerator()
jwtToken = t.generateToken(env.upper() + '_Conf')

data = {
    "model_type_id": model['id'],
    "model_name": model['name'],
    "repo_tag": tag_name,
    "repo": model['repo'],
    "dataset_id": dataset['id'],
    "dataset_name": dataset['dataset_name'],
    "created_by": "ori.braun@zoominfo.com"
}
print('data', data)
url = "https://dsp.zoominfo.com/api/v1/experiment/add"
if env == 'stg':
    url = "https://dsp-stg.zoominfo.com/api/v1/experiment/add"
headers = {
    'x-token': 'fake-super-secret-token',
    'Authorization': 'Bearer ' + jwtToken
}

response = requests.post(url, json=data, headers=headers)
try:
    result = json.loads(response.content)
    print(result)
except Exception as e:
    print('error', e)
