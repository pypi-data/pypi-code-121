from builtins import input
from uuid import getnode as get_mac

import sys
import os
import webbrowser
import logging
import pkg_resources

from requests import ConnectionError

import p1
from p1.colors import *
from p1.utils import cprint, data2json, _assert
from p1.jsonfile import JsonFile

def main():
    try:
        sitename = sys.argv[2] if len(sys.argv) > 2 else '_DEFAULT'
        login(sitename)
    except Exception as e:
        cprint(LRED, "ops!")
        raise e


def login(sitename):
    """login in site"""

    # fetch site urls
    site = p1.get_site(sitename)
    _assert(site is not None, "Site %s not found in config.yaml" % sitename)

    # check site login style
    api_login_url = site.api_login_url()
    _assert(api_login_url, "Site %s has no login url" % site.name)

    # perform cli tools login; fetch auth and acces urls and login token
    p1_version = pkg_resources.get_distribution('p1ufcg').version
    response = site.post(api_login_url, {"mac": str(get_mac()), "p1_version": p1_version})
    response.encoding = 'utf-8'
    user_auth_url = response.json()['user-auth-url']
    api_access_url = response.json()['api-access-url']

    # open browser at authorization page
    cprint(YELLOW, user_auth_url)
    cprint(LCYAN, f"Abrir o browser para authorizar o login? (S/n) ", end="")
    if input() in "Ss":
        if webbrowser.open(user_auth_url):
            print(f"Aguardando autorização via browser…")
        else:
            cprint(LRED, "Ops! Não foi possível abrir o browser.")
            cprint(WHITE, "Visite o link acima para autorizar o login.")
    else:
        cprint(WHITE, "Visite o link acima para autorizar o login.")

    # request access code
    for i in range(10):
        response = site.get(f'{api_access_url}')
        if response.status_code == 500:
            cprint(LRED, "O login falhou (timeout)")
            cprint(LGREEN, "Tente novamente...")
            #sys.exit(1)
            continue
        authorization = response.json()
        if response.status_code == 200: break

    # check authorization
    if 'authorized' not in authorization:
        cprint(LRED, 'Login não autorizado')
        logging.info('Login não autorizado')
        sys.exit(1)

    # check whether the login worked
    if not 'tst_token' in authorization:
        cprint(LRED, 'O login falhou (não autorizado)')
        logging.info('tst_token não encontrado na resposta')
        return

    # save token
    tokens = JsonFile(os.path.expanduser('~/.p1/tokens.json'))
    tokens[site.name] = authorization['tst_token']
    tokens.writable = True
    tokens.save()

    msg = f"Você está logado no site de p1 como {YELLOW}{authorization['email']}{RESET}"
    cprint(LGREEN, msg)
    logging.info(msg)
