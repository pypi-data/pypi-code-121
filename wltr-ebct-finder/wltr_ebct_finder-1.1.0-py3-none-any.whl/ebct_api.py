import requests


def find_data(data):
    response = requests.get('http://www.viacep.com.br/ws/%s/json' % data)

    if response.status_code == 200:
        return response.json()

    else:
        return response
