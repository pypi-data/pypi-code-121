import logging

from twisted.internet.defer import Deferred

from peek_core_user._private.server.controller.AdminAuthController import (
    AdminAuthController,
)
from peek_core_user.server.UserAdminAuthApiABC import UserAdminAuthApiABC

logger = logging.getLogger(__name__)


class UserAdminAuthApi(UserAdminAuthApiABC):
    def __init__(self, adminAuthController: AdminAuthController):
        self._adminAuthController = adminAuthController

    def shutdown(self):
        pass

    def check(self, username: str, password: str) -> Deferred:
        return self._adminAuthController.check(username, password)
