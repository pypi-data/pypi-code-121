import requests


version: str = "v1.0"


def echo(s: str):
    res = requests.get("http://baidu.com")
    print(res.url)
    return version + " : " + s