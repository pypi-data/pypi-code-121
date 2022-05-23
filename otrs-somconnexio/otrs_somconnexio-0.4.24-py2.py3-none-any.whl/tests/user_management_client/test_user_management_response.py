import unittest
from otrs_somconnexio.user_management_client.user_management_response import UserManagementResponse
from otrs_somconnexio.exceptions import UserManagementResponseEmpty


class FakeResponse():
    def __init__(self, value):
        self.content = {
            'Result': value
        }

    def json(self):
        return self.content


class UserManagementResponseTestCase(unittest.TestCase):

    def test_response_setting_call_ok(self):
        raw_response = FakeResponse([1])

        response = UserManagementResponse(
            raw_response,
            1,
            "Testing OK response"
        )

        self.assertEqual(response.raw_data, [1])

    def test_response_call_ko(self):
        raw_response = FakeResponse([])

        self.assertRaises(
            UserManagementResponseEmpty,
            UserManagementResponse,
            raw_response,
            1,
            "Testing KO response"
        )

    def test_response_getting_call_even_list(self):
        even_list = ['key', 'value']
        expected_dict = {'key': 'value'}
        raw_response = FakeResponse(even_list)

        response = UserManagementResponse(
            raw_response,
            1,
            "Getting call even list"
        )

        self.assertEqual(response.get_data(), expected_dict)

    def test_response_getting_call_odd_list(self):
        odd_list = ['key', 'value', 'key2']
        expected_dict = {'key': 'value'}
        raw_response = FakeResponse(odd_list)

        response = UserManagementResponse(
            raw_response,
            1,
            "Getting call odd list"
        )

        self.assertEqual(response.get_data(), expected_dict)
