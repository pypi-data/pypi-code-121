"""
Main interface for ivschat service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_ivschat import (
        Client,
        ivschatClient,
    )

    session = Session()
    client: ivschatClient = session.client("ivschat")
    ```
"""
from .client import ivschatClient

Client = ivschatClient


__all__ = ("Client", "ivschatClient")
