from typing import Callable

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_core_user.server.UserAdminAuthApiABC import UserAdminAuthApiABC
from peek_core_user.server.UserFieldHookApiABC import UserFieldHookApiABC
from peek_core_user.server.UserImportApiABC import UserImportApiABC
from peek_core_user.server.UserInfoApiABC import UserInfoApiABC
from peek_core_user.server.UserLoginApiABC import UserLoginApiABC
from peek_core_user.tuples.login.UserLoginResponseTuple import UserLoginResponseTuple
from peek_core_user.tuples.login.UserLogoutResponseTuple import UserLogoutResponseTuple

UserPostLoginHookCallable = Callable[[UserLoginResponseTuple], Deferred]

UserPostLogoutHookCallable = Callable[[UserLogoutResponseTuple], Deferred]


class UserApiABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def loginApi(self) -> UserLoginApiABC:
        """Login API

        Returns the API class that handles the user logins

        :return A reference to the UserLoginApiABC class
        """

    @property
    @abstractmethod
    def importApi(self) -> UserImportApiABC:
        """Import API

        Returns the API class that can be used to import the internal user/group objects

        :return A reference to the UserImportApiABC class
        """

    @property
    @abstractmethod
    def fieldHookApi(self) -> UserFieldHookApiABC:
        """Hook API

        Returns the API class that can be used to attach callbacks and observers to the
        login/logout process

        :return A reference to the UserFieldHookApiABC class
        """

    @property
    @abstractmethod
    def infoApi(self) -> UserInfoApiABC:
        """Info API

        Returns the API class that provides information about users

        :return A reference to the UserInfoApiABC class
        """

    @property
    @abstractmethod
    def adminAuth(self) -> UserAdminAuthApiABC:
        """Admin Auth API

        Returns the API class admin authentication for the peek-logic-service

        :return A reference to the UserAdminAuthApiABC class
        """
