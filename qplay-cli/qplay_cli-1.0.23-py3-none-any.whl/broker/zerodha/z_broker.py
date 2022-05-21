from qplay_cli.config.qplay_config import QplayConfig
from kiteconnect import KiteConnect
import traceback
import pickle
import codecs
from qplay_cli.broker.zerodha.kite_utils import KiteUtils

class ZBroker:
    """Commands for interacting with broker
    """
    zerodha_api_key = "zerodha_api_key"
    zerodha_api_secret = "zerodha_api_secret"
    
    def __init__(self):
        pass
    
    def configure(self):
        quantplay_config = QplayConfig.get_config()
        
        print("Enter Zerodha API key:")
        api_key = input()
        
        print("Enter Zerodha API Secret:")
        api_secret = input()
        
        quantplay_config['DEFAULT'][ZBroker.zerodha_api_key] = api_key
        quantplay_config['DEFAULT'][ZBroker.zerodha_api_secret] = api_secret
        
        
        with open('{}/config'.format(QplayConfig.config_path), 'w') as configfile:
            quantplay_config.write(configfile)
    
    def validate_config(self, quantplay_config):
        if quantplay_config is None:
            return False
        if ZBroker.zerodha_api_key not in quantplay_config['DEFAULT']:
            return False
        if ZBroker.zerodha_api_secret not in quantplay_config["DEFAULT"]:
            return False
            
        return True
            
    def generate_token(self):
        quantplay_config = QplayConfig.get_config()
        
        if not self.validate_config(quantplay_config):
            self.configure()
            quantplay_config = QplayConfig.get_config()

        api_key = quantplay_config['DEFAULT']['zerodha_api_key']
        api_secret = quantplay_config['DEFAULT']['zerodha_api_secret']
        kite = KiteConnect(api_key=api_key)
        
        request_token = None
        try:
            request_token = KiteUtils.get_request_token(kite_api_key=api_key)
        except Exception as e:
            traceback.print_exc()
            print("Need token input " + kite.login_url())
            raise e
            # request_token = input()
    
        print("request token {} api_secret {}".format(request_token, api_secret))
    
        data = kite.generate_session(request_token, api_secret=api_secret)
        kite.set_access_token(data["access_token"])
        
        
        QplayConfig.save_config("kite_object", codecs.encode(pickle.dumps(kite), "base64").decode())
        return kite