import json
from logging import getLogger
from typing import Optional, List, Dict, Union

from opentelemetry import trace
from opentelemetry.propagate import inject, extract
from opentelemetry.propagators.textmap import Setter
from opentelemetry.sdk.trace import Tracer
from opentelemetry.context import attach, detach
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace.status import Status
from opentelemetry.instrumentation.utils import http_status_to_status_code

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor

_LOG = getLogger(__name__)


class ASGISetter(Setter):

    def set(self, carrier: dict, key: str, value: str) -> None:
        """Setter implementation to add a HTTP header value to the ASGI
        scope.

        Args:
            carrier: ASGI scope object
            key: header name in scope
            value: header value
        """
        # asgi header keys are in lower case
        key = key.lower()
        headers = carrier.get("headers", [])
        carrier["headers"] = [(key.encode('utf-8'), value.encode('utf-8'))] + headers


asgi_setter = ASGISetter()


class HeliosAsgiMiddleware:

    def __init__(self, app, tracer: Optional[Tracer], get_span_details=None):
        self.app = app
        self.tracer = tracer
        self.get_span_details = get_span_details or self.get_default_span_details

    @staticmethod
    def get_default_span_details(scope: Dict):
        span_name = scope.get("path", "").strip() or "HTTP {}".format(
            scope.get("method", "").strip()
        )

        return span_name, {}

    def add_headers_to_span(self, span, response_headers):
        if response_headers is None:
            return

        try:
            current_headers = span.attributes.get(HeliosBaseHttpInstrumentor.HTTP_RESPONSE_HEADERS_ATTRIBUTE_NAME)
            if current_headers is not None:
                response_headers.update(json.loads(current_headers))

            span.set_attribute(
                HeliosBaseHttpInstrumentor.HTTP_RESPONSE_HEADERS_ATTRIBUTE_NAME,
                json.dumps(response_headers))
        except Exception:
            # Let's play it safe
            pass

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        span_name, attributes = self.get_span_details(scope)

        self.set_url_and_target(attributes, scope)
        self.set_method(attributes, scope)

        request_headers = self.extract_headers(scope.get('headers'))
        propagated_context = extract(request_headers)

        try:
            attributes[HeliosBaseHttpInstrumentor.HTTP_REQUEST_HEADERS_ATTRIBUTE_NAME] = json.dumps(request_headers)
        except Exception as error:
            _LOG.debug('asgi instrumentation __call__ error: %s.', error)

        token = attach(propagated_context)
        try:
            with self.tracer.start_as_current_span(
                    f"{span_name}", kind=trace.SpanKind.SERVER, context=propagated_context
            ) as span:
                span.set_attributes(attributes)

                async def wrapped_send(message):
                    try:
                        if 'status' in message:
                            status_code = message.get('status')
                            self.set_status_code(span, status_code) if status_code else None

                        if 'headers' in message:
                            response_headers = HeliosAsgiMiddleware.extract_headers(message.get('headers'))
                            self.add_headers_to_span(span, response_headers)

                        if 'body' in message:
                            body = message.get('body')
                            body_attr = HeliosBaseHttpInstrumentor.HTTP_RESPONSE_BODY_ATTRIBUTE_NAME
                            span.set_attribute(body_attr, body) if body is not None else None
                    except Exception as sendError:
                        _LOG.debug('asgi send instrumentation error: %s.', sendError)

                    return await send(message)

                async def wrapped_receive():
                    message = await receive()

                    try:
                        if 'status' in message:
                            status_code = message.get("status")
                            self.set_status_code(span, status_code)

                        if 'body' in message:
                            body = message.get('body')
                            body_attr = HeliosBaseHttpInstrumentor.HTTP_REQUEST_BODY_ATTRIBUTE_NAME
                            span.set_attribute(body_attr, body) if body is not None else None
                    except Exception as receiveError:
                        _LOG.debug('asgi receive instrumentation error: %s.', receiveError)

                    return message

                inject(scope, setter=asgi_setter)
                return await self.app(scope, wrapped_receive, wrapped_send)
        finally:
            detach(token)

    @staticmethod
    def extract_headers(headers: Optional[List]) -> Optional[Dict]:
        if headers is None:
            return None

        try:
            return {
                HeliosAsgiMiddleware.bytes_to_str(key): HeliosAsgiMiddleware.bytes_to_str(value)
                for (key, value) in headers
            }
        except Exception as error:
            _LOG.debug('asgi instrumentation extract_headers error: %s.', error)
            return None

    @staticmethod
    def bytes_to_str(str_or_bytes: Union[str, bytes]) -> str:
        return str_or_bytes.decode() if isinstance(str_or_bytes, bytes) else str_or_bytes

    @staticmethod
    def set_url_and_target(attributes, scope):
        url = ''
        path = ''
        try:
            protocol = scope.get('type')
            host, port = scope.get('server')
            root_path = scope.get('root_path')
            path = scope.get('path')
            port = '' if port in [80, 443] else f':{port}'
            query = scope.get('query_string')
            url_path = path
            if type(query) == bytes and len(query) > 0:
                url_path = f'{path}?{query.decode()}'

            url = f'{protocol}://{host}{port}{root_path}{url_path}'
        except Exception:
            pass
        finally:
            attributes[SpanAttributes.HTTP_URL] = url
            if len(path) > 0 and attributes.get(SpanAttributes.HTTP_TARGET) is None:
                attributes[SpanAttributes.HTTP_TARGET] = path

    @staticmethod
    def set_method(attributes, scope):
        method = ''
        try:
            method = scope.get('method', '').strip()
        except Exception:
            pass
        finally:
            attributes[SpanAttributes.HTTP_METHOD] = method

    @staticmethod
    def set_status_code(span, status_code):
        """Adds HTTP response attributes to span using the status_code argument."""
        if not span.is_recording() or not status_code:
            return

        try:
            status_code = int(status_code)
        except ValueError:
            pass
        else:
            span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, status_code)
            span.set_status(Status(http_status_to_status_code(status_code, server_span=True)))
