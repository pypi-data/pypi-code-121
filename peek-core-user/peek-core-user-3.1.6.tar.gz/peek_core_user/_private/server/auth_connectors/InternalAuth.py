import logging
from typing import List

from peek_core_user._private.server.controller.PasswordUpdateController import (
    PasswordUpdateController,
)
from peek_core_user._private.storage.InternalGroupTuple import (
    InternalGroupTuple,
)
from peek_core_user._private.storage.InternalUserGroupTuple import (
    InternalUserGroupTuple,
)
from peek_core_user._private.storage.InternalUserPassword import (
    InternalUserPassword,
)
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.Setting import (
    globalSetting,
    ADMIN_LOGIN_GROUP,
    OFFICE_LOGIN_GROUP,
    MOBILE_LOGIN_GROUP,
)
from peek_core_user.server.UserDbErrors import UserPasswordNotSetException
from twisted.cred.error import LoginFailed

logger = logging.getLogger(__name__)


class InternalAuth:
    FOR_ADMIN = 1
    FOR_OFFICE = 2
    FOR_FIELD = 3

    def checkPassBlocking(
        self, dbSession, userName, password, forService: int
    ) -> List[str]:

        results = (
            dbSession.query(InternalUserPassword)
            .join(InternalUserTuple)
            .filter(InternalUserTuple.userKey == userName.lower())
            .all()
        )

        if not results or not results[0].password:
            raise UserPasswordNotSetException(userName)

        passObj = results[0]
        if passObj.password != PasswordUpdateController.hashPass(password):
            raise LoginFailed("Username or password is incorrect")

        groups = (
            dbSession.query(InternalGroupTuple)
            .join(InternalUserGroupTuple)
            .filter(InternalUserGroupTuple.userId == passObj.userId)
            .all()
        )

        groupNames = [g.groupName for g in groups]

        if forService == self.FOR_ADMIN:
            adminGroup = globalSetting(dbSession, ADMIN_LOGIN_GROUP)
            if adminGroup not in set(groupNames):
                raise LoginFailed("User is not apart of an authorised group")

        elif forService == self.FOR_OFFICE:
            officeGroup = globalSetting(dbSession, OFFICE_LOGIN_GROUP)
            if officeGroup not in set(groupNames):
                raise LoginFailed("User is not apart of an authorised group")

        elif forService == self.FOR_FIELD:
            fieldGroup = globalSetting(dbSession, MOBILE_LOGIN_GROUP)
            if fieldGroup not in set(groupNames):
                raise LoginFailed("User is not apart of an authorised group")

        else:
            raise Exception(
                "InternalAuth:Unhandled forService type %s" % forService
            )

        return groupNames
