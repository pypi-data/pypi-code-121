class ApiConfig():
    '''Api Config
        
        Args:
            key (str): api keyword.
            uri (str): api uri.
            apiType (str): api Type, default value is "get".
            argsTemplete (str): api param format(Example "param1={0}&param2={1}"), default is "param1={0}".
            descrition (str): api descrition.
    '''
    def __init__(self, key:str, uri:str, apiType:str="get", argsTemplete:str="param1={0}", descrition:str=""):
        self._key=key
        self._uri=uri
        self._type=apiType
        self._argsTemplete=argsTemplete
        self._descrition=descrition

    @property
    def Key(self):
        return self._key

    @property
    def Uri(self):
        return self._uri

    @property
    def Type(self):
        return self._type

    @property
    def ArgsTemplete(self):
        return self._argsTemplete

    @property
    def Descrition(self):
        return self._descrition

class Config():
    '''SMS CONFIG
       
       Args:
            platforName (str): open api name.
            account (str): open api account.
            secret (str): open api secret.
            certificate (str): open api private certificate.
            version (str): open api version, default value is "1.0"

       Property:
            PlatformName (str): get the open api platform name.
            Account (str): get open api platform account.
            Secret (str): get open api platform secret.
            Certificate (str): (https) get open api plate form certificate.
            Apis (class<ApiList>): get apilist.
            Version (str): get open api version, default value is "1.0"
    '''
    
    def __init__(self,platformName:str, account:str, secret:str, certificate:str, version:str="1.0"):
        self._platformName=platformName
        self._account=account
        self._secret=secret
        self._certificate=certificate
        self._apiList=[]
        self._version=version

    def AddApi(self, apiConfig:ApiConfig):
        '''AddApi

            Args:
                apiConfig (Class<ApiConfig>):api config
        '''
        self._apiList.append(apiConfig)
    @property
    def Version(self):
        return self._version

    @property
    def PlatformName(self):
        return self._platformName
    
    @property
    def Account(self):
        return self._account

    @property
    def Secret(self):
        return self._secret

    @property
    def Certificate(self):
        return self._certificate

    @property
    def Apis(self):
        return self._apiList


