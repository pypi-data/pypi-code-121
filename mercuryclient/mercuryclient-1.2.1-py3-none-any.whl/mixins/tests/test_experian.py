from unittest import mock
from unittest import TestCase

from mercuryclient.api import MercuryApi
from mercuryclient.types.experian.request import (
    Address,
    Applicant,
    ExperianRequest,
    Identity,
)


class ExperianMixinTest(TestCase):
    def setUp(self):
        self.client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        self.request_obj = ExperianRequest(
            enquiry_reason="AUTO_LOAN",
            finance_purpose="NEW_CAR",
            amount_financed=100,
            duration_of_agreement=12,
            applicant=Applicant(
                first_name="Sample",
                last_name="Name",
                gender="MALE",
                date_of_birth="2000-01-01",
                pan=Identity(id_number="ABCDE1234"),
                addresses=[
                    Address(
                        address_line_1="Random address",
                        city="This City",
                        state="BIHAR",
                        pincode="123456",
                    )
                ],
            ),
        )
        self.request_dict = {
            "profile": "some_profile",
            "enquiry_reason": "AUTO_LOAN",
            "finance_purpose": "NEW_CAR",
            "amount_financed": 100,
            "duration_of_agreement": 12,
            "applicant": {
                "first_name": "Sample",
                "last_name": "Name",
                "gender": "MALE",
                "date_of_birth": "2000-01-01",
                "pan": {"id_number": "ABCDE1234"},
                "addresses": [
                    {
                        "address_line_1": "Random address",
                        "city": "This City",
                        "state": "BIHAR",
                        "pincode": "123456",
                    }
                ],
            },
        }

        self.post_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._post_json_http_request"
        ).start()
        self.addCleanup(self.post_api_mock.stop)
        self.get_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._get_json_http_request"
        ).start()
        self.addCleanup(self.get_api_mock.stop)
        self.sleep_mock = mock.patch("mercuryclient.mixins.experian.time.sleep").start()
        self.sleep_mock.return_value = None
        self.addCleanup(self.get_api_mock.stop)

    def test_request_experian_report(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)
        self.client.request_experian_report(self.request_obj, "some_profile")

        self.post_api_mock.assert_called_with(
            "api/v1/experian/",
            data=self.request_dict,
            send_request_id=True,
            add_bearer_token=True,
        )

    def test_request_exception_raised_if_status_code_error(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        self.post_api_mock.return_value = ("random_string", mock_response)
        with self.assertRaises(Exception):
            self.client.request_experian_report(self.request_obj, "some_profile")

    def test_request_api_succeeds_if_status_code_success(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)

        request_id = self.client.request_experian_report(
            self.request_obj, "some_profile"
        )
        self.assertEqual(request_id, "random_string")

    def test_response_experian_report(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        self.get_api_mock.return_value = ("random_string", mock_response)
        self.client.get_experian_response("random_string")

        self.get_api_mock.assert_called_with(
            "api/v1/experian/",
            headers={"X-Mercury-Request-Id": "random_string"},
            send_request_id=False,
            add_bearer_token=True,
        )

    def test_response_exception_raised_if_status_code_error(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        self.get_api_mock.return_value = ("random_string", mock_response)
        with self.assertRaises(Exception):
            self.client.get_experian_response("random_string")

    def test_response_api_succeeds_if_status_code_success(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json = mock.MagicMock()
        mock_response.json.return_value = {"status": "SUCCESS"}
        self.get_api_mock.return_value = ("random_string", mock_response)

        request_id, result = self.client.get_experian_response("random_string")
        self.assertEqual(request_id, "random_string")
        self.assertEqual(result["status"], "SUCCESS")

    def test_entire_request_response_flow(self):
        mock_post_response = mock.MagicMock()
        mock_post_response.status_code = 201
        mock_get_response = mock.MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json = mock.MagicMock()
        mock_get_response.json.return_value = {"status": "SUCCESS"}
        self.post_api_mock.return_value = ("random_string", mock_post_response)
        self.get_api_mock.return_value = ("random_string", mock_get_response)

        response = self.client.fetch_experian_report(self.request_obj, "some_profile")

        self.post_api_mock.assert_called_with(
            "api/v1/experian/",
            data=self.request_dict,
            send_request_id=True,
            add_bearer_token=True,
        )
        self.get_api_mock.assert_called_with(
            "api/v1/experian/",
            headers={"X-Mercury-Request-Id": "random_string"},
            send_request_id=False,
            add_bearer_token=True,
        )
        self.sleep_mock.assert_called_with(15)
        self.assertEqual(response["status"], "SUCCESS")

    def test_entire_request_response_flow_failure(self):
        mock_post_response = mock.MagicMock()
        mock_post_response.status_code = 201
        mock_get_response = mock.MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json = mock.MagicMock()
        mock_get_response.json.return_value = {"status": "IN_PROGRESS"}
        self.post_api_mock.return_value = ("random_string", mock_post_response)
        self.get_api_mock.return_value = ("random_string", mock_get_response)

        with self.assertRaises(Exception):
            self.client.fetch_experian_report(self.request_obj, "some_profile")
