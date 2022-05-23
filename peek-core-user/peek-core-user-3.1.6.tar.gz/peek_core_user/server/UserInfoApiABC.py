from abc import ABCMeta
from abc import abstractmethod
from typing import List
from typing import Optional

from peek_core_user.tuples.UserDetailTuple import UserDetailTuple
from twisted.internet.defer import Deferred


class UserInfoApiABC(metaclass=ABCMeta):
    @abstractmethod
    def user(self, userName: str) -> Deferred:
        """Users

        :param userName: The userName of the user to retrieve

        :return: A Deferred, firing with Optional[UserDetailTuple]
        """

    @abstractmethod
    def userBlocking(
        self, userName: str, ormSession=None
    ) -> Optional[UserDetailTuple]:
        """User Details for User ID

        Return an instance of c{UserDetailTuple} for the userName provided.
        :param userName: The username to retrive the details for
        :param ormSession: Specify the ormSession to use, otherwise it may close the
                            current session.

        :return UserDetailTuple
        """

    @abstractmethod
    def userByUserKeyBlocking(
        self, userKey: str, ormSession=None
    ) -> Optional[UserDetailTuple]:
        """User Details for User key

        Return an instance of c{UserDetailTuple} for the userName provided.
        :param userKey: The userkey to retrive the details for
        :param ormSession: Specify the ormSession to use, otherwise it may close the
                            current session.

        :return UserDetailTuple
        """

    @abstractmethod
    def users(
        self,
        likeTitle: Optional[str] = None,
        groupNames: Optional[List[str]] = None,
        isFieldLogin: Optional[bool] = None,
    ) -> Deferred:
        """Users

        :param likeTitle: An optional string to look for in the title of the users
        :param groupNames: An optional list of group names to include users for.

        :return: A Deferred, callbacking with a List[UserDetailTuple]
        """

    @abstractmethod
    def groups(self, likeTitle: Optional[str] = None) -> Deferred:
        """Groups

        :param likeTitle: An optional string to look for in the title of the groups

        :return: A Deferred, callbacking with a List[GroupDetailTuple]
        """

    @abstractmethod
    def peekDeviceTokensForUser(self, userName: str) -> Deferred:  # List[str]:
        """Peek Device Tokens for Logged in User

        Return all the peek device tokens for devices this user is logged in to.

        :return A list of Peek Device Tokens
        """

    @abstractmethod
    def peekUserForDeviceToken(
        self, deviceToken
    ) -> Deferred:  # Optional[UserDetailTuple]:
        """Peek User for Device Token

        Return a user detail tuple for a user logged into a device with deviceToken

        :return UserDetail or None
        """

    @abstractmethod
    def peekTokensWithUserDetails(
        self, isFieldDevice: bool
    ) -> Deferred:  # List[FieldDeviceWithUserDetailsTuple]
        """Peek logged-in field device tokens with or without logged-in user
        details

        :return: A list of Peek Device Tokens logged in or not logged in on
        Field app with user details tuples
        """

    @abstractmethod
    def peekLoggedInDeviceTokens(self, isFieldDevice: bool) -> Deferred:
        # List[
        # str]
        """Peek field device tokens with logged-in status

        :return: A list of string of device tokens
        """

    @abstractmethod
    def userLoggedInInfo(self, userName: str, isFieldDevice: bool) -> Deferred:
        """Peek logged-in field device info by userName

        :param userName: The username / userid of the user, EG C917
        :return: A list of user LoggedIn Info
        """
