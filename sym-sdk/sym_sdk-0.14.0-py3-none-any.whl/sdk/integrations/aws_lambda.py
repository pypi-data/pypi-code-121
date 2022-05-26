"""Methods for invoking AWS Lambda functions."""

from typing import Any, Optional

from sym.sdk.exceptions.aws import AWSLambdaError  # noqa


def invoke(arn: str, payload: Optional[dict] = None) -> Any:
    """
    Synchronously invokes an AWS Lambda function.
    Returns the JSON-deserialized object returned by the lambda

    Args:
        arn: The ARN of the Lambda function to invoke.
        payload: A dict of JSON-serializable data to pass to the function.
    """


def invoke_async(arn: str, payload: Optional[dict] = None) -> bool:
    """
    Asynchronously invokes an AWS Lambda function.
    Note that this method simply returns a boolean indicating success enqueuing the invocation.

    Args:
        arn: The ARN of the Lambda function to invoke.
        payload: A dict of JSON-serializable data to pass to the function.
    """
