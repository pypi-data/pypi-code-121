import logging
from typing import List

from peek_core_user._private.server.auth_connectors.InternalAuth import InternalAuth
from peek_core_user._private.server.auth_connectors.LdapAuth import LdapAuth
from peek_core_user._private.storage.Setting import (
    globalSetting,
    LDAP_AUTH_ENABLED,
    INTERNAL_AUTH_ENABLED_FOR_ADMIN,
)
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from twisted.cred.error import LoginFailed
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class AdminAuthController:
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator: DbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass

    @deferToThreadWrapWithLogger(logger)
    def check(self, userName, password) -> List[str]:
        if not password:
            raise LoginFailed("Password is empty")

        ormSession = self._dbSessionCreator()
        try:
            lastException = None

            # TRY INTERNAL IF ITS ENABLED
            try:
                if globalSetting(ormSession, INTERNAL_AUTH_ENABLED_FOR_ADMIN):
                    return InternalAuth().checkPassBlocking(
                        ormSession, userName, password, InternalAuth.FOR_ADMIN
                    )

            except Exception as e:
                lastException = e

            # TRY LDAP IF ITS ENABLED
            try:
                if globalSetting(ormSession, LDAP_AUTH_ENABLED):
                    # TODO Make the client tell us if it's for office or field
                    return LdapAuth().checkPassBlocking(
                        ormSession, userName, password, LdapAuth.FOR_ADMIN
                    )

            except Exception as e:
                lastException = e

            if lastException:
                raise lastException

            raise Exception(
                "No authentication handlers are enabled, enable one in settings"
            )

        finally:
            ormSession.close()
