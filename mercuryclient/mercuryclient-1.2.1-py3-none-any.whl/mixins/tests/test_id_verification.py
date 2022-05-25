from datetime import date
from unittest import TestCase, mock

from mercuryclient.api import MercuryApi
from mercuryclient.types.id_verification.request import PassportDetails


class IDVerificationMixinTest(TestCase):
    def setUp(self):
        self.client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )

        self.post_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._post_json_http_request"
        ).start()
        self.addCleanup(self.post_api_mock.stop)
        self.get_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._get_json_http_request"
        ).start()
        self.addCleanup(self.get_api_mock.stop)

    def test_wrong_id_type_raises_exception(self):
        with self.assertRaises(Exception) as exc:
            self.client.request_verify_id(
                "Something", "ABCDE1234", "aadhaarapi", "some_profile"
            )

        self.assertEqual(str(exc.exception), "Something is not a valid id_type")
        self.post_api_mock.assert_not_called()

    def test_request_id_verification(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)

        self.client.request_verify_id(
            "PAN_CARD", "ABCDE1234", "aadhaarapi", "some_profile"
        )

        self.post_api_mock.assert_called_with(
            "api/v1/id_verification/",
            data={
                "provider": "aadhaarapi",
                "profile": "some_profile",
                "id_type": "PAN_CARD",
                "id_number": "ABCDE1234",
            },
            send_request_id=True,
            add_bearer_token=True,
        )

    def test_request_id_verification_passport(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)

        passport_details = PassportDetails(
            first_name="Sample",
            last_name="Name",
            date_of_birth=date(1991, 1, 1),
            expiry_date=date(1995, 6, 6),
            gender="MALE",
            passport_type="PERSONAL",
            country="INDIA",
        )

        with self.assertRaises(Exception) as exc:
            self.client.request_verify_id(
                "PASSPORT", "ABCDE1234", "aadhaarapi", "some_profile"
            )

        self.assertEqual(
            str(exc.exception), "passport_details required for PASSPORT ID Type"
        )

        self.client.request_verify_id(
            "PASSPORT",
            "ABCDE1234",
            "aadhaarapi",
            "some_profile",
            passport_details=passport_details,
        )

        self.post_api_mock.assert_called_with(
            "api/v1/id_verification/",
            data={
                "provider": "aadhaarapi",
                "profile": "some_profile",
                "id_type": "PASSPORT",
                "id_number": "ABCDE1234",
                "passport_details": {
                    "first_name": "Sample",
                    "last_name": "Name",
                    "date_of_birth": "1991-01-01",
                    "expiry_date": "1995-06-06",
                    "gender": "MALE",
                    "passport_type": "PERSONAL",
                    "country": "INDIA",
                },
            },
            send_request_id=True,
            add_bearer_token=True,
        )

    def test_request_exception_raised_if_status_code_error(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        self.post_api_mock.return_value = ("random_string", mock_response)

        with self.assertRaises(Exception):
            self.client.request_verify_id(
                "PAN_CARD", "ABCDE1234", "aadhaarapi", "some_profile"
            )

    def test_request_api_succeeds_if_status_code_success(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)

        request_id = self.client.request_verify_id(
            "PAN_CARD", "ABCDE1234", "aadhaarapi", "some_profile"
        )
        self.assertEqual(request_id, "random_string")

    def test_response_verify_id(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        self.get_api_mock.return_value = ("random_string", mock_response)
        self.client.get_verify_id_result("random_string")

        self.get_api_mock.assert_called_with(
            "api/v1/id_verification/",
            headers={"X-Mercury-Request-Id": "random_string"},
            send_request_id=False,
            add_bearer_token=True,
        )

    def test_response_exception_raised_if_status_code_error(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        self.get_api_mock.return_value = ("random_string", mock_response)
        with self.assertRaises(Exception):
            self.client.get_verify_id_result("random_string")

    def test_response_api_succeeds_if_status_code_success(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json = mock.MagicMock()
        mock_response.json.return_value = {"status": "SUCCESS"}
        self.get_api_mock.return_value = ("random_string", mock_response)

        request_id, result = self.client.get_verify_id_result("random_string")
        self.assertEqual(request_id, "random_string")
        self.assertEqual(result["status"], "SUCCESS")
