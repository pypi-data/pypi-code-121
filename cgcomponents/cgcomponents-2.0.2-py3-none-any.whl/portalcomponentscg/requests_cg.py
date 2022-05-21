import json
import requests
from itertools import count
import const


def get_intranet(url):

    """
    :param url: Url do GET - Deve ser informada no .env
    :return: Informacoes do Intranet
    """

    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}

    return_inform = requests.get(url=url, headers=headers, verify=True)
    return_inform_format = json.loads(return_inform.text)

    return return_inform_format


def get_cg(url):

    """
    :param url: Url do GET - Deve ser informada no .env
    :return: Informacoes solicitadas
    """

    params = {
        'username': const.USERNAME_LOGIN,
        'password': const.PASSWORD_LOGIN
    }
    key = requests.post(const.URL_LOGIN, data=params)
    key_headers = json.loads(key.text)

    headers = {'Authorization': 'Token ' + key_headers['key']}
    return_inform = requests.get(url=url, headers=headers, verify=True)
    return_inform_format = json.loads(return_inform.text)

    return return_inform_format


def post_cg(url, json_i):

    """
    :param url: Url do Post - Deve ser informada no .env
    :return: Registra informacoes no Portal
    """

    params = {
        'username': const.USERNAME_LOGIN,
        'password': const.PASSWORD_LOGIN
    }
    key = requests.post(const.URL_LOGIN, data=params)
    key_headers = json.loads(key.text)
    headers = {'Authorization': 'Token ' + key_headers['key'],
               'Content-type': 'application/json',
               'Accept': 'application/json'}
    try:
        x = requests.post(url=url, data=json.dumps(json_i),
                             headers=headers, verify=True)

    except:
        pass


def delete_cg_generic(url, id, dict_inform):
    """
    :param url: Url do Delet - Deve ser informada no .env
    :return: Status code
    """

    params = {
        'username': const.USERNAME_LOGIN,
        'password': const.PASSWORD_LOGIN
    }
    key = requests.post(const.URL_LOGIN, data=params)
    key_headers = json.loads(key.text)

    headers = {'Authorization': 'Token ' + key_headers['key'],
               'Content-type': 'application/json',
               'Accept': 'application/json'
               }

    return_inform = requests.get(url=f'{url}{id}/', headers=headers, verify=True)
    return_inform_format = json.loads(return_inform.text)

    n = count(0)

    for i_return_portal in return_inform_format['colaborador']:
        num = next(n)
        if str(dict_inform['id']) == str(i_return_portal['id']):
            return_inform_format['colaborador'].pop(num)

    try:
        x = requests.patch(url=f'{const.URL_API_POST_FOLHA_DE_PAGAMENTOS}{return_inform_format["id"]}/',
                              data=json.dumps(return_inform_format),
                              headers=headers, verify=True)
    except:
        pass
