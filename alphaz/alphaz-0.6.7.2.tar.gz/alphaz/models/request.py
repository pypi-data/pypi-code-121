import requests
from alphaz.models.config import AlphaConfig
from alphaz.models.logger import AlphaLogger

from core import core
LOG = core.get_logger('http')

class AlphaRequest():
    config: AlphaConfig = None
    host = None

    def __init__(self,config: AlphaConfig,log=None,logger_root=None):
        self.config = config
        self.host   = self.config.get('host')

        self.log    = log or LOG

        super().__init__()

    def get_url(self,route):
        if route[0] != '/':
            route = '/' + route
        ssl = self.config.get('ssl')
        prefix = 'https://'
        if ssl is None or not ssl:
            prefix = 'http://'
        return prefix + self.host + route

    def post(self,route,data={}):
        try:
            response    = requests.post(self.get_url(route), data=data, verify=False)
            return str(response.text)
        except Exception as ex:
            if self.log: self.log.error(ex)
            return None

    def get(self,route,data={}):
        try:
            response    = requests.get(self.get_url(route), params=data, verify=False)
            return str(response.text)
        except Exception as ex:
            if self.log: self.log.error(ex)
            return None