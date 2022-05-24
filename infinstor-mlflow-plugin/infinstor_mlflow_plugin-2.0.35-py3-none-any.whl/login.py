#!/usr/bin/env python
import sys
import getpass
import json
import builtins
from typing import Dict
from . import servicedefs ,set_builtins_with_serverside_config   # do not remove 'servicedefs', although it is unreferenced; needed to setup some 'builtins' attributes
from infinstor_mlflow_plugin.tokenfile import write_token_file, get_token_file_name
from requests.exceptions import HTTPError
import requests
from os.path import expanduser
from os.path import sep as separator
import time
import configparser
from urllib.parse import unquote, urlparse
import os
import traceback
import logging
import urllib.parse

from . import get_log_level_from_config_json
logger = logging.getLogger(__name__)
loglevel_int:int = get_log_level_from_config_json(__name__)
if loglevel_int:
    logger.setLevel(loglevel_int)

def print_version(token):
    """print the output of /api/2.0/mlflow/infinstor/get_version

    Args:
        token ([type]): [description]
    """
    headers = { 'Authorization': token }
    url = 'https://' + builtins.mlflowserver + '/api/2.0/mlflow/infinstor/get_version'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred while getting version: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred while getting version: {err}')
        raise

def get_creds():
    if sys.stdin.isatty():
        username = input("Username: ")
        password = getpass.getpass("Password: ")
    else:
        username = sys.stdin.readline().rstrip()
        password = sys.stdin.readline().rstrip()
    return username, password

def get_customer_info_rest(idToken:str) -> dict:
    """Invokes api.<infinstor.com>/customerinfo API and returns the dict

    Args:
        idToken (str): idToken to use for authentication

    Returns:
        dict: the response from /customerinfo call
        {'awsAccountId': 'xxx', 'enableProjects': 'true', 'InfinSnapBuckets': [], 'InfinStorAccessKeyId': 'xxxx', 'userName': 'xxxxx@infinstor.com', 'serviceVersion': '2.0.18', 'productCode': ['xxxx'], 'iamExternalId': 'xxx', 'customerId': 'xxxxx', 'customerArtifactUri': 'xxxxx', 'customerRoleArn': 'xxxxx', 'mlflowTrackingDdbTableName': 'xxxxxx', 'isSecondaryUser': 'true'}
    """
    payload = ("ProductCode=" + builtins.prodcode)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': idToken
        }

    url = 'https://' + builtins.apiserver + '/customerinfo'
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise

    # print('customerinfo success')
    logger.debug(f"url={url}; response.content={response.content}")
    try:
        response_json:dict = response.json()
    except Exception as e:
        # if authentication fails, see this as the response instead of valid json: response.content=b'<html><head><meta http-equiv="refresh" content="0; URL=\'https://service.isstage13.isstage2.com/login.html\'"/></head><body>Login expired. Please login again</body></html>'
        raise Exception(f"Authentication failed for {url}.  Please check your token and try again.." ) from e
    
    return response_json
    
def login_and_update_token_file(region, username, password) -> dict:
    """ does AuthFlow = "USER_PASSWORD_AUTH" or grant_type = 'authorization_code' (oauth)
    
    does AuthFlow = "REFRESH_TOKEN_AUTH"
    
    then updates token file at ~/.infinstor/token or at location
    specified by environment var INFINSTOR_TOKEN_FILE

    Args:
        region (str): AWS region where cognito is deployed
        username (str): see above description
        password (str): see above description
        srvdict (dict): dictionary that describes the service; returned by api/2.0/mflow/infinstor/get_version; 
    Returns:
        [dict]: returns /customerinfo REST call results
    """
    if ( not builtins.isexternalauth ):
        logger.debug(f"login_and_update_token_file(): login using AuthFlow=USER_PASSWORD_AUTH flow (cognito API)")
        postdata = dict()
        auth_parameters = dict()
        auth_parameters['USERNAME'] = username
        auth_parameters['PASSWORD'] = password
        postdata['AuthParameters'] = auth_parameters
        postdata['AuthFlow'] = "USER_PASSWORD_AUTH"
        postdata['ClientId'] = builtins.clientid

        payload = json.dumps(postdata)

        url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'
        headers = {
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
                }

        try:
            response:requests.Response = requests.post(url, data=payload, headers=headers)
            logger.debug(f"login_and_update_token_file(): response headers for cognito AuthFlow = USER_PASSWORD_AUTH for url={url} = {response.headers}")
            logger.debug(f"login_and_update_token_file(): response for cognito AuthFlow = USER_PASSWORD_AUTH url={url} = {response.content}")
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        
        authres = response.json()['AuthenticationResult']
        idToken = authres['IdToken']
        accessToken = authres['AccessToken']
        refresh_token = authres['RefreshToken']
        
        ##Refresh token once############################
        postdata = dict()
        auth_parameters = dict()
        auth_parameters['REFRESH_TOKEN'] = refresh_token
        postdata['AuthParameters'] = auth_parameters
        postdata['AuthFlow'] = "REFRESH_TOKEN_AUTH"
        postdata['ClientId'] = builtins.clientid

        payload = json.dumps(postdata)

        url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'
        headers = {
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
                }

        try:
            response = requests.post(url, data=payload, headers=headers)
            logger.debug(f"login_and_update_token_file(): response headers for cognito AuthFlow = REFRESH_TOKEN_AUTH for url={url} = {response.headers}")
            logger.debug(f"login_and_update_token_file(): response for cognito AuthFlow = REFRESH_TOKEN_AUTH url={url} = {response.content}")
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

        authres = response.json()['AuthenticationResult']
        idToken = authres['IdToken']
        accessToken = authres['AccessToken']
        #########

    else:  # this is the external auth flow..
        logger.debug(f"login_and_update_token_file(): login using grant_type=authorization_code flow (cognito API)")
        serviceserver:str = builtins.serviceserver
        # "https%3A%2F%2Fservice11.ai.isstage1.com%2Fologin.html"
        # https://api13.isstage13.isstage2.com/customerinfo
        redirect_uri:str = f"https://{builtins.mlflowserver}/api/2.0/mlflow/infinstor/cliclient_authorize"
        
        # create the cognito oauth2 URL based on the service dashboard url
        # example url for auth code=https://service11-ai-isstage1-com.auth.us-east-1.amazoncognito.com/oauth2/authorize?redirect_uri=https%3A%2F%2Fservice11.ai.isstage1.com%2Fologin.html&response_type=code&scope=openid&state=uxZCvnJk33cDTIoFhT2yxo846Rdj7Q&access_type=offline&prompt=select_account&client_id=6g8uhmgagq42ii3j6klfcmpru9
        # scope=openid%20email%20profile%20phone&
        oauth2_authorize_url:str = f"https://{serviceserver.replace('.','-')}.auth.{builtins.region}.amazoncognito.com/oauth2/authorize?redirect_uri={urllib.parse.quote_plus( redirect_uri)}&response_type=code&state=uxZCvnJk33cDTIoFhT2yxo846Rdj7Q&access_type=offline&prompt=select_account&client_id={builtins.clientid}"
        
        auth_code:str = input(f"Enter this URL in a browser and obtain a code: {oauth2_authorize_url}\n  Enter the obtained code here: ")
        
        # get the auth2 access token url based on the service dasshboard url
        oauth2_token_url = f"https://{serviceserver.replace('.','-')}.auth.{builtins.region}.amazoncognito.com/oauth2/token"
        # do not urlencode the redirect_uri using urllib.parse.quote_plus():  the post call automatically does this..
        response:requests.Response = requests.post(oauth2_token_url, data={"grant_type":"authorization_code", "client_id":builtins.clientid, "code":auth_code, 'redirect_uri': redirect_uri})
        logger.debug(f"login_and_update_token_file(): response headers for grant_type:authorization_code for url={oauth2_token_url} = {response.headers}")
        logger.debug(f"login_and_update_token_file(): response for grant_type:authorization_code for url={oauth2_token_url} = {response.content}")
        
        authres = response.json()
        idToken = authres['id_token']
        accessToken = authres['access_token']
        refresh_token = authres['refresh_token']
        
        # refresh the token.
        response:requests.Response = requests.post(oauth2_token_url, data={"grant_type":"refresh_token", "client_id":builtins.clientid, "refresh_token":refresh_token})
        logger.debug(f"login_and_update_token_file(): response headers for oauth2 grant_type:refresh_token for url={oauth2_token_url} = {response.headers}")
        logger.debug(f"login_and_update_token_file(): response for oauth2 grant_type:refresh_token for url={oauth2_token_url} = {response.content}")
        accessToken = authres['access_token']
        refresh_token = authres['refresh_token']
        
    token_time = int(time.time())
    tokfile = get_token_file_name()
    write_token_file(tokfile, token_time, accessToken, refresh_token, builtins.clientid,\
                builtins.service, idToken)

    response_json:dict = get_customer_info_rest(idToken)
    
    infinStorAccessKeyId = unquote(response_json.get('InfinStorAccessKeyId'))
    infinStorSecretAccessKey = unquote(response_json.get('InfinStorSecretAccessKey'))
    setup_credentials(infinStorAccessKeyId, infinStorSecretAccessKey)

    logger.info('login_and_update_token_file(): Login to service ' + builtins.service + ' complete')
    print_version(accessToken)
    return response_json

def setup_credentials(infinStorAccessKeyId, infinStorSecretAccessKey):
    home = expanduser("~")
    config = configparser.ConfigParser()
    newconfig = configparser.ConfigParser()
    credsfile = home + separator + ".aws" + separator + "credentials"
    if (os.path.exists(credsfile)):
        credsfile_save = home + separator + ".aws" + separator + "credentials.save"
        try:
            os.remove(credsfile_save)
        except Exception as err:
            print()
        try:
            os.rename(credsfile, credsfile_save)
        except Exception as err:
            print()
        config.read(credsfile_save)
        for section in config.sections():
            if (section != 'infinstor'):
                newconfig[section] = {}
                dct = dict(config[section])
                for key in dct:
                    newconfig[section][key] = dct[key]
    else:
        dotaws = home + "/.aws"
        if (os.path.exists(dotaws) == False):
            os.mkdir(dotaws, 0o755)
            open(credsfile, 'a').close()

    newconfig['infinstor'] = {}
    newconfig['infinstor']['aws_access_key_id'] = infinStorAccessKeyId
    newconfig['infinstor']['aws_secret_access_key'] = infinStorSecretAccessKey

    with open(credsfile, 'w') as configfile:
        newconfig.write(configfile)

# returns dict of service details if successful, None if unsuccessful
def bootstrap_from_mlflow_rest() -> Dict[str,str]:
    """ use the MLFLOW_TRACKING_URI environment variable to bootstrap: call get_version() REST API and use it to return a dict with the configuration detected like 'clientid', 'appclientid', 'service', 'region' and others..

    Returns:
        [dict]: see description above
    """
    
    ##########
    #  TODO: a copy exists in 
    #  infinstor-mlflow/plugin/infinstor_mlflow_plugin/login.py 
    #  infinstor-mlflow/processors/singlevm/scripts/rclocal.py
    #  infinstor-jupyterlab/server-extension/jupyterlab_infinstor/__init__.py
    #  infinstor-jupyterlab/server-extension/jupyterlab_infinstor/cognito_utils.py
    #  infinstor-jupyterlab/clientlib/infinstor/bootstrap.py
    #  infinstor-jupyterlab/infinstor_py_bootstrap_project/infinstor_py_bootstrap/infinstor_py_bootstrap.py
    #  Need to see how to share code between two pypi packages to eliminate this duplication
    #  when refactoring this code, also refactor the copies
    ############
    
    muri = os.getenv('MLFLOW_TRACKING_URI')
    pmuri = urlparse(muri)
    if (pmuri.scheme.lower() != 'infinstor'):
        raise Exception("Error: MLFLOW_TRACKING_URI must be set to infinstor://.... to bootstrap infinstor mlflow client.  Please check documentation for details.")
    # extract 'infinstor.com' from 'mlflow.infinstor.com'
    cognito_domain = pmuri.hostname[pmuri.hostname.index('.')+1:]
    url = 'https://' + pmuri.hostname + '/api/2.0/mlflow/infinstor/get_version'
    headers = { 'Authorization': 'None' }
    try:
        response = requests.get(url, headers=headers)
        logger.debug(f"response headers from url={url}: {response.headers}")
        logger.debug(f"response from url={url}: {response.content}")
        response.raise_for_status()
        resp = response.json()
        serv_dict:Dict[str,str] = { 'clientid' : resp['cognitoCliClientId'],
                'appclientid' : resp['cognitoAppClientId'],
                'mlflowserver' : resp['mlflowDnsName'] + '.' + cognito_domain,
                'mlflowuiserver' : resp['mlflowuiDnsName'] + '.' + cognito_domain,
                'mlflowstaticserver' : resp['mlflowstaticDnsName'] + '.' + cognito_domain,
                'apiserver' : resp['apiDnsName'] + '.' + cognito_domain,
                'serviceserver' : resp['serviceDnsName'] + '.' + cognito_domain,
                'service' : cognito_domain,
                'region': resp['region'],
                # handle the case where server is a old version that doesn't set this.. server returns the string 'true' or 'false' and not boolean True or False
                'isexternalauth': resp.get('isExternalAuth', False) }
        logger.debug(f"Service details from url={url}: {serv_dict}")
        return serv_dict
    except HTTPError as http_err:
        logger.error(f"Caught Exception: {http_err}: {traceback.format_exc()}" )
        return None
    except Exception as err:
        logger.error(f"Caught Exception: {err}: {traceback.format_exc()}" )
        return None

def _login(srvdct, username:str=None, password:str=None):
    """ performs a login into the service.  Also sets the builtins based on values of 'srvdct'
    Args:
        srvdct [dict]: service dictionary which describes the service

    """
    set_builtins_with_serverside_config(srvdct)
    
    try:
        tokfile = get_token_file_name()
        token, service = get_token(srvdct['region'], tokfile, False)
        if (service == builtins.service):
            print('Login to service ' + service + ' completed')
            return
        else:
            print('service mismatch between MLFLOW_TRACKING_URI and {}. Forcing login'.format(tokfile))
            raise Exception('service mismatch between MLFLOW_TRACKING_URI and {}. Forcing login'.format(tokfile))
    except Exception as err:
        logger.debug('caught exception ' + str(err))
        pass

    if not username or not password:
        if not builtins.isexternalauth:
            username, password = get_creds()

    customerinfo:dict = login_and_update_token_file(srvdct['region'], username, password)

    # set enableProjects / isProjectEnabled ; /customer_info REST response has 'enableProjects': 'true'        
    builtins.enableProjects = True if customerinfo.get('enableProjects', False) == 'true' else False
    srvdct['enableProjects'] = builtins.enableProjects
    logger.debug(f"enableProjects={builtins.enableProjects}")

def login():
    if (_login(bootstrap_from_mlflow_rest())):
        return 0
    else:
        return 255

def get_python_creds():
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    return username, password

def new_login():
    uname, passwd = get_python_creds()
    _login(bootstrap_from_mlflow_rest(), uname, passwd)

if __name__ == "__main__":
    exit(login())
