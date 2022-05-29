import requests
import urllib3
urllib3.disable_warnings()


def get_info():
    """请求信息"""
    data = requests.get("https://www.baidu.com/", verify=False)
    print(data.status_code)
    return data.content
