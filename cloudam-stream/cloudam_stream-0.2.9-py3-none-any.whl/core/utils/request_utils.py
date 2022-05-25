import requests


def get(url):
    print("get request url:")
    print(url)
    resp = requests.get(url)
    return resp.text
