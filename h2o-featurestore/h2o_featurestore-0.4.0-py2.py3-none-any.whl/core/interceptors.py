import abc
import collections
import sys
import time
import uuid
from random import randint
from typing import *

import grpc

import featurestore

from .auth import AuthException


class _ClientCallDetails(
    collections.namedtuple(
        "_ClientCallDetails", ("method", "timeout", "metadata", "credentials")
    ),
    grpc.ClientCallDetails,
):
    pass


class AuthClientInterceptor(
    grpc.UnaryUnaryClientInterceptor, grpc.StreamUnaryClientInterceptor
):
    def __init__(self, client):
        self._client = client

    def _intercept_call(self, continuation, client_call_details, request_or_iterator):
        if client_call_details.method in (
            "/featurestore.core.CoreService/Login",
            "/featurestore.core.CoreService/GetAccessToken",
            "/featurestore.core.CoreService/GetVersion",
        ):
            return continuation(client_call_details, request_or_iterator)
        else:
            metadata = []
            if client_call_details.metadata is not None:
                metadata = list(client_call_details.metadata)
            is_success, token_or_error = self._client.auth._obtain_token()
            if is_success:
                sys.tracebacklimit = None
                metadata.append(
                    (
                        "authorization",
                        token_or_error,
                    )
                )
            else:
                sys.tracebacklimit = 0
                raise AuthException(token_or_error)
            metadata.append(("request-id", str(uuid.uuid4())))
            metadata.append(("client-version", featurestore.__version__))
            new_client_call_details = _ClientCallDetails(
                client_call_details.method,
                self._client._client_config.timeout,
                metadata,
                client_call_details.credentials,
            )
            return continuation(new_client_call_details, request_or_iterator)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(
        self, continuation, client_call_details, request_iterator
    ):
        return self._intercept_call(continuation, client_call_details, request_iterator)


class SleepingPolicy(abc.ABC):
    @abc.abstractmethod
    def sleep(self, try_i: int):
        """
        How long to sleep in milliseconds.
        :param try_i: the number of retry (starting from zero)
        """
        assert try_i >= 0


class ExponentialBackoff(SleepingPolicy):
    def __init__(self, *, init_backoff_ms: int, max_backoff_ms: int, multiplier: int):
        self.init_backoff = randint(0, init_backoff_ms)
        self.max_backoff = max_backoff_ms
        self.multiplier = multiplier

    def sleep(self, try_i: int):
        sleep_range = min(
            self.init_backoff * self.multiplier**try_i, self.max_backoff
        )
        sleep_ms = randint(0, sleep_range)
        time.sleep(sleep_ms / 1000)


class RetryOnRpcErrorClientInterceptor(
    grpc.UnaryUnaryClientInterceptor, grpc.StreamUnaryClientInterceptor
):
    def __init__(
        self,
        *,
        max_attempts: int,
        sleeping_policy: SleepingPolicy,
        status_for_retry: Optional[Tuple[grpc.StatusCode]] = None,
    ):
        self.max_attempts = max_attempts
        self.sleeping_policy = sleeping_policy
        self.status_for_retry = status_for_retry

    def _intercept_call(self, continuation, client_call_details, request_or_iterator):

        for try_i in range(self.max_attempts):
            response = continuation(client_call_details, request_or_iterator)

            if isinstance(response, grpc.RpcError):

                # Return if it was last attempt
                if try_i == (self.max_attempts - 1):
                    return response

                # If status code is not in retryable status codes
                if (
                    self.status_for_retry
                    and response.code() not in self.status_for_retry
                ):
                    return response

                self.sleeping_policy.sleep(try_i)
            else:
                return response

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(
        self, continuation, client_call_details, request_iterator
    ):
        return self._intercept_call(continuation, client_call_details, request_iterator)
