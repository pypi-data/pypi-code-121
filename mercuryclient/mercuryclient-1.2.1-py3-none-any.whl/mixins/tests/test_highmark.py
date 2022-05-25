from unittest import mock
from unittest import TestCase

from mercuryclient.api import MercuryApi
from mercuryclient.types.highmark.request import (
    Address,
    Applicant,
    HighmarkRequest,
    Identity,
    Relation,
)


class HighmarkMixinTest(TestCase):
    def setUp(self):
        self.client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        self.request_obj = HighmarkRequest(
            inquiry_reference_number="ref_no",
            credit_request_type="INDIVIDUAL",
            credit_transaction_id="transaction_id",
            inquiry_purpose_type="ACCT-ORIG",
            inquiry_purpose_type_desc="AUTO_LOAN",
            inquiry_stage="PRE_SCREEN",
            los_app_id="RANDOM_APP_ID",
            loan_amount=100,
            applicant=Applicant(
                name="Sample Name",
                date_of_birth="2000-01-01",
                nominee=Relation(relation_type="FATHER", relation_name="Mr. Father"),
                identities=[Identity(id_type="PAN_CARD", id_number="ABCDE123")],
                addresses=[
                    Address(
                        address_type="RESIDENCE",
                        address_line_1="Random Address",
                        city="Random City",
                        state="BIHAR",
                        pincode="123456",
                    )
                ],
            ),
        )
        self.request_dict = {
            "profile": "some_profile",
            "inquiry_reference_number": "ref_no",
            "credit_request_type": "INDIVIDUAL",
            "credit_transaction_id": "transaction_id",
            "inquiry_purpose_type": "ACCT-ORIG",
            "inquiry_purpose_type_desc": "AUTO_LOAN",
            "inquiry_stage": "PRE_SCREEN",
            "los_app_id": "RANDOM_APP_ID",
            "loan_amount": 100,
            "applicant": {
                "name": "Sample Name",
                "date_of_birth": "2000-01-01",
                "identities": [{"id_type": "PAN_CARD", "id_number": "ABCDE123"}],
                "nominee": {"relation_type": "FATHER", "relation_name": "Mr. Father"},
                "addresses": [
                    {
                        "address_type": "RESIDENCE",
                        "address_line_1": "Random Address",
                        "city": "Random City",
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
        self.sleep_mock = mock.patch("mercuryclient.mixins.highmark.time.sleep").start()
        self.sleep_mock.return_value = None
        self.addCleanup(self.get_api_mock.stop)

    def test_request_highmark_report(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)

        self.client.request_highmark_report(self.request_obj, "some_profile")

        self.post_api_mock.assert_called_with(
            "api/v1/highmark/",
            data=self.request_dict,
            send_request_id=True,
            add_bearer_token=True,
        )

    def test_request_exception_raised_if_status_code_error(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        self.post_api_mock.return_value = ("random_string", mock_response)

        with self.assertRaises(Exception):
            self.client.request_highmark_report(self.request_obj, "some_profile")

    def test_request_api_succeeds_if_status_code_success(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_string", mock_response)

        request_id = self.client.request_highmark_report(
            self.request_obj, "some_profile"
        )
        self.assertEqual(request_id, "random_string")

    def test_response_highmark_report(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        self.get_api_mock.return_value = ("random_string", mock_response)
        self.client.get_highmark_response("random_string")

        self.get_api_mock.assert_called_with(
            "api/v1/highmark/",
            headers={"X-Mercury-Request-Id": "random_string"},
            send_request_id=False,
            add_bearer_token=True,
        )

    def test_response_exception_raised_if_status_code_error(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        self.get_api_mock.return_value = ("random_string", mock_response)
        with self.assertRaises(Exception):
            self.client.get_highmark_response("random_string")

    def test_response_api_succeeds_if_status_code_success(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json = mock.MagicMock()
        mock_response.json.return_value = {"status": "SUCCESS"}
        self.get_api_mock.return_value = ("random_string", mock_response)

        request_id, result = self.client.get_highmark_response("random_string")
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

        response = self.client.fetch_highmark_report(self.request_obj, "some_profile")

        self.post_api_mock.assert_called_with(
            "api/v1/highmark/",
            data=self.request_dict,
            send_request_id=True,
            add_bearer_token=True,
        )
        self.get_api_mock.assert_called_with(
            "api/v1/highmark/",
            headers={"X-Mercury-Request-Id": "random_string"},
            send_request_id=False,
            add_bearer_token=True,
        )
        self.sleep_mock.assert_called_with(11)
        self.assertEqual(response["status"], "SUCCESS")

    def test_entire_request_response_flow_failure(self):
        client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )
        mock_post_response = mock.MagicMock()
        mock_post_response.status_code = 201
        mock_get_response = mock.MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json = mock.MagicMock()
        mock_get_response.json.return_value = {"status": "IN_PROGRESS"}
        self.post_api_mock.return_value = ("random_string", mock_post_response)
        self.get_api_mock.return_value = ("random_string", mock_get_response)

        with self.assertRaises(Exception):
            client.fetch_highmark_report(self.request_obj, "some_profile")
