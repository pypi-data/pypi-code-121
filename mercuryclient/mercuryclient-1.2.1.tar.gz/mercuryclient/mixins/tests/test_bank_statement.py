from unittest import mock
from unittest import TestCase

from mercuryclient.api import MercuryApi


class BankStatementMixinTest(TestCase):
    def setUp(self):
        self.post_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._post_json_http_request"
        ).start()
        self.addCleanup(self.post_api_mock.stop)
        self.get_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._get_json_http_request"
        ).start()
        self.addCleanup(self.get_api_mock.stop)

    def test_send_bank_statement_request(self):
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
        client.request_bank_statement(
            "http://httpbin.org/status/200", "HDFC", "some_provider", "some_profile"
        )

        self.post_api_mock.assert_called_with(
            "api/v1/bank_statement/",
            data={
                "provider": "some_provider",
                "profile": "some_profile",
                "statement_file_url": "http://httpbin.org/status/200",
                "statement_bank_name": "HDFC",
            },
            send_request_id=True,
            add_bearer_token=True,
        )

        client.request_bank_statement(
            "http://httpbin.org/status/200",
            "HDFC",
            "some_provider",
            "some_profile",
            statement_password="somepassword",
        )

        self.post_api_mock.assert_called_with(
            "api/v1/bank_statement/",
            data={
                "provider": "some_provider",
                "profile": "some_profile",
                "statement_file_url": "http://httpbin.org/status/200",
                "statement_bank_name": "HDFC",
                "statement_password": "somepassword",
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

        rqid = client.request_bank_statement(
            "9876543210", "Random message", "some_provider", "some_profile"
        )
        self.assertEqual(rqid, "random_string")

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
        client.get_bank_statement_result("random_string")

        self.get_api_mock.assert_called_with(
            "api/v1/bank_statement/",
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
            client.get_bank_statement_result("random_string")

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

        rqid, result = client.get_bank_statement_result("random_string")
        self.assertEqual(rqid, "random_string")
        self.assertEqual(result["status"], "SUCCESS")
