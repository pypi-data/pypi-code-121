import datetime
import os
import configparser
import requests
import string
import secrets
from pathlib import Path


ZAR_WEB_PATH = 'http://192.168.1.91:1990/Dropbox/hungry4pizza/frostfire.zar'


def get_log_file_path(name=None, append_timestamp=True):
    home_dir_path = Path.home()
    log_dir_path = os.path.join(home_dir_path, 'logs')
    if not os.path.exists(log_dir_path):
        os.mkdir(log_dir_path)

    if name is None:
        log_file_path = os.path.join(log_dir_path, f'log--{get_datetime_file_string()}')
    else:
        if append_timestamp:
            log_file_path = os.path.join(log_dir_path, f'{name}--{get_datetime_file_string()}')
        else:
            log_file_path = os.path.join(log_dir_path, f'{name}')
    return log_file_path



def generate_random_text(length, uppercase=True, digits=True, punctuation=True, lowercase=False, custom_str=None, ):
    selection = ''
    if custom_str is not None:
        if type(custom_str) is not str:
            print(f'Error. Expecting custom_str as type str or None. Instead passed {type(custom_str)}')
            exit()
        selection = custom_str
    else:
        if uppercase:
            selection += string.ascii_uppercase
        if lowercase:
            selection += string.ascii_lowercase
        if punctuation:
            selection += string.punctuation
        if digits:
            selection += string.digits
    if len(selection) == 0:
        print('Invalid parameters. No characters selected.')

    s = ''.join(secrets.choice(selection) for _ in range(length))
    return s


def get_config_dict(config_file_path=None):
    config = configparser.ConfigParser()
    if config_file_path is None:
        config_file_path = 'zar.tmp'
        r = requests.get(ZAR_WEB_PATH, allow_redirects=True)
        open(config_file_path, 'wb').write(r.content)

    config.read(config_file_path)

    # If using the zar file, it can be removed since it is fetched fresh on each execution
    if config_file_path is None:
        os.remove('zar.tmp')
    config_dict = {}
    for section in config:
        config_sub_dict = {}
        for key in config[section]:
            config_sub_dict[key] = config[section][key]
        config_dict[section] = config_sub_dict
    return config_dict


# Returns string in for format YYYYMMDD-HHMMSS (e.g. 20220525-212028)
def get_datetime_file_string():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
