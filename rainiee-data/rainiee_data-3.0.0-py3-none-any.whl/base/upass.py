# -*- coding:utf-8 -*- 
import os

TOKEN_F_P = 'rainiee_data.token'
HOST_F_P = 'rainiee_data.host'


def set_token(token):
    user_home = os.path.expanduser('~')
    path = os.path.join(user_home, TOKEN_F_P)
    with open(path, 'w') as f:
        f.write(token)


def get_token():
    user_home = os.path.expanduser('~')
    path = os.path.join(user_home, TOKEN_F_P)
    with open(path, 'r') as f1:
        return f1.readline()

def get_host():
    user_home = os.path.expanduser('~')
    path = os.path.join(user_home, HOST_F_P)
    try:
        with open(path, 'r') as f1:
            host = f1.readline()
            if len(host) > 0 and (not host.isspace()):
                return host
    except:
        pass
    return 'http://data.rainiee.com'


