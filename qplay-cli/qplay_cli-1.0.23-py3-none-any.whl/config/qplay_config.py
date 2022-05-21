import configparser
from os.path import expanduser
import os

class QplayConfig:
    """Contains methods for writing and reading Quantplay config.
    """
    config_path = "{}/.quantplay".format(expanduser("~"))
    
    def __init__(self):
        pass
    
    @staticmethod
    def get_credentials():
        isExist = os.path.exists(QplayConfig.config_path)
        if not isExist:
            # Create a new directory because it does not exist 
            os.makedirs(QplayConfig.config_path)
        
        credentials = configparser.ConfigParser()
        credentials.read("{}/config".format(QplayConfig.config_path))
        
        return credentials
        
    @staticmethod
    def get_config():
        return QplayConfig.get_credentials()

    @staticmethod
    def save_credentials(access_token):
        credentials = QplayConfig.get_credentials()
        credentials['DEFAULT']['access_token'] = access_token
        with open('{}/config'.format(QplayConfig.config_path), 'w') as configfile:
            credentials.write(configfile)
            
    @staticmethod
    def save_config(key, value):
        credentials = QplayConfig.get_credentials()
        credentials['DEFAULT'][key] = value
        with open('{}/config'.format(QplayConfig.config_path), 'w') as configfile:
            credentials.write(configfile)
