# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

"""
Tests for Login File
"""

import unittest
from unittest import mock
from os.path import expanduser
import os
import json
import atexit

from shapelets.services.login_service_support import (
    _add_default_user,
    _add_entry_to_login_file,
    _read_user_from_login_file,
    _create_login_directory,
    _remove_entry_from_login_file,
    _update_user_password
)

DIR_LOGIN_PATH = expanduser("~") + os.sep + ".testFolder"
LOGIN_FILE_PATH = DIR_LOGIN_PATH + os.sep + ".testProfile.json"


class LoginUnitTest(unittest.TestCase):
    """
    Unit Tests for Login File
    """

    def setUp(self) -> None:
        """
        Creates the directory and login file for the tests
        """
        self.dir_login_path = expanduser("~") + os.sep + ".testFolder"
        self.login_file_path = self.dir_login_path + os.sep + ".testProfile.json"

    def test_add_new_user(self):
        """
        Adds new user to login file using only server, user and password
        """
        new_entry = {
            "server": "LocalHost1",
            "user": "User1",
            "password": "Password1",
            "port": None,
            "default": None
        }
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1")
        with open(self.login_file_path, 'r') as file:
            file_data = json.load(file)
        self.assertDictEqual(file_data[0], new_entry)
        clean_up()

    def test_add_new_user_with_port(self):
        """
        Adds new user to login file using server, user, password and port
        """
        new_entry = {
            "server": "LocalHost1",
            "user": "User1",
            "password": "Password1",
            "port": 1234,
            "default": None
        }
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1", 1234)
        with open(self.login_file_path, 'r') as file:
            file_data = json.load(file)
        self.assertDictEqual(file_data[0], new_entry)
        clean_up()

    def test_add_new_user_default(self):
        """
        Adds new default user to login file
        """
        new_entry = {
            "server": "LocalHost1",
            "user": "User1",
            "password": "Password1",
            "port": 1234,
            "default": True
        }
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1", 1234,
                                 True)
        with open(self.login_file_path, 'r') as file:
            file_data = json.load(file)
        self.assertDictEqual(file_data[0], new_entry)
        clean_up()

    def test_create_login_directory(self):
        """
        Creates login directory
        """
        _create_login_directory(self.dir_login_path)
        self.assertTrue(os.path.exists(DIR_LOGIN_PATH))
        clean_up()

    def test_remove_entry_from_login_file(self):
        """
        Removes user form login file
        """
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1", 1234)
        self.assertTrue(_remove_entry_from_login_file(self.login_file_path, "LocalHost1", "User1"))
        clean_up()

    def test_read_user_from_login_file(self):
        """
        Reads user from login file
        """
        new_entry = {
            "server": "LocalHost1",
            "user": "User1",
            "password": "Password1",
            "port": 1234,
            "default": None
        }
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1", 1234)
        user_info = _read_user_from_login_file(self.dir_login_path, self.login_file_path,
                                               "LocalHost1", "User1")
        self.assertDictEqual(user_info, new_entry)
        clean_up()

    def test_read_default_user_from_login_file_with_address(self):
        """
        Reads default user from login file
        """
        new_entry = {
            "server": "LocalHost1",
            "user": "User1",
            "password": "Password1",
            "port": 1234,
            "default": True
        }
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1", 1234, True)
        user_info = _read_user_from_login_file(self.dir_login_path, self.login_file_path,
                                               "LocalHost1")
        self.assertDictEqual(user_info, new_entry)
        clean_up()

    def test_update_password(self):
        """
        Updates password for user
        """
        new_entry = {
            "server": "LocalHost1",
            "user": "User1",
            "password": "NewPassword",
            "port": 1234,
            "default": None
        }
        _add_entry_to_login_file(self.dir_login_path,
                                 self.login_file_path,
                                 "LocalHost1",
                                 "User1",
                                 "OldPassword",
                                 1234,
                                 None)
        self.assertTrue(_update_user_password(self.dir_login_path,
                                              self.login_file_path,
                                              "LocalHost1",
                                              "User1",
                                              "OldPassword",
                                              "NewPassword"))
        with open(self.login_file_path, 'r') as file:
            file_data = json.load(file)
        self.assertDictEqual(file_data[0], new_entry)
        clean_up()


@mock.patch('shapelets.services.login_service_support._get_input')
class LoginUnitTestWithMock(unittest.TestCase):
    """
    Unit Tests for Login File Mocking User Answer
    """

    def setUp(self) -> None:
        """
        Creates the directory and login file for the tests
        """
        self.dir_login_path = expanduser("~") + os.sep + ".testFolder"
        self.login_file_path = self.dir_login_path + os.sep + ".testProfile.json"

    def test_change_default_user(self, mock_user_answer):
        """
        Changes default user for server
        """
        mock_user_answer.return_value = "yes"
        no_default_user = {
            "server": "LocalHost1",
            "user": "User1",
            "password": "Password1",
            "port": 1234,
            "default": None
        }
        default_user = {
            "server": "LocalHost1",
            "user": "User2",
            "password": "Password2",
            "port": 1234,
            "default": True
        }
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User2", "Password2", 1234)
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1", 1234,
                                 True)
        self.assertTrue(_add_default_user(self.login_file_path, "LocalHost1", "User2"))
        with open(self.login_file_path, 'r') as file:
            file_data = json.load(file)
        self.assertDictEqual(file_data[1], no_default_user)
        self.assertDictEqual(file_data[0], default_user)
        clean_up()

    def test_avoid_set_default_user(self, mock_user_answer):
        """
        Avoids changing default user
        """
        mock_user_answer.return_value = "no"
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1", 1234, True)
        self.assertFalse(_add_default_user(self.login_file_path, "LocalHost1", "User1"))
        clean_up()

    def test_add_new_user_default_with_default_user_already_existed(self, mock_user_answer):
        """
        Replaces default user
        """
        mock_user_answer.return_value = "yes"
        old_default_entry = {
            "server": "LocalHost1",
            "user": "User1",
            "password": "Password1",
            "port": 1234,
            "default": None
        }
        new_default_entry = {
            "server": "LocalHost1",
            "user": "User2",
            "password": "Password2",
            "port": 1234,
            "default": True
        }
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User1", "Password1", 1234, True)
        _add_entry_to_login_file(self.dir_login_path, self.login_file_path, "LocalHost1",
                                 "User2", "Password2", 1234, True)
        with open(self.login_file_path, 'r') as file:
            file_data = json.load(file)
        self.assertDictEqual(file_data[0], old_default_entry)
        self.assertDictEqual(file_data[1], new_default_entry)
        clean_up()


def clean_up():
    """
    Cleans up the directory and login file after every execution
    """
    if os.path.isfile(LOGIN_FILE_PATH):
        os.remove(LOGIN_FILE_PATH)

    if os.path.isdir(DIR_LOGIN_PATH):
        os.rmdir(DIR_LOGIN_PATH)


atexit.register(clean_up)
