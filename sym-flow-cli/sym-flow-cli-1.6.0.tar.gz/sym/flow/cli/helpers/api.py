from datetime import timedelta
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import parse_obj_as

from sym.flow.cli.errors import (
    SymAPIError,
    SymAPIMissingEntityError,
    UnknownBotError,
    UnknownOrgError,
    UnknownUserError,
)
from sym.flow.cli.helpers.config import Config
from sym.flow.cli.helpers.rest import SymRESTClient
from sym.flow.cli.helpers.utils import filter_dict
from sym.flow.cli.models import Organization
from sym.flow.cli.models.resource import ResourceType, TerraformResource
from sym.flow.cli.models.service import Service
from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.models.token import SymToken
from sym.flow.cli.models.user import User
from sym.flow.cli.models.user_type import UserType


class SymAPI:
    def __init__(self, url: str, access_token: Optional[str] = None):
        self.rest = SymRESTClient(
            url=url, access_token=access_token or Config.get_access_token()
        )

    def set_access_token(self, access_token: str):
        self.rest.access_token = access_token

    def get_organization_from_email(self, email: str) -> Organization:
        """Exchanges the provided email for the corresponding Organization data."""
        try:
            response = self.rest.get(
                "auth/org", {"email": email}, force_auth=False
            ).json()
            return Organization(slug=response["slug"], client_id=response["client_id"])
        except (KeyError, SymAPIMissingEntityError) as err:
            raise UnknownOrgError(email) from err

    def verify_login(self, email: Optional[str] = None) -> bool:
        """Returns True if the User's current credentials are valid as determined by the Sym API, False otherwise
        If an email is available to validate, include it in the request,
        """
        response = self.rest.get(
            "auth/login", filter_dict({"email": email}), validate=False
        )
        return response.status_code == 200

    def get_integrations(self) -> List[dict]:
        """Retrieve all Sym Integrations accessible to the currently
        authenticated user.
        """
        return self.rest.get("entities/integrations").json()

    def get_users(self, query_params: Optional[dict] = None) -> List[User]:
        """Retrieve all Sym Users accessible to the currently
        authenticated user.
        """

        response = self.rest.get("users", query_params).json()
        return parse_obj_as(List[User], response["users"])

    def get_user(self, email: str) -> User:
        """Given an email, get the whole user object and their identities"""
        users = self.get_users()
        user = next((u for u in users if u.sym_email == email), None)
        if not user:
            raise UnknownUserError(email=email)

        return user

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Given a User UUID, get the whole user object and their identities"""
        users = self.get_users({"id": user_id})
        if users:
            return users[0]

        return None

    def get_bot(self, username: str) -> User:
        """Given a bot username, get the whole bot object and their identities"""
        bots = self.get_users({"type": UserType.BOT})
        bot = next((b for b in bots if b.sym_identifier == username), None)

        if not bot:
            raise UnknownBotError(username=username)

        return bot

    def update_users(self, payload: dict) -> List[dict]:
        return self.rest.patch("users", payload).json()

    def delete_user(self, payload: dict) -> List[dict]:
        return self.rest.post("users/delete", payload).json()

    def delete_identities(self, payload: dict) -> List[dict]:
        return self.rest.post("users/identities/delete", payload).json()

    def get_slack_install_url(self, service_id: str) -> str:
        """Get the URL that starts the Slack App installation flow.

        Returns:
            The URL to install the Slack App and the Sym Request ID used to
            retrieve the URL as a string.
        """

        return self.rest.get("services/slack/link", {"service_id": service_id}).json()[
            "url"
        ]

    def uninstall_slack(self, service_id: str) -> None:
        """Make a request to the Sym API to uninstall the Slack App.

        Raises SymAPIUnknownError from handle_response on failure. Otherwise,
        assume success.
        """

        self.rest.get("services/slack/uninstall", {"token": service_id}, validate=False)

    def get_services(
        self, service_types: List[str] = ServiceType.all_names()
    ) -> List[Service]:
        """Retrieve services in service_types registered to the currently
        authenticated user's organization.

        service_types defaults to all recognized service types
        """
        response = self.rest.get("services").json()
        services = parse_obj_as(List[Service], response["services"])

        return [s for s in services if s.service_type in service_types]

    def get_service(self, service_type: str, external_id: str) -> Service:
        """Retrieve a Service by the given service_type and external_id.
        Expects that the response will have exactly one Service
        """
        response = self.rest.get(
            "services", {"service_type": service_type, "external_id": external_id}
        ).json()
        services = parse_obj_as(List[Service], response["services"])
        if (num_services := len(services)) != 1:
            raise SymAPIError(
                f"Expected 1 service, but found {num_services} instead",
                "400",
                self.rest.last_request_id,
            )

        return services[0]

    def create_service(self, service_type: ServiceType, external_id: str) -> Service:
        """Creates a new Service for the currently authenticated user's organization"""
        response = self.rest.post(
            "services",
            {"service_type": service_type.type_name, "external_id": external_id},
        ).json()
        return Service.parse_obj(response["results"][0])

    def delete_service(self, service_type_name: str, external_id: str):
        """Deletes a Service from the currently authenticated user's organization"""
        return self.rest.post(
            "services/delete",
            {"service_type": service_type_name, "external_id": external_id},
        ).json()

    def get_service_references(self, service_id: str) -> Dict[str, List[str]]:
        """Gets all objects referencing a service, i.e. Identities/Integrations
        if any exist, a service cannot be deleted"""
        return self.rest.get(f"service/{service_id}/references").json()["references"]

    def create_token(
        self, username: str, expiry: timedelta, label: Optional[str] = None
    ) -> str:
        """Creates a new token in the organization for the given bot-user and expiry"""
        expiry_in_seconds = expiry.total_seconds()
        response = self.rest.post(
            "tokens",
            filter_dict(
                {"username": username, "expiry": expiry_in_seconds, "label": label}
            ),
        ).json()

        return response["access_token"]

    def revoke_token(self, jti: str):
        return self.rest.post(
            "tokens/delete",
            {"identifier": jti},
        ).json()

    def get_tokens(self) -> List[SymToken]:
        response = self.rest.get(
            "tokens",
        ).json()
        return parse_obj_as(List[SymToken], response["tokens"])

    def get_resources(self, resource_type: ResourceType) -> List[TerraformResource]:
        """Retrieve all of an Organization's Terraform resources of a particular type."""

        response = self.rest.get(f"entities/{resource_type}").json()
        return parse_obj_as(List[TerraformResource], response)
