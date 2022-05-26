import json
import uuid
from datetime import timedelta
from typing import Iterator, List
from unittest.mock import ANY, patch
from urllib.parse import quote
from uuid import UUID

import pytest
import requests_mock
from pydantic import parse_obj_as

from sym.flow.cli.errors import (
    NotAuthorizedError,
    SymAPIAggregateError,
    SymAPIError,
    SymAPIUnknownError,
)
from sym.flow.cli.helpers.api import SymAPI, SymRESTClient
from sym.flow.cli.models.resource import ResourceType, TerraformResource
from sym.flow.cli.models.service import Service
from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.models.user import User
from sym.flow.cli.tests.conftest import get_mock_response
from sym.flow.cli.tests.factories.tokens import SymTokenFactory
from sym.flow.cli.tests.factories.users import UserFactory

MOCK_INTEGRATIONS_BAD_DATA = [
    {
        "name": "integration 1",
        "type": "aws",
    },
    {
        "name": "integration 2",
        "type": "aws_sso",
    },
]

MOCK_INTEGRATIONS_DATA = [
    {
        "id": "de6bd4ae-b30e-4033-9b06-bc918db2e619",
        "slug": "integration-1",
        "type": "aws",
        "srn": "test_org:sym_integration:aws:integration-1",
        "updated_at": "2021-01-19 19:29:46.505678+00",
    },
    {
        "id": "e8e46254-585d-4cac-9744-fd88a3c81390",
        "slug": "integration-2",
        "srn": "test_org:sym_integration:aws_sso:integration-2",
        "type": "aws_sso",
        "updated_at": "2021-01-19 18:29:46.505678+00",
    },
]

MOCK_SERVICES_DATA = {
    "services": [
        {
            "id": "e016f857-9979-4710-a53b-0dd6cedcae53",
            "slug": "google",
            "label": "Google",
            "external_id": "symops.io",
        },
        {
            "id": "166e7fef-c44b-40ce-b6ed-d3066799060a",
            "slug": "sym",
            "label": "Sym",
            "external_id": "cloud",
        },
        # This service will be filtered out by the get_services api because the service type is not recognized
        {
            "id": "abc",
            "slug": "cloud",
            "label": "Some service not in Service Types",
            "external_id": "cloud",
        },
    ]
}

MOCK_CREATE_SERVICE_DATA = {
    "status": "success",
    "errors": [],
    "succeeded": 1,
    "failed": 0,
    "results": [
        {
            "id": "4df1dae0-892b-47a1-9dee-9f818b7d331b",
            "slug": "slack",
            "label": "Slack",
            "external_id": "T123ABC",
        }
    ],
}

MOCK_SERVICE_REFERENCES_DATA = {
    "error": "false",
    "references": {
        "identities": ["274ab5cf-7322-430a-97eb-e7f3cec6a987"],
        "integrations": [],
    },
}


MOCK_BASE_URL = "http://faketest.symops.io/api/v1"


@pytest.fixture
def sym_rest_client(sandbox) -> Iterator[SymRESTClient]:
    with sandbox.push_xdg_config_home():
        yield SymRESTClient(url=MOCK_BASE_URL, access_token="")


@pytest.fixture
def sym_api(sandbox) -> Iterator[SymAPI]:
    with sandbox.push_xdg_config_home():
        yield SymAPI(url=MOCK_BASE_URL, access_token="abc")


class TestSymRESTClient:
    def test_make_headers(self, sym_rest_client, auth_token):
        with pytest.raises(NotAuthorizedError, match="symflow login"):
            sym_rest_client.make_headers()

        sym_rest_client.access_token = "access"
        headers = sym_rest_client.make_headers()
        assert headers.get("X-Sym-Request-ID") is not None
        assert headers.get("Authorization") == "Bearer access"

    def test_handle_response(self, sym_rest_client):
        response_500 = get_mock_response(500)
        with pytest.raises(SymAPIUnknownError, match="500"):
            sym_rest_client.handle_response(response_500)

        response_400 = get_mock_response(400)
        with pytest.raises(SymAPIUnknownError, match="400"):
            sym_rest_client.handle_response(response_400)

        response_with_msg = get_mock_response(
            401,
            {
                "error": True,
                "message": "The provided JWT could not be validated.",
                "code": "AuthenticationError:INVALID_JWT",
                "status_code": 401,
                "is_retryable": False,
            },
        )
        with pytest.raises(SymAPIAggregateError, match=response_with_msg.data["message"]):
            sym_rest_client.handle_response(response_with_msg)

        response_with_error_list = get_mock_response(
            400,
            {
                "status": "error",
                "errors": ["some error message"],
                "succeeded": 0,
                "failed": 1,
                "results": [],
            },
        )
        with pytest.raises(
            SymAPIAggregateError, match=response_with_error_list.data["errors"][0]
        ):
            sym_rest_client.handle_response(response_with_error_list)

        response_200 = get_mock_response(200)
        assert sym_rest_client.handle_response(response_200) == response_200

    @patch(
        "requests.request",
        return_value=get_mock_response(200),
    )
    def test_request(self, mock_request, sym_rest_client):
        data = {"test": "hello"}

        # Auth is required by default, make sure if force_auth not specified
        with pytest.raises(NotAuthorizedError, match="symflow login"):
            sym_rest_client.post("fake-endpoint", data)

        mock_request.assert_not_called()

        # If force_auth specified False, we should let the call through
        sym_rest_client._request("POST", "fake-endpoint", force_auth=False, data=data)
        mock_request.assert_called_with(
            "POST",
            url=f"{MOCK_BASE_URL}/fake-endpoint",
            data=json.dumps(data),
            headers=ANY,
            params=ANY,
        )

        # If force_auth not specified False but access token exists, let call through
        sym_rest_client.access_token = "access"
        sym_rest_client.post("fake-endpoint", data)
        mock_request.assert_called_with(
            "POST",
            url=f"{MOCK_BASE_URL}/fake-endpoint",
            data=json.dumps(data),
            headers=ANY,
            params=ANY,
        )


class TestSymAPI:
    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200, {"client_id": "12345abc", "slug": "test"})),
    )
    def test_get_organization_from_email(self, mock_api_get, sym_api, test_org):
        email = "test@symops.io"
        org_data = sym_api.get_organization_from_email(email)

        mock_api_get.assert_called_once_with(
            "auth/org", {"email": email}, force_auth=False
        )

        assert org_data["slug"] == test_org["slug"]
        assert org_data["client_id"] == test_org["client_id"]

    @pytest.mark.parametrize("status_code", [400, 403, 500])
    def test_verify_login_failure(self, status_code, sym_api):
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.get",
            return_value=(get_mock_response(status_code)),
        ) as mock_api_get:
            assert sym_api.verify_login("test@symops.io") is False

        mock_api_get.assert_called_once_with(
            "auth/login", {"email": "test@symops.io"}, validate=False
        )

    @pytest.mark.parametrize("status_code", [200])
    def test_verify_login_success(self, status_code, sym_api):
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.get",
            return_value=(get_mock_response(status_code)),
        ) as mock_api_get:
            assert sym_api.verify_login("test@symops.io") is True
        mock_api_get.assert_called_once_with(
            "auth/login", {"email": "test@symops.io"}, validate=False
        )

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200, data=MOCK_INTEGRATIONS_DATA)),
    )
    def test_get_integrations(self, _, sym_api):
        data = sym_api.get_integrations()
        assert len(data) == 2
        assert data[0]["slug"] == "integration-1"
        assert data[0]["type"] == "aws"
        assert data[0]["srn"] == "test_org:sym_integration:aws:integration-1"
        assert data[0]["updated_at"] == "2021-01-19 19:29:46.505678+00"
        assert data[1]["slug"] == "integration-2"
        assert data[1]["type"] == "aws_sso"
        assert data[1]["srn"] == "test_org:sym_integration:aws_sso:integration-2"
        assert data[1]["updated_at"] == "2021-01-19 18:29:46.505678+00"

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200, data=MOCK_INTEGRATIONS_DATA)),
    )
    def test_get_resources(self, _, sym_api):
        data = sym_api.get_resources(resource_type=ResourceType.SYM_INTEGRATION)
        assert len(data) == 2

        resource = data[0]
        assert isinstance(resource, TerraformResource)
        assert resource.identifier == UUID("de6bd4ae-b30e-4033-9b06-bc918db2e619")
        assert resource.sub_type == "aws"
        assert resource.slug == "integration-1"

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200, data=MOCK_SERVICES_DATA)),
    )
    def test_get_services(self, mock_api_get, sym_api):
        all_services = parse_obj_as(List[Service], MOCK_SERVICES_DATA["services"])
        expected_services = [
            s for s in all_services if s.service_type in ServiceType.all_names()
        ]

        data = sym_api.get_services()
        mock_api_get.assert_called_once_with("services")
        assert data == expected_services

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(
            get_mock_response(200, {"services": MOCK_SERVICES_DATA["services"][:1]})
        ),
    )
    def test_get_service(self, mock_api_get, sym_api):
        expected = Service.parse_obj(MOCK_SERVICES_DATA["services"][0])

        data = sym_api.get_service(expected.service_type, expected.external_id)
        mock_api_get.assert_called_once_with(
            "services",
            {
                "service_type": expected.service_type,
                "external_id": expected.external_id,
            },
        )
        assert data == expected

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200, MOCK_SERVICES_DATA)),
    )
    def test_get_service_unexpected_response(self, mock_api_get, sym_api):
        # Mock returns more than one service
        with pytest.raises(SymAPIError, match="Expected 1 service, but found 3 instead"):
            sym_api.get_service("slack", "T123")

        mock_api_get.assert_called_once_with(
            "services", {"service_type": "slack", "external_id": "T123"}
        )

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.post",
        return_value=(get_mock_response(200, data=MOCK_CREATE_SERVICE_DATA)),
    )
    def test_create_service(self, mock_api_post, sym_api):
        service_type = ServiceType.SLACK
        external_id = "T123ABC"
        service = sym_api.create_service(service_type, external_id)
        mock_api_post.assert_called_once_with(
            "services",
            {"service_type": service_type.type_name, "external_id": external_id},
        )
        assert service.service_type == service_type.type_name
        assert service.external_id == external_id

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.post",
        return_value=(get_mock_response(200)),
    )
    def test_delete_services(self, mock_api_post, sym_api):
        service_type = ServiceType.SLACK
        external_id = "T123ABC"
        sym_api.delete_service(service_type.type_name, external_id)
        mock_api_post.assert_called_once_with(
            "services/delete",
            {"service_type": service_type.type_name, "external_id": external_id},
        )

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200, MOCK_SERVICE_REFERENCES_DATA)),
    )
    def test_get_service_references(self, mock_api_get, sym_api):

        data = sym_api.get_service_references("fake-service-id")
        mock_api_get.assert_called_once_with(
            "service/fake-service-id/references",
        )
        assert data == MOCK_SERVICE_REFERENCES_DATA["references"]

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200, {"url": "http://hello.sym.com"})),
    )
    def test_get_slack_install_url(self, mock_api_get, sym_api):
        url = sym_api.get_slack_install_url("fake_service_id")
        mock_api_get.assert_called_once_with(
            "services/slack/link", {"service_id": "fake_service_id"}
        )
        assert url == "http://hello.sym.com"

    @patch(
        "sym.flow.cli.helpers.api.SymRESTClient.get",
        return_value=(get_mock_response(200)),
    )
    def test_uninstall_slack(self, mock_api_get, sym_api):
        assert sym_api.uninstall_slack(service_id="T1234567") is None
        mock_api_get.assert_called_once_with(
            "services/slack/uninstall", {"token": "T1234567"}, validate=False
        )

    def test_last_request_id(self, sym_api):
        with requests_mock.Mocker() as m:
            email = "user@example.com"
            m.get(
                f"{MOCK_BASE_URL}/auth/org?email={quote(email)}",
                text='{"slug": "fake-org", "client_id": "fake-client-id"}',
            )

            assert not sym_api.rest.last_request_id
            resp = sym_api.get_organization_from_email(email)
            assert resp["slug"] == "fake-org"
            assert sym_api.rest.last_request_id

    def test_get_users(self, sym_api: SymAPI):
        users: List[User] = UserFactory.create_batch(5)
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.get",
            return_value=(get_mock_response(200, {"users": users})),
        ) as mock_api_get:
            data = sym_api.get_users()
            mock_api_get.assert_called_once_with("users", None)
            assert data == users

    def test_get_user(self, sym_api: SymAPI):
        users: List[User] = UserFactory.create_batch(5)
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.get",
            return_value=(get_mock_response(200, {"users": users})),
        ) as mock_api_get:
            data = sym_api.get_user(users[0].sym_email)
            mock_api_get.assert_called_once_with("users", None)
            assert data == users[0]

    def test_get_user_by_id(self, sym_api: SymAPI):
        users: List[User] = UserFactory.create_batch(5)
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.get",
            return_value=(get_mock_response(200, {"users": users[0:1]})),
        ) as mock_api_get:
            user_uuid = uuid.UUID(users[0].id)
            data = sym_api.get_user_by_id(user_uuid)
            mock_api_get.assert_called_once_with("users", {"id": user_uuid})
            assert data == users[0]

    def test_create_token(self, sym_api: SymAPI):
        access_token = str(uuid.uuid4())
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.post",
            return_value=(get_mock_response(200, {"access_token": access_token})),
        ) as mock_api:
            username = "bot-user"
            expiry = timedelta(seconds=30)
            label = "some label"
            data = sym_api.create_token(username, expiry, label)
            mock_api.assert_called_once_with(
                "tokens",
                {"username": username, "expiry": expiry.total_seconds(), "label": label},
            )
            assert data == access_token

    def test_create_token_no_label(self, sym_api: SymAPI):
        access_token = str(uuid.uuid4())
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.post",
            return_value=(get_mock_response(200, {"access_token": access_token})),
        ) as mock_api:
            username = "bot-user"
            expiry = timedelta(seconds=30)
            data = sym_api.create_token(username, expiry)
            mock_api.assert_called_once_with(
                "tokens", {"username": username, "expiry": expiry.total_seconds()}
            )
            assert data == access_token

    def test_revoke_token(self, sym_api: SymAPI):
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.post",
            return_value=(get_mock_response(200)),
        ) as mock_api:
            identifier = str(uuid.uuid4())
            sym_api.revoke_token(identifier)
            mock_api.assert_called_once_with("tokens/delete", {"identifier": identifier})

    def test_get_tokens(self, sym_api: SymAPI):
        tokens = SymTokenFactory.create_batch(3)
        with patch(
            "sym.flow.cli.helpers.api.SymRESTClient.get",
            return_value=(get_mock_response(200, {"tokens": tokens})),
        ) as mock_api:
            result = sym_api.get_tokens()

            mock_api.assert_called_once_with("tokens")
            assert result == tokens
