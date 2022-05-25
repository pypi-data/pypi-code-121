import requests
import json
from http import HTTPStatus
from pipeline.schema.inputs import generatedProjectNameInputs
from token_generator import tokenGenerator
##
# @file
# @brief test_server_post is used in order to check
#        the service liveness for example or post a request and get the data (response) back.
#        (only for checking use)

t = tokenGenerator()
jwtToken = t.generateToken('STG_Conf')
global_headers = {
    'x-token': 'fake-super-secret-token',
    'Authorization': 'Bearer ' + jwtToken
}
base_url = 'http://localhost:8080/'


def post(endPoint, data):
    """! Post method, send post request to a specific URL and return the response back in the data.

     Args:
        data : json file data that will use for the request post.
        endPoint : end point of the URL. (base_url + endPoint will be the complete url)
     Returns:
        data : Response content
     """
    headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
    url = base_url + endPoint
    response = requests.post(url, json=data, headers=headers)
    print(f"Response elapsed time: {response.elapsed.total_seconds()}")
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        data = HTTPStatus.INTERNAL_SERVER_ERROR.description
    else:
        try:
            data = json.loads(response.content)
        except Exception as ex:
            data = response.content
    return data


def get(endPoint, data):
    """! Get method, send get request to a specific URL and return the response back.

     Args:
        data : data params that will use for the get request
        endPoint : end point of the URL. (base_url + endPoint will be the complete url)
     Returns:
        data : Response content
     """
    headers = {"Content-Type": "application/json; charset=UTF-8", **global_headers}
    url = base_url + endPoint
    response = requests.get(url, params=data, headers=headers)
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        data = HTTPStatus.INTERNAL_SERVER_ERROR.description
    else:
        try:
            data = json.loads(response.content)
        except Exception as ex:
            data = response.content
    return data


if __name__ == '__main__':
    # test - parse
    data = {}
    d = generatedProjectNameInputs(**data)

    results = get('livenessprobe', {})
    print('results', results)

    results = post('parse', data)
    print('results', results)

    results = post('predict', data)
    print('results', results)

    # test - test
    batch = []
    batch.append(d.dict())
    results = post('test', batch)
    print('results', results)
