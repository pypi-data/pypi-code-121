from jarvis_sdk.indykite.identity.v1beta1 import identity_management_api_pb2 as pb2
from google.protobuf import struct_pb2

def enrich_token(self, user_token: str, token_claims: dict, session_claims: dict):
    try:
        token_struct = struct_pb2.Struct()
        if token_claims is not None:
            token_struct.update(token_claims)

        session_struct = struct_pb2.Struct()
        if session_claims is not None:
            session_struct.update(session_claims)

        response = self.stub.EnrichToken(
            pb2.EnrichTokenRequest(
                access_token=user_token,
                token_claims=token_struct,
                session_claims=session_struct,
            )
        )
    except Exception as exception:
        print(exception)
        return None

    if not response:
        return None

    return response
