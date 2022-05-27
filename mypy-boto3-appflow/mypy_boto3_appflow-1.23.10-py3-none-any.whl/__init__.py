"""
Main interface for appflow service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_appflow import (
        AppflowClient,
        Client,
    )

    session = Session()
    client: AppflowClient = session.client("appflow")
    ```
"""
from .client import AppflowClient

Client = AppflowClient


__all__ = ("AppflowClient", "Client")
