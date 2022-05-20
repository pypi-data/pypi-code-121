import boto3
import getpass
import hashlib
import os
import functools
import requests
from .config import Config

boto3.setup_default_session(region_name='us-east-1')

def email2username(email):
    return email.replace('@', '-at-')

def authentication_api(email, password):
    url = f"{Config.PORTAL_API_ENDPONT}/auth"
    resp = requests.get(url, auth=(email, password))
    access = resp.json()['data']
    Config.auth = access['auth']
    Config.user = access['user']
    Config.user['accessIdentityId'] = Config.user['identityId']
    Config.user['accessUserId'] = Config.user['userId']
    Config.user['accessEmail'] = Config.user['email']


def getSupportedUsers(email, password):
    url = f"{Config.PORTAL_API_ENDPONT}/auth"
    resp = requests.get(url, auth=(email, password))
    access = resp.json()['data']
    keys = access['user']
    supportedUsers = keys['guestUsers']
    return supportedUsers

def getEmailPasswdAuthKey():
    flow360dir = os.path.expanduser('~/.flow360')
    if os.getenv('FLOW360CLIENT_AUTHDIR'):
        flow360dir = os.getenv('FLOW360CLIENT_AUTHDIR')
    if os.path.exists('{0}/{1}'.format(flow360dir, 'email')) and \
            os.path.exists('{0}/{1}'.format(flow360dir, 'passwd')):
        with open(os.path.join(flow360dir, 'email'), 'r') as f:
            email = f.read()
        with open(os.path.join(flow360dir, 'passwd'), 'r') as f:
            password = f.read()
        try:
            authentication_api(email, password)
            return
        except:
            print('Error: Failed to log in with existing user:', email)
            print()
            pass
    while True:
        email = input('enter your email registered at flexcompute: ')
        password = getpass.getpass()
        salt = '5ac0e45f46654d70bda109477f10c299'
        password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        try:
            authentication_api(email, password)
            break
        except:
            print('Error: Failed to log in with new username and password.')
            print()
            pass
    while True:
        login = input('Do you want to keep logged in on this machine ([Y]es / [N]o) ')
        if login == 'Y' or login == 'y':
            os.makedirs(flow360dir, exist_ok=True)
            with open(os.path.join(flow360dir, 'passwd'), 'w') as f:
                f.write(password)
            with open(os.path.join(flow360dir, 'email'), 'w') as f:
                f.write(email)
            break
        elif login == 'N' or login == 'n':
            os.makedirs(flow360dir, exist_ok=True)
            break
        else:
            print('Unknown response: {0}\n'.format(login))


def refreshToken(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        return resp

    return wrapper



getEmailPasswdAuthKey()
