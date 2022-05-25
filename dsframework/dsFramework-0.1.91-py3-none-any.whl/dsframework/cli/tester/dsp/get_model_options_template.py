import requests
import json
import sys
from server.token_generator import tokenGenerator

env = sys.argv[1]

t = tokenGenerator()
jwtToken = t.generateToken(env.upper() + '_Conf')

main_model = 'original_project_name'
repo = 'dozi/' + main_model
data = ""
url = "https://dsp.zoominfo.com/api/v1/models/getModelOptions"
if env == 'stg':
	url = "https://dsp-stg.zoominfo.com/api/v1/models/getModelOptions"
headers = {
	'x-token': 'fake-super-secret-token',
	'Authorization': 'Bearer ' + jwtToken
}

response = requests.post(url, json=data, headers=headers)
try:
	result = json.loads(response.content)
	models = result['data']['models']
	model_options = [{'name': model['name'], 'id': model['id'], 'repo': model['repo']} for model in models if model['repo'] == repo]
	if len(model_options) == 0:
		print(f'no model named {main_model} in dsp')
	else:
		if not len(model_options):
			print(f'cant find model name {main_model} in dsp')
		else:
			print(model_options)
except Exception as e:
	print('error', e)
