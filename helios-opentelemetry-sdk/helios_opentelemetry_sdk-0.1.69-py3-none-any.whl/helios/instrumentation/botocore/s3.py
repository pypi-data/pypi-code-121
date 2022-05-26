from helios.instrumentation.base import HeliosBaseInstrumentor
from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.botocore.consts import AwsParam, AwsAttribute, AwsService


class S3Instrumentor(object):

    def __init__(self):
        pass

    def request_hook(self, span, operation_name, api_params):
        if api_params is None:
            return

        bucket = api_params.get(AwsParam.BUCKET)
        key = api_params.get(AwsParam.KEY)
        value = api_params.get(AwsParam.BODY)

        attributes = dict({
            SpanAttributes.DB_SYSTEM: AwsService.S3
        })
        if bucket:
            attributes[AwsAttribute.S3_BUCKET] = bucket
        if key:
            attributes[AwsAttribute.S3_KEY] = key
        if value and type(value) == bytes:
            HeliosBaseInstrumentor.set_payload_attribute(span, AwsAttribute.DB_QUERY_RESULT, value.decode())

        span.set_attributes(attributes)

    def response_hook(self, span, operation_name, result):
        attributes = dict({
            SpanAttributes.DB_SYSTEM: AwsService.S3
        })
        # TODO: fix how we read the body. The code below drains it and so customers get an empty body
        # https://botocore.amazonaws.com/v1/documentation/api/latest/reference/response.html#botocore.response.StreamingBody
        # body_stream = result.get(AwsParam.BODY)
        # if body_stream:
        #    HeliosBaseInstrumentor.set_payload_attribute(span, AwsAttribute.DB_QUERY_RESULT, body_stream.read())
        span.set_attributes(attributes)
