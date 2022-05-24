# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import unittest
from os.path import expanduser
import os
import uuid
import shutil

from shapelets import init_session, Shapelets
from shapelets.services.login_service import LoginService
from shapelets.services.login_service_support import (
    _add_entry_to_login_file,
    _remove_entry_from_login_file
)

DIR_LOGIN_PATH = expanduser("~") + os.sep + ".shapelets"
LOGIN_FILE_PATH = DIR_LOGIN_PATH + os.sep + ".profile.json"


class LoginTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from shapelets.__main__ import start_all_command
        start_all_command()

    def test_register_user(self):
        username = str(uuid.uuid1().int)
        password = username
        login_service = LoginService("https://127.0.0.1")
        if login_service.check_username_is_available(username):
            login_service.register_user(username, password)
        self.assertFalse(login_service.check_username_is_available(username))

    def test_init_session(self):
        shapelets = init_session("admin", "admin", "https://localhost")
        self.assertTrue(isinstance(shapelets, Shapelets))

    def test_init_session_only_with_server(self):
        username = str(uuid.uuid1().int)
        password = username
        login_service = LoginService("https://localhost")
        if login_service.check_username_is_available(username):
            login_service.register_user(username, password)
        if not os.path.isdir(DIR_LOGIN_PATH):
            os.mkdir(DIR_LOGIN_PATH)
        else:
            if os.path.isfile(LOGIN_FILE_PATH):
                copy_file = f'{LOGIN_FILE_PATH}.copy'
                shutil.copyfile(LOGIN_FILE_PATH, copy_file)
                os.remove(LOGIN_FILE_PATH)
        _add_entry_to_login_file(
            DIR_LOGIN_PATH,
            LOGIN_FILE_PATH,
            "https://localhost",
            username,
            password,
            port=8443,
            default=True)
        shapelets = init_session(address="https://localhost")
        self.assertTrue(isinstance(shapelets, Shapelets))
        _remove_entry_from_login_file(LOGIN_FILE_PATH, "https://localhost", username)
        if copy_file:
            shutil.copyfile(copy_file, LOGIN_FILE_PATH)
            os.remove(copy_file)

    def test_init_session_only_without_server(self):
        username = str(uuid.uuid1().int)
        password = username
        login_service = LoginService("https://localhost")
        if login_service.check_username_is_available(username):
            login_service.register_user(username, password)
        if not os.path.isdir(DIR_LOGIN_PATH):
            os.mkdir(DIR_LOGIN_PATH)
        else:
            if os.path.isfile(LOGIN_FILE_PATH):
                copy_file = f'{LOGIN_FILE_PATH}.copy'
                shutil.copyfile(LOGIN_FILE_PATH, copy_file)
                os.remove(LOGIN_FILE_PATH)
        _add_entry_to_login_file(
            DIR_LOGIN_PATH,
            LOGIN_FILE_PATH,
            "https://localhost",
            username,
            password,
            port=8443,
            default=True)
        shapelets = init_session()
        self.assertTrue(isinstance(shapelets, Shapelets))
        _remove_entry_from_login_file(LOGIN_FILE_PATH, "https://localhost", username)
        if copy_file:
            shutil.copyfile(copy_file, LOGIN_FILE_PATH)
            os.remove(copy_file)
