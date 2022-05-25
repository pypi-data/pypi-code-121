import requests
import json
import sys
from server.token_generator import tokenGenerator

env = sys.argv[1]
model_name = sys.argv[2]
model_id = sys.argv[3]


t = tokenGenerator()
jwtToken = t.generateToken(env.upper() + '_Conf')

data = {
	"model_type_id": model_id
}
url = "https://dsp.zoominfo.com/api/v1/truth-datasets/getDatasetOptions"
if env == 'stg':
	url = "https://dsp-stg.zoominfo.com/api/v1/truth-datasets/getDatasetOptions"
headers = {
	'x-token': 'fake-super-secret-token',
	'Authorization': 'Bearer ' + jwtToken
}

response = requests.post(url, json=data, headers=headers)
try:
	result = json.loads(response.content)
	datasets = result['data']['datasets']
	dataset_options = [{'dataset_name': dataset['dataset_name'], 'id': dataset['id']} for dataset in datasets]
	if len(dataset_options) == 0:
		print(f'no dataset options for model named {model_name} in dsp')
	else:
		print(dataset_options)
except Exception as e:
	print('error', e)
