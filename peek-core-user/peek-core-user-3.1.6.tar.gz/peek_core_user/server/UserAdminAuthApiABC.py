from abc import ABCMeta, abstractmethod

from twisted.internet.defer import Deferred


class UserAdminAuthApiABC(metaclass=ABCMeta):
    @abstractmethod
    def check(self, username: str, password: str) -> Deferred:
        """check

        :param username
        :param password

        :returns callback for success, or errback for fail
        """
