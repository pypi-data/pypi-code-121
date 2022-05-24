
from abc import ABCMeta, abstractmethod

from cryptotoolbox.bifrost.models.auth import PasswordCredentials, ClientCredentials
from cryptotoolbox.napoleon_config_tools import getter, config


class AbsctractRessource(metaclass=ABCMeta):

    @abstractmethod
    def get_credentials(self):
        raise NotImplemented

    @property
    @abstractmethod
    def _id(self):
        raise NotImplemented

    @property
    @abstractmethod
    def _secret(self):
        raise NotImplemented

    @property
    @abstractmethod
    def _type(self):
        raise NotImplemented

    @property
    @abstractmethod
    def _user(self):
        raise NotImplemented

    @property
    @abstractmethod
    def _password(self):
        raise NotImplemented


class RessourceTemplate(AbsctractRessource):

    def get_credentials(self):
        pass

    @property
    def _id(self):
        pass

    @property
    @abstractmethod
    def _secret(self):
        pass

    @property
    @abstractmethod
    def _type(self):
        pass

    @property
    @abstractmethod
    def _user(self):
        pass

    @property
    @abstractmethod
    def _password(self):
        pass


@config
class Service(AbsctractRessource):
    def __init__(self):
        self.__credentials = PasswordCredentials()
        self.__id = None
        self.__secret = None
        self.__type = None
        self.__user = None
        self.__password = None

    @property
    def _id(self):
        return self.id

    @property
    def _secret(self):
        return self.__secret

    @property
    def _type(self):
        return self.__type

    @property
    def _user(self):
        return self.__user

    @property
    def _password(self):
        return self.__password

    def get_credentials(self):
        return PasswordCredentials(self._id, self._secret,self._user,self._password)


@config
class Provider(AbsctractRessource):
    def __init__(self):
        self.__credentials = None
        self.__id = None
        self.__secret = None
        self.__type = None

    @property
    def _type(self):
        return self.__type

    @property
    def _id(self):
        return self.__id

    @property
    def _secret(self):
        return self.__secret

    @property
    def _user(self):
        return None

    @property
    def _password(self):
        return None

    def get_credentials(self):
        return ClientCredentials(self._id, self._type)


class Bitmex(Provider):

    @property
    @getter("providers.bitmex.id")
    def _id(self):
        return self._id

    @property
    @getter("providers.bitmex.secret")
    def _secret(self):
        return self._secret

    @property
    @getter("providers.bitmex.type")
    def _type(self):
        return self._type

    def get_credentials(self):
        return super(Bitmex, self).get_credentials()


class Dropbox(Provider):

    @property
    @getter("providers.dropbox.id")
    def _id(self):
        return self.id

    @property
    @getter("providers.dropbox.secret")
    def _secret(self):
        return self.secret

    @property
    @getter("providers.dropbox.type")
    def _type(self):
        return self.type


class Binance(Provider):

    @property
    @getter("providers.binance.id")
    def _id(self):
        return self._id

    @property
    @getter("providers.binance.secret")
    def _secret(self):
        return self._secret

    @property
    @getter("providers.binance.type")
    def _type(self):
        return self._type


class CryptoCompare(Provider):

    @property
    @getter("providers.cryptocompare.id")
    def _id(self):
        return self.id

    @property
    @getter("providers.cryptocompare.secret")
    def _secret(self):
        return self.secret

    @property
    @getter("providers.cryptocompare.type")
    def _type(self):
        return self.type


class NapoleonService(Service):

    @property
    @getter("providers.napoleon_service.id")
    def _id(self):
        return self.id

    @property
    @getter("providers.napoleon_service.secret")
    def _secret(self):
        return self.secret

    @property
    @getter("providers.napoleon_service.type")
    def _type(self):
        return self.type

    @property
    @getter("providers.napoleon_service.user")
    def _user(self):
        return self.user

    @property
    @getter("providers.napoleon_service.password")
    def _password(self):
        return self.password

    @property
    def credentials(self):
        return super(NapoleonService, self).get_credentials()


class Ressources(object):
    def __init__(self):
        self.__bitmex = Bitmex
        self.__binance = Binance
        self.__dropbox = Dropbox
        self.__cryptocompare = CryptoCompare
        self.__napoleon_service = NapoleonService

    @property
    def bitmex(self):
        return self.__bitmex

    @property
    def binance(self):
        return self.__binance

    @property
    def cryptocompare(self):
        return self.__cryptocompare

    @property
    def dropbox(self):
        return self.__dropbox

    @property
    def napoleon_service(self):
        return self.__napoleon_service


if __name__ == '__main__':
    s = Bitmex().get_credentials()
    credentials = NapoleonService().get_credentials()
    end = True
