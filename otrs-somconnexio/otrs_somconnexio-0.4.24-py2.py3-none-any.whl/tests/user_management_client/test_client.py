# coding: utf-8
import os
import unittest
import json
from mock import Mock, patch

from otrs_somconnexio.exceptions import UserManagementResponseEmpty
from otrs_somconnexio.user_management_client.client import UserManagementClient

USER = 'user'
PASSW = 'passw'
URL = 'https://otrs-url.coop/'


@patch.dict(os.environ, {
    'OTRS_USER': USER,
    'OTRS_PASSW': PASSW,
    'OTRS_URL': URL
})
class UserManagementClientTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'test@test.test'
        self.expected_url = '{}otrs/nph-genericinterface.pl/Webservice/UserManagement/cuser'.format(URL)

        self.expected_body = {
            "UserLogin": USER,
            "Password": PASSW,
            "Object": "Kernel::System::CustomerUser"
        }

    @patch('otrs_somconnexio.user_management_client.client.requests', spec=['post'])
    def test_set_user_preference(self, requests_mock):
        lang = 'es'
        preference_key = 'UserLanguage'

        self.expected_body["Method"] = "SetPreferences"
        self.expected_body["Parameter"] = {
            "Key": preference_key,
            "Value": lang,
            "UserID": self.user_id
        }

        requests_mock.post.return_value = Mock(spec=['json'])
        requests_mock.post.return_value.json.return_value = {"Result": [1]}

        UserManagementClient(self.user_id).set_preference(preference_key, lang)

        requests_mock.post.assert_called_once_with(
            self.expected_url, data=json.dumps(self.expected_body))

    @patch('otrs_somconnexio.user_management_client.client.requests', spec=['post'])
    def test_set_user_preference_raise_error_if_fails(self, requests_mock):
        lang = 'es'
        preference_key = 'UserLanguage'

        requests_mock.post.return_value = Mock(spec=['json'])
        requests_mock.post.return_value.json.return_value = {"Result": []}

        self.assertRaises(
            UserManagementResponseEmpty,
            UserManagementClient(self.user_id).set_preference,
            preference_key,
            lang
        )

    @patch('otrs_somconnexio.user_management_client.client.requests', spec=['post'])
    def test_get_user_preferences(self, requests_mock):

        self.expected_body["Method"] = "GetPreferences"
        self.expected_body["Parameter"] = {
            "UserID": self.user_id
        }
        expected_response = {
            "Result": ['key1', 'value1', 'key2', 'value2']
        }
        expected_result = {
            'key1': 'value1',
            'key2': 'value2'
        }

        requests_mock.post.return_value = Mock(spec=['json'])
        requests_mock.post.return_value.json.return_value = expected_response

        result = UserManagementClient(self.user_id).get_preferences()

        requests_mock.post.assert_called_once_with(
            self.expected_url, data=json.dumps(self.expected_body))

        self.assertEqual(result, expected_result)

    @patch('otrs_somconnexio.user_management_client.client.requests', spec=['post'])
    def test_get_empty_user_preferences(self, requests_mock):

        self.expected_body["Method"] = "GetPreferences"
        self.expected_body["Parameter"] = {
            "UserID": self.user_id
        }
        expected_response = {
            "Result": []
        }
        expected_result = {}

        requests_mock.post.return_value = Mock(spec=['json'])
        requests_mock.post.return_value.json.return_value = expected_response

        result = UserManagementClient(self.user_id).get_preferences()

        requests_mock.post.assert_called_once_with(
            self.expected_url, data=json.dumps(self.expected_body))

        self.assertEqual(result, expected_result)

    @patch('otrs_somconnexio.user_management_client.client.requests', spec=['post'])
    def test_get_data(self, requests_mock):

        self.expected_body["Method"] = "CustomerUserDataGet"
        self.expected_body["Parameter"] = {
            "User": self.user_id
        }

        expected_response = {
            "Result": ['key1', 'value1', 'key2', 'value2']
        }
        expected_result = {
            'key1': 'value1',
            'key2': 'value2'
        }

        requests_mock.post.return_value = Mock(spec=['json'])
        requests_mock.post.return_value.json.return_value = expected_response

        result = UserManagementClient(self.user_id).get_data()

        requests_mock.post.assert_called_once_with(
            self.expected_url, data=json.dumps(self.expected_body))

        self.assertEqual(result, expected_result)
