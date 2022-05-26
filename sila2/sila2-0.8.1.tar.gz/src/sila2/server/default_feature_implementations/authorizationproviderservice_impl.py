from typing import Dict
from uuid import UUID

from sila2.features.authorizationproviderservice import (
    AuthorizationFailed,
    AuthorizationProviderServiceBase,
    InvalidAccessToken,
    Verify_Responses,
)
from sila2.framework import FullyQualifiedIdentifier
from sila2.server import SilaServer
from sila2.server.default_feature_implementations.authenticationservice_impl import AccessToken
from sila2.server.metadata_dict import MetadataDict


class AuthorizationProviderServiceImpl(AuthorizationProviderServiceBase):
    tokens: Dict[UUID, AccessToken]

    def __init__(self, parent_server: SilaServer):
        super().__init__(parent_server=parent_server)
        self.server_uuid = parent_server.server_uuid
        self.tokens = parent_server.feature_servicers["AuthenticationService"].implementation.active_tokens

    def Verify(
        self, AccessToken: str, RequestedServer: str, RequestedFeature: str, *, metadata: MetadataDict
    ) -> Verify_Responses:
        try:
            token = self.tokens[UUID(AccessToken)]
        except ValueError:
            raise InvalidAccessToken  # no UUID
        except KeyError:
            raise AuthorizationFailed  # unknown token

        if UUID(RequestedServer) != self.server_uuid:
            raise AuthorizationFailed

        if FullyQualifiedIdentifier(RequestedFeature) not in token.features:
            raise AuthorizationFailed

        if token.remaining_lifetime.total_seconds() <= 0:
            self.tokens.pop(token.token)
            raise AuthorizationFailed

        return Verify_Responses(int(token.remaining_lifetime.total_seconds()))
