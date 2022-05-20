import requests
from flow360client.authentication import getEmailPasswdAuthKey
from .config import Config


class FileDoesNotExist(Exception):
    pass


def handle_response(func):
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        if resp.status_code == 401 and Config.auth_retry < 1:
            getEmailPasswdAuthKey()
            Config.auth_retry = Config.auth_retry + 1
            resp = func(*args, **kwargs)
        elif resp.status_code != 200:
            print(resp.content)
            resp.raise_for_status()
        try:
            Config.auth_retry = 0
            jsn = resp.json()['data']
        except Exception as e:
            print('Could not json decode response : {0}!'.format(resp.text))
            raise
        return jsn

    return wrapper


@handle_response
def portalApiGet(method, data=None):
    queryUrl = f"{Config.PORTAL_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360ACCESSUSER': Config.user['accessIdentityId']}
    return requests.get(queryUrl, headers=headers, json=data)


@handle_response
def flow360ApiPost(method, data=None):
    queryUrl = f"{Config.FLOW360_WEB_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360ACCESSUSER': Config.user['accessIdentityId']}
    return requests.post(queryUrl, headers=headers, json=data)


@handle_response
def flow360ApiPut(method, data):
    queryUrl = f"{Config.FLOW360_WEB_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360ACCESSUSER': Config.user['accessIdentityId']}
    return requests.put(queryUrl, headers=headers, json=data)


@handle_response
def flow360ApiGet(method):
    queryUrl = f"{Config.FLOW360_WEB_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360ACCESSUSER': Config.user['accessIdentityId']}
    return requests.get(queryUrl, headers=headers)

@handle_response
def flow360ApiDelete(method):
    queryUrl = f"{Config.FLOW360_WEB_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360ACCESSUSER': Config.user['accessIdentityId']}
    return requests.delete(queryUrl, headers=headers)
