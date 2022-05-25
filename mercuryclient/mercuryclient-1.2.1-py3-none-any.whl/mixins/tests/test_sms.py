from unittest import mock
from unittest import TestCase

from mercuryclient.api import MercuryApi


class SMSMixinTest(TestCase):
    def setUp(self):
        self.post_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._post_json_http_request"
        ).start()
        self.addCleanup(self.post_api_mock.stop)
        self.get_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._get_json_http_request"
        ).start()
        self.addCleanup(self.get_api_mock.stop)

    def test_send_sms_request(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)
        client.send_sms("9876543210", "Random message", "some_provider", "some_profile")

        self.post_api_mock.assert_called_with(
            "api/v1/sms/",
            data={
                "provider": "some_provider",
                "profile": "some_profile",
                "recipient": "9876543210",
                "message": "Random message",
            },
            send_request_id=True,
            add_bearer_token=True,
        )

    def test_request_exception_raised_if_status_code_error(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        self.post_api_mock.return_value = ("random_string", mock_response)
        with self.assertRaises(Exception):
            client.send_sms(
                "9876543210", "Random message", "some_provider", "some_profile"
            )

    def test_request_api_succeeds_if_status_code_success(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)

        response = client.send_sms(
            "9876543210", "Random message", "some_provider", "some_profile"
        )
        self.assertEqual(response["request_id"], "random_string")
        self.assertEqual(response["status"], "Success")

    def test_response_sms_result(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        self.get_api_mock.return_value = ("random_string", mock_response)
        client.get_sms_result("random_string")

        self.get_api_mock.assert_called_with(
            "api/v1/sms/",
            headers={"X-Mercury-Request-Id": "random_string"},
            send_request_id=False,
            add_bearer_token=True,
        )

    def test_response_exception_raised_if_status_code_error(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        self.get_api_mock.return_value = ("random_string", mock_response)
        with self.assertRaises(Exception):
            client.get_sms_result("random_string")

    def test_response_api_succeeds_if_status_code_success(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json = mock.MagicMock()
        mock_response.json.return_value = {"status": "SUCCESS"}
        self.get_api_mock.return_value = ("random_string", mock_response)

        response = client.get_sms_result("random_string")
        self.assertEqual(response["request_id"], "random_string")
        self.assertEqual(response["status"], "SUCCESS")
