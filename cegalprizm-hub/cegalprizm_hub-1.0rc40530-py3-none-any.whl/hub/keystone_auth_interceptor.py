# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import collections
import grpc

from .generic_client_interceptor import create


class _ClientCallDetails(
        collections.namedtuple(
            '_ClientCallDetails',
            ('method', 'timeout', 'metadata', 'credentials')),
        grpc.ClientCallDetails):
    pass


def auth_header_interceptor(token_provider):

    def intercept_call(client_call_details, request_iterator, request_streaming,
                       response_streaming):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append((
            "authorization",
            "Bearer " + token_provider.get_access_token(),
        ))
        client_call_details = _ClientCallDetails(
            client_call_details.method, client_call_details.timeout, metadata,
            client_call_details.credentials)
        return client_call_details, request_iterator, None

    return create(intercept_call)