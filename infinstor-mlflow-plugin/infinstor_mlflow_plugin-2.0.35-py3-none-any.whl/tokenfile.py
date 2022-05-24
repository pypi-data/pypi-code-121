import requests
from requests.exceptions import HTTPError
import json
import time
import os
import logging
import posixpath

from . import get_log_level_from_config_json

logger = logging.getLogger(__name__)
loglevel_int:int = get_log_level_from_config_json(__name__)
if loglevel_int:
    logger.setLevel(loglevel_int)


def get_token_file_name():
    if 'INFINSTOR_TOKEN_FILE_DIR' in os.environ:
        return os.path.join(os.environ['INFINSTOR_TOKEN_FILE_DIR'], "token")
    else:
        return os.path.join(os.path.expanduser("~"), ".infinstor", "token")

def read_token_file(tokfile:str=None):
    """reads and returns the following from the tokenfile: access_token, refresh_token, token_time, client_id, service, token_type, id_token

    Args:
        tokfile ([str]): the token file to read

    Returns:
        [tuple]: returns the tuple access_token, refresh_token, token_time, client_id, service, token_type, id_token
    """
    if not tokfile: tokfile = get_token_file_name()

    fclient_id = None
    ftoken = None
    frefresh_token = None
    ftoken_time = None
    fservice = None
    token_type = None
    id_token = None
    with (open(tokfile)) as fp:
        for count, line in enumerate(fp):
            if (line.startswith('ClientId=')):
                fclient_id = line[len('ClientId='):].rstrip()
            if (line.startswith('Token=')):
                ftoken = line[len('Token='):].rstrip()
            if (line.startswith('RefreshToken=')):
                frefresh_token = line[len('RefreshToken='):].rstrip()
            if (line.startswith('TokenTimeEpochSeconds=')):
                ftoken_time = int(line[len('TokenTimeEpochSeconds='):].rstrip())
            if (line.startswith('Service=')):
                fservice = line[len('Service='):].rstrip()
            if (line.startswith('TokenType=')):
                token_type = line[len('TokenType='):].rstrip()
            if (line.strip().lower().startswith('idtoken=')):
                # read the content after '='
                id_token = line.split('=')[1].strip()
    if (token_type == None):
        if (ftoken != None and ftoken.startswith('Custom ')):
            token_type = 'Custom'
        else:
            token_type = 'Bearer'
    return ftoken, frefresh_token, ftoken_time, fclient_id, fservice, token_type, id_token

def write_token_file(tokfile, token_time, token, refresh_token, client_id, service, idToken:str):
    os.makedirs(os.path.dirname(tokfile), exist_ok=True)
    with open(tokfile, 'w') as wfile:
        wfile.write("Token=" + token + "\n")
        wfile.write("RefreshToken=" + refresh_token + "\n")
        wfile.write("ClientId=" + client_id + "\n")
        wfile.write("TokenTimeEpochSeconds=" + str(token_time) + "\n")
        wfile.write("Service=" + service + "\n")
        wfile.write("IdToken=" + idToken + "\n")
        wfile.close()

def renew_token(region, tokfile, refresh_token, client_id, service):
    payload = "{\n"
    payload += "    \"AuthParameters\" : {\n"
    payload += "        \"REFRESH_TOKEN\" : \"" + refresh_token + "\"\n"
    payload += "    },\n"
    payload += "    \"AuthFlow\" : \"REFRESH_TOKEN_AUTH\",\n"
    payload += "    \"ClientId\" : \"" + client_id + "\"\n"
    payload += "}\n"

    url = 'https://cognito-idp.' +region +'.amazonaws.com:443/'

    headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target' : 'AWSCognitoIdentityProviderService.InitiateAuth'
            }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        logger.info(f'HTTP error occurred while trying to renew token: {http_err}')
        raise
    except Exception as err:
        logger.info(f'Other error occurred while trying to renew token: {err}')
        raise
    else:
        authres = response.json()['AuthenticationResult']
        token = authres['AccessToken']
        idToken = authres['IdToken']        
        token_time = int(time.time())
        write_token_file(tokfile, token_time, token, refresh_token, client_id, service, idToken)

def get_id_token(region):
    """returns the idToken if available.. Also may return a custom token

    Returns:
        [tuple]: ( idToken or CustomToken, service )
    """
    # read the idToken
    ( access_token, refresh_token, token_time, client_id, service, token_type, id_token) = read_token_file()

    if (token_type == "Custom"):
        logger.debug("get_token(): Custom Infinstor token")
        return access_token, service
    
    time_now = int(time.time())
    # we have so many copies of tokenfile writing code in our codebase, there is a chance that not all copies write idToken.  handle this with 'if not id_token' below.
    if ((token_time + (30 * 60)) < time_now) or not id_token:
        logger.info(f'get_id_token(): InfinStor token has expired or id_token not found in tokenfile: Calling renew: id_token found in token file={id_token == None} token_time={token_time}; (token_time + (30 * 60)={token_time + (30 * 60)}; time_now={time_now}')
        renew_token(region, get_token_file_name(), refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file()
        
    return id_token, service

def get_token(region, tokfile, force_renew):
    token = None
    refresh_token = None
    token_time = None
    client_id = None
    service = None

    token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file(tokfile)

    if (token_type == "Custom"):
        logger.debug("get_token(): Custom Infinstor token")
        return token, service

    if (force_renew == True):
        logger.info("get_token(): Forcing renewal of infinstor token")
        renew_token(region, tokfile, refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file(tokfile)
        return token, service

    time_now = int(time.time())
    if ((token_time + (30 * 60)) < time_now):
        logger.debug(f'get_token(): InfinStor token has expired. Calling renew: token_time={token_time}; (token_time + (30 * 60)={(token_time + (30 * 60))}; time_now={time_now}')
        renew_token(region, tokfile, refresh_token, client_id, service)
        token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file(tokfile)
        return token, service
    else:
        logger.debug(f'get_token(): InfinStor token has not expired: token_time={token_time}; time_now={time_now}')
        return token, service
