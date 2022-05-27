from typing import Any, Callable, Iterator, Tuple, TypeVar

import grpc

# based on https://github.com/grpc/grpc/blob/master/examples/python/interceptors/headers/greeter_client.py#L26
# but using the `aio` versions of the interceptors
# additional inspiration from https://github.com/alphauslabs/blue-sdk-python/tree/c3b346aeaa0fe963d70168627632c8dc5f68bd6c/alphausblue/connection
# which uses async grpc
from grpc.aio import (
    StreamStreamClientInterceptor,
    StreamUnaryClientInterceptor,
    UnaryStreamClientInterceptor,
    UnaryUnaryClientInterceptor,
)

InterceptorCallable = Callable[[Any, Any, Any, Any], Tuple[Any, Any, Any]]

# Ignoring some typing here, since the `grpc` package does not define types


class _GenericClientInterceptor(
    UnaryUnaryClientInterceptor,
    UnaryStreamClientInterceptor,
    StreamUnaryClientInterceptor,
    StreamStreamClientInterceptor,
):
    """
    Generic interceptor that covers most of the possible GRPC call types
    """

    def __init__(self, interceptor_function: InterceptorCallable):
        self._fn = interceptor_function

    async def intercept_unary_unary(self, continuation, client_call_details, request):  # type: ignore
        return await self._intercept(
            continuation, client_call_details, iter((request,)), False, False
        )

    async def intercept_unary_stream(self, continuation, client_call_details, request):  # type: ignore
        return await self._intercept(
            continuation, client_call_details, iter((request,)), False, True
        )

    async def intercept_stream_unary(  # type: ignore
        self, continuation, client_call_details, request_iterator
    ):
        return await self._intercept(
            continuation, client_call_details, request_iterator, True, False
        )

    async def intercept_stream_stream(  # type: ignore
        self, continuation, client_call_details, request_iterator
    ):
        return await self._intercept(
            continuation, client_call_details, request_iterator, True, True
        )

    async def _intercept(
        self,
        continuation: Any,
        client_call_details: Any,
        request_iterator: Iterator[Any],
        request_streaming: bool,
        response_streaming: bool,
    ) -> Any:
        """
        Actual intercept methods implementation
        """

        new_details, new_request_iterator, postprocess = self._fn(
            client_call_details, request_iterator, request_streaming, response_streaming
        )

        response_it = await continuation(
            new_details,
            new_request_iterator if request_streaming else next(new_request_iterator),
        )

        return postprocess(response_it) if postprocess else response_it


TRequest = TypeVar("TRequest")


def header_adder_interceptor(header: str, value: str) -> _GenericClientInterceptor:
    """
    Creates an interceptor object that adds a header to every GRPC call.

    @param header: Name for the header
    @param value: Value for the header
    @returns: Interceptor instance
    """

    def intercept_call(
        client_call_details: Any,
        request_iterator: Iterator[TRequest],
        request_streaming: bool,
        response_streaming: bool,
    ) -> Tuple[grpc.aio.ClientCallDetails, Iterator[TRequest], Any]:
        del request_streaming, response_streaming

        metadata = client_call_details.metadata
        if not metadata:
            metadata = grpc.aio.Metadata()

        metadata[header] = value

        client_call_details = grpc.aio.ClientCallDetails(
            client_call_details.method,
            client_call_details.timeout,
            metadata,
            client_call_details.credentials,
            client_call_details.wait_for_ready,
        )
        return client_call_details, request_iterator, None

    return _GenericClientInterceptor(intercept_call)
