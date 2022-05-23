import abc


class CurlInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, "setopt_userpwd")
                and callable(subclass.setopt_userpwd)
                and hasattr(subclass, "setopt_cookiejar")
                and callable(subclass.setopt_cookiejar)
                and hasattr(subclass, "setopt_cookiefile")
                and callable(subclass.setopt_cookiefile)
                and hasattr(subclass, "setopt_connecttimeout")
                and callable(subclass.setopt_connecttimeout)
                and hasattr(subclass, "setopt_timeout")
                and callable(subclass.setopt_timeout)
                and hasattr(subclass, "get")
                and callable(subclass.get)
                and hasattr(subclass, "post")
                and callable(subclass.post)
                or NotImplementedError)

    @abc.abstractmethod
    def setopt_userpwd(self, user: str, password: str) -> None:
        """sets user and password to connect with"""
        raise NotImplementedError

    @abc.abstractmethod
    def setopt_cookiejar(self, cookie_file: str) -> None:
        """sets the path to file for cookie jar"""
        raise NotImplementedError

    @abc.abstractmethod
    def setopt_cookiefile(self, cookie_file: str) -> None:
        """sets the path to cookie file"""
        raise NotImplementedError

    @abc.abstractmethod
    def setopt_connecttimeout(self, connect_timeout: int) -> None:
        """sets the connection timeout in seconds"""
        raise NotImplementedError

    @abc.abstractmethod
    def setopt_timeout(self, timeout: int) -> None:
        """sets the timeout (connection + data exchange) in seconds"""
        raise NotImplementedError

    @abc.abstractmethod
    def get(self):
        raise NotImplementedError

    @abc.abstractmethod
    def post(self):
        raise NotImplementedError
