from typing import List

from google.protobuf.empty_pb2 import Empty

from .. import CoreService_pb2 as pb
from ..entities.pat import PersonalAccessToken


class PersonalAccessTokens:
    def __init__(self, stub):
        self._stub = stub

    def generate(self, name: str, description: str, expiry_date: str = None) -> str:
        request = pb.GenerateTokenRequest()
        request.name = name
        request.description = description
        if expiry_date:
            request.expiry_date = expiry_date
        response = self._stub.GenerateToken(request)
        return response.token

    def list(self) -> List[PersonalAccessToken]:
        request = Empty()
        response = self._stub.ListTokens(request)
        return [PersonalAccessToken(self._stub, pat) for pat in response.tokens]

    def get(self, token_id: str) -> PersonalAccessToken:
        request = pb.TokenRequest()
        request.token_id = token_id
        response = self._stub.GetToken(request)
        return PersonalAccessToken(self._stub, response.token)

    def __repr__(self):
        return "This class wraps together methods working with Personal Access Tokens (PATs)"
