# -*- coding: utf-8 -*-

"""
Manage the underlying boto3 session and client.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Union, TYPE_CHECKING

import boto3

if TYPE_CHECKING:  # pragma: no cover
    import botocore.session
    from botocore.client import BaseClient
    from boto3.resources.base import ServiceResource

from .services import AwsServiceEnum


class BotoSesManager:
    """
    Boto3 session and client manager that use cache to create low level client.

    .. note::

        boto3.session.Session is a static object that won't talk to AWS endpoint.
        also session.client("s3") won't talk to AWS endpoint right away. The
        authentication only happen when a concrete API request called.

    .. versionadded:: 0.0.1

    .. versionadded:: 0.0.4

        add ``default_client_kwargs`` arguments that set default keyword
        arguments for ``boto3.session.Session.client`` method.
    """

    def __init__(
        self,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_session_token: str = None,
        region_name: str = None,
        botocore_session: "botocore.session.Session" = None,
        profile_name: str = None,
        default_client_kwargs: dict = None,
        expiration_time: datetime = datetime(2100, 1, 1, tzinfo=timezone.utc),
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.region_name = region_name
        self.botocore_session = botocore_session
        self.profile_name = profile_name
        self.expiration_time: datetime = expiration_time
        if default_client_kwargs is None:
            default_client_kwargs = dict()
        self.default_client_kwargs = default_client_kwargs

        self._boto_ses_cache: Optional[boto3.session.Session] = None
        self._client_cache: Dict[str, "BaseClient"] = dict()
        self._resource_cache: Dict[str, "ServiceResource"] = dict()
        self._aws_account_id_cache: Optional[str] = None
        self._aws_region_cache: Optional[str] = None

    @property
    def boto_ses(self) -> boto3.session.Session:
        """
        Get boto3 session from metadata.

        .. versionadded:: 1.0.2
        """
        if self._boto_ses_cache is None:
            self._boto_ses_cache = boto3.session.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token,
                region_name=self.region_name,
                botocore_session=self.botocore_session,
                profile_name=self.profile_name,
            )
        return self._boto_ses_cache

    @property
    def aws_account_id(self) -> str:
        """
        Get current aws account id of the boto session

        .. versionadded:: 1.0.1
        """
        if self._aws_account_id_cache is None:
            sts_client = self.get_client(AwsServiceEnum.STS)
            self._aws_account_id_cache = sts_client.get_caller_identity()["Account"]
        return self._aws_account_id_cache

    @property
    def aws_region(self) -> str:
        """
        Get current aws region of the boto session

        .. versionadded:: 0.0.1
        """
        if self._aws_region_cache is None:
            self._aws_region_cache = self.boto_ses.region_name
        return self._aws_region_cache

    def get_client(
        self,
        service_name: str,
        region_name: str = None,
        api_version: str = None,
        use_ssl: bool = True,
        verify: Union[bool, str] = None,
        endpoint_url: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_session_token: str = None,
        config=None,
    ) -> "BaseClient":
        """
        Get aws boto client using cache.

        .. versionadded:: 0.0.1

        .. versionchanged:: 0.0.3

            add additional keyword arguments pass to
            ``boto3.session.Session.client()`` method.
        """
        try:
            return self._client_cache[service_name]
        except KeyError:
            client_kwargs = dict(
                region_name=region_name,
                api_version=api_version,
                use_ssl=use_ssl,
                verify=verify,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                config=config,
            )
            client_kwargs = {k: v for k, v in client_kwargs.items() if v is not None}
            kwargs = dict(self.default_client_kwargs)
            if self.default_client_kwargs:
                kwargs.update(client_kwargs)
            client = self.boto_ses.client(service_name, **kwargs)
            self._client_cache[service_name] = client
            return client

    def get_resource(
        self,
        service_name: str,
        region_name: str = None,
        api_version: str = None,
        use_ssl: bool = True,
        verify: Union[bool, str] = None,
        endpoint_url: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_session_token: str = None,
        config=None,
    ) -> "ServiceResource":
        """
        Get aws boto service resource using cache

        .. versionadded:: 0.0.2

        .. versionchanged:: 0.0.3

            add additional keyword arguments pass to
            ``boto3.session.Session.resource()`` method.
        """
        try:
            return self._resource_cache[service_name]
        except KeyError:
            resource_kwargs = dict(
                region_name=region_name,
                api_version=api_version,
                use_ssl=use_ssl,
                verify=verify,
                endpoint_url=endpoint_url,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                config=config,
            )
            resource_kwargs = {
                k: v for k, v in resource_kwargs.items() if v is not None
            }
            kwargs = dict(self.default_client_kwargs)
            if self.default_client_kwargs:
                kwargs.update(resource_kwargs)
            resource = self.boto_ses.resource(service_name, **kwargs)
            self._resource_cache[service_name] = resource
            return resource

    def assume_role(
        self,
        role_arn: str,
        role_session_name: str = None,
        duration_seconds: int = 3600,
        tags: list = None,
        transitive_tag_keys: list = None,
        external_id: str = None,
        mfa_serial_number: str = None,
        mfa_token: str = None,
        source_identity: str = None,
    ) -> "BotoSesManager":
        """
        Assume an IAM role, create another :class`BotoSessionManager` and return.

        .. versionadded:: 0.0.1
        """
        if role_session_name is None:
            role_session_name = uuid.uuid4().hex
        kwargs = {
            k: v
            for k, v in dict(
                RoleArn=role_arn,
                RoleSessionName=role_session_name,
                DurationSeconds=duration_seconds,
                Tags=tags,
                TransitiveTagKeys=transitive_tag_keys,
                external_id=external_id,
                SerialNumber=mfa_serial_number,
                TokenCode=mfa_token,
                SourceIdentity=source_identity,
            ).items()
            if v is not None
        }
        sts_client = self.get_client(AwsServiceEnum.STS)
        res = sts_client.assume_role(**kwargs)
        expiration_time = res["Credentials"]["Expiration"]
        bsm = self.__class__(
            aws_access_key_id=res["Credentials"]["AccessKeyId"],
            aws_secret_access_key=res["Credentials"]["SecretAccessKey"],
            aws_session_token=res["Credentials"]["SessionToken"],
            expiration_time=expiration_time,
            default_client_kwargs=self.default_client_kwargs,
        )
        return bsm

    def is_expired(self) -> bool:
        """
        Check if this boto session is expired.

        .. versionadded:: 0.0.1
        """
        return datetime.utcnow().replace(tzinfo=timezone.utc) >= self.expiration_time
