# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest

from shapelets import Shapelets
from shapelets.services.login_service import LoginService


class PingTest(unittest.TestCase):

    def setUp(self):
        username = "admin2"
        password = "admin2password"
        login_service = LoginService("https://127.0.0.1")
        if login_service.check_username_is_available(username):
            login_service.register_user(username, password)
        else:
            login_service.login_user(username, password)
        self.client = Shapelets(login_service)

    def test_ping(self):
        ping = self.client.ping()
        self.assertEqual(True, ping)
