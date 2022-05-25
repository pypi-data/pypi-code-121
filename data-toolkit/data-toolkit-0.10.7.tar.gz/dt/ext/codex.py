import os
import requests
import json
import time

# construct a function that loads my openai API key from home and then calls it
def load_api_key(api_key_file):
    api_key = json.loads(open(api_key_file).read())['cai_key']
    return api_key

# construct a function that calls the openai codex and returns the results
def constuct_call(api_key, prompt):
    engine = 'cushman-codex' # codex engine could also be
    # engine = 'davinci-codex'
    url = f'https://api.openai.com/v1/engines/{engine}/completions'
    data = { 'prompt': prompt, 'max_tokens' : 200  } # 'stream': True

    # convert data to json
    json_data = json.dumps(data)

    headers = {'Authorization': 'Bearer {}'.format(api_key),
                'Content-Type': 'application/json'}
    response = requests.post(url, json_data, headers=headers)
    return response
    
def get_cai_suggestions(query: str, n_suggestions: int = 5):
    # measure timing 
    start = time.time()
    # get the api key from the home directory 
    api_path = os.path.join(os.path.expanduser('~'), 'dt_config.json')
    api_key = load_api_key(api_path)
    response = constuct_call(api_key, query)
    after = time.time()
    print('API call took {} seconds'.format(after - start))
    # convert response to dict from string 
    response_dict = json.loads(response.text)

    end = time.time()
    print('Total time was {} seconds'.format(end - start))

    return response_dict

