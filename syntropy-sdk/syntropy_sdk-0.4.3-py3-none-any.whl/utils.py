import json
import time

from urllib3.response import HTTPResponse

from syntropy_sdk import ApiClient, AuthApi, Configuration, models
from syntropy_sdk.exceptions import *

TAKE_MAX_ITEMS_PER_CALL = 100
MAX_PAYLOAD_SIZE = 99 * 1024
MAX_QUERY_FIELD_SIZE = 2 * 1024

ALLOWED_NETWORK_TOPOLOGIES = (
    "P2P",
    "P2M",
    "MESH",
)


class WithRetry:
    """Call api method several times in case of an error. Implements exponential back-off without jitter.

    Example:
        WithRetry(auth_api.login)("username", "password")
    """

    def __init__(self, func, retry_count=7, base=15, exponent=1, cap=180):
        self.func = func
        self.retry_count = retry_count
        self.base = base
        self.exponent = exponent
        self.cap = cap

    def __call__(self, *args, **kwargs):
        for attempt in range(self.retry_count):
            try:
                return self.func(*args, **kwargs)
            except ApiException as err:
                if err.status not in (500, 502, 503, 504, 408, 429):
                    raise
                # NOTE: This check is specifically for attempting to create connections just after the network was created.
                # In such a case the network ID is returned by the create_network api call, however, it is not yet being seen
                # by subsequent create_connections call if it is made too quickly.
                if err.status == 400 and attempt:
                    raise
                if attempt >= self.retry_count - 1:
                    raise
                delay = min(self.cap, self.base * 2 ** (attempt * self.exponent))
                time.sleep(delay)


class WithPagination:
    """Call api method to retrieve as many times as is necessary to get up to `take` entries.

    NOTE: If `take` parameter is not provided, then this helper will retrieve all available entries.

    TODO: This implementation disregards HTTP headers that contain pagination information and therefore
    sometimes it will make an additional request beyound the total data. This request should return
    an empty result and this will be used as a stop signal.
    This behavior should be amended so that HTTP headers would be used to determine the total number of
    entries available. Currently, regular api methods overwrite `_return_http_data_only` kwarg, thus
    `*_with_http_info` methods should be used instead.

    Example:
        WithPagination(platform_api.platform_agent_index)(skip=10, take=10000)
    """

    def __init__(self, func, max_take=TAKE_MAX_ITEMS_PER_CALL):
        self.func = func
        self.max_take = max_take

    def __call__(self, *args, **kwargs):
        take = kwargs.pop("take", 0)
        skip = kwargs.pop("skip", 0)
        take = take if take else None
        skip = skip if skip else 0

        result = {"data": []}
        take_now = self.max_take
        while True:
            if take is not None:
                take_now = min(take_now, take)
                if take_now <= 0:
                    break
            call_result = self.func(*args, skip=skip, take=take_now, **kwargs)

            call_result = deserialize_result(call_result)

            if call_result["data"]:
                result["data"] += call_result["data"]

            if len(call_result["data"]) < take_now:
                break
            if take is not None:
                take -= take_now
            skip += self.max_take

        return result


def _default_translator(field):
    def translator(body, data):
        if data is None:
            return body[field]
        else:
            return {
                **body,
                field: data,
            }

    return translator


class BatchedRequest:
    """Executes requests in batches in order to circumvent payload/field size limit.
    Assumes that the batchable parameter is a list/tuple and api call returns a list.

    Translator must be provided for requests that have "body" as a kwarg. The translator
    is a callable that accepts the body as first argument and batch data as the second argument.
    It must return the list if the second argument is None and the payload body otherwise.
    It must not modify the body.

    Example translator:
        def translator(body, data):
            if data is None:
                return body["data"]
            else:
                return {
                    **body,
                    "data": data,
                }

    Example usage:
        BatchedRequest(
            api.update_connection_services,
            max_payload_size=MAX_PAYLOAD_SIZE,
            translator=_default_translator("changes"),
        )(body=body)
    """

    def __init__(
        self,
        func,
        max_payload_size,
        translator=_default_translator("data"),
    ):
        self.func = func
        self.max_payload_size = max_payload_size
        self.translator = translator

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def _calculate_payload_size(self, data):
        if isinstance(data, list):
            return len(",".join(str(i) for i in data))
        else:
            return len(json.dumps(data))

    def _determine_batch_size(self, body, data, batch_size):
        while batch_size:
            data = data[:batch_size]
            batch = self.translator(body, data) if body is not None else data
            if self._calculate_payload_size(batch) > self.max_payload_size:
                batch_size //= 2
            else:
                return batch_size, batch
        raise SyntropyError("Batch size could not be determined")

    def _generate_batches(self, body, data):
        batch_size = len(data)
        while data:
            batch_size, batch = self._determine_batch_size(body, data, batch_size)
            data = data[batch_size:]
            yield batch

    def _call(self, body, data, *args, **kwargs):
        result = []
        for batch in self._generate_batches(body, data):
            # TODO: What to do with errors in result?
            func = WithRetry(self.func)
            if body is None:
                response = func(batch, *args, **kwargs)
            else:
                response = func(body=batch, *args, **kwargs)
            response = deserialize_result(response)
            if isinstance(response, dict) and "data" in response:
                result += response["data"]
            else:
                result.append(response)
        # NOTE: Undesirable side effect: will transform non-list responses to {"data": data}
        return {"data": result}


class BatchedRequestBody(BatchedRequest):
    def __init__(
        self,
        func,
        max_payload_size,
        translator=_default_translator("data"),
    ):
        super().__init__(func, max_payload_size, translator=translator)

    def __call__(self, *args, **kwargs):
        body = kwargs.pop("body")
        data = self.translator(body, None)
        return self._call(body, data, *args, **kwargs)


class BatchedRequestQuery(BatchedRequest):
    def __init__(
        self,
        func,
        max_query_size,
    ):
        super().__init__(func, max_query_size)

    def __call__(self, *args, **kwargs):
        query = args[0]
        args = args[1:]
        return self._call(None, query, *args, **kwargs)


class BatchedRequestFilter(BatchedRequest):
    def __init__(
        self,
        func,
        max_query_size,
        filter_data=None,
    ):
        """Generates as many requests as needed in order to query
        data using filters in such a way so that the filter query string
        does not exceed max_query_size limit.

        Args:
            func (_type_): A function to use for the query.
            max_query_size (_type_): maximum size of the query string.
            filter_data (_type_): an additional list of filter items.
        """
        super().__init__(func, max_query_size)
        self.filter_data = filter_data if filter_data is not None else []

    def _build_query(self, data):
        return ",".join(str(i) for i in data)

    def _calculate_payload_size(self, data):
        return len(self._build_query(data))

    def __call__(self, *args, **kwargs):
        result = []
        filter = self.filter_data
        if "filter" in kwargs:
            filter += kwargs["filter"]
            del kwargs["filter"]

        for batch in self._generate_batches(None, filter):
            func = WithRetry(self.func)

            filter_batch = self._build_query(batch)
            response = func(filter=filter_batch, *args, **kwargs)
            response = deserialize_result(response)
            if isinstance(response, dict) and "data" in response:
                result += response["data"]
            else:
                result.append(response)
        # NOTE: Undesirable side effect: will transform non-list responses to {"data": data}
        return {"data": result}


def deserialize_result(call_result):
    if isinstance(call_result, HTTPResponse):
        # fetch data from response object
        call_result = json.loads(call_result.data)
    elif hasattr(call_result, "to_dict"):
        call_result = call_result.to_dict()  # FIXME: This is for compatibility
    return call_result


def login_with_access_token(api_url, access_token):
    """Exchange access token retrieved from the Platform for JWT access token.
    JWT access token can be used to make Platform API calls.
    """
    config = Configuration()
    config.host = api_url
    api = ApiClient(config)
    auth = AuthApi(api)

    body = models.V1NetworkAuthAccessTokenLoginRequest(access_token=access_token)
    try:
        response = auth.v1_network_auth_access_token_login(body)
        return response.data.access_token
    finally:
        del auth
        del api
