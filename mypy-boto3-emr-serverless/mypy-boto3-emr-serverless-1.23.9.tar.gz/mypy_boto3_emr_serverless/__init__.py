"""
Main interface for emr-serverless service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_emr_serverless import (
        Client,
        EMRServerlessWebServiceClient,
        ListApplicationsPaginator,
        ListJobRunsPaginator,
    )

    session = Session()
    client: EMRServerlessWebServiceClient = session.client("emr-serverless")

    list_applications_paginator: ListApplicationsPaginator = client.get_paginator("list_applications")
    list_job_runs_paginator: ListJobRunsPaginator = client.get_paginator("list_job_runs")
    ```
"""
from .client import EMRServerlessWebServiceClient
from .paginator import ListApplicationsPaginator, ListJobRunsPaginator

Client = EMRServerlessWebServiceClient


__all__ = (
    "Client",
    "EMRServerlessWebServiceClient",
    "ListApplicationsPaginator",
    "ListJobRunsPaginator",
)
