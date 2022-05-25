
import configparser
from core import wmconstants
from core import logging_utils
import logging
from os import path
import json,re

loggr=None

if loggr == None:
    loggr = logging_utils.get_logger(__name__)

def parse_dbcfg(creds_path='~/.databrickscfg', profile='DEFAULT'):
    config = configparser.ConfigParser()
    abs_creds_path = path.expanduser(creds_path)
    (abs_creds_path)
    config.read(abs_creds_path)
    try:
        current_profile = dict(config[profile])
        return current_profile
    except KeyError:
        raise ValueError(
            'Unable to find credentials to load for profile. Profile only supports tokens.')

#parse args from json string
# '''{"profile": "", "url":"", "export_db": "logs", "is_azure":"False", "verify_ssl": "False", "verbosity":"debug", 
#     "clusterid":"0444-034f21-fayv7e2d","master_name_scope":"masterscp", 
#     "master_name_key":"user", "master_pwd_scope":"masterscp", "master_pwd_key":"pass"}'''
def parse_input_jsonargs(jsonargs, host, token):
    args =json.loads(jsonargs)
    args['url']=url_validation(host)
    args['token']=token
    args.update({'verbosity':getLogLevel(args['verbosity'])})
    args.update({'is_azure':getLogLevel(args['is_azure'])})
    args.update({'verify_ssl':getLogLevel(args['verify_ssl'])})
    # verify the proper url settings to configure this client
    if ('.com' in args['url']==False) or ('.net' in args['url']==False):
        loggr.info("Verify Hostname. Hostname should contain '.com' or '.net'")
    return args


def url_validation(url):
    if '/?o=' in url:
        # if the workspace_id exists, lets remove it from the URL
        url = re.sub("\/\?o=.*", '', url)
    elif 'net/' == url[-4:]:
        url = url[:-1]
    elif 'com/' == url[-4:]:
        url = url[:-1]
    return url.rstrip("/")



#DEBUG < INFO < WARNING < ERROR < CRITICAL
def getLogLevel(s):
    s=s.upper()
    if s == "DEBUG": return logging.DEBUG
    elif s == "INFO": return logging.INFO
    elif s == "WARNING": return logging.WARNING
    elif s == "ERROR": return logging.ERROR
    elif s == "CRITICAL": return logging.CRITICAL

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")



