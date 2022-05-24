from __future__ import absolute_import
from copy import deepcopy
from typing import List, Dict, Union, Any, Optional, BinaryIO
from datetime import datetime

from .countries_cache import CountriesCache
from .crypto_utils import (
    hash_object_record_keys,
    normalize_object_record_keys,
    decrypt_record,
    encrypt_record,
    get_salted_hash,
    normalize_key,
)
from .exceptions import (
    StorageCryptoException,
    StorageConfigValidationException,
    SecretsValidationException,
)
from .incountry_crypto import InCrypto
from .http_client import HttpClient
from .models import (
    AttachmentCreate,
    AttachmentMetaUpdate,
    AttachmentRequest,
    BatchDeleteFilter,
    Country,
    CustomEncryptionValidation,
    FindFilter,
    FindFilterNonHashed,
    FIND_LIMIT,
    Record,
    RecordNonHashed,
    RecordRaw,
    RecordListForBatch,
    RecordListNonHashedForBatch,
    RecordListRawForBatch,
    RequestOptions,
    SortFilter,
    StorageWithEnv,
    StorageOptions,
    SecretsValidation,
    EncryptionType,
)
from .secret_key_accessor import SecretKeyAccessor
from .token_clients import StaticTokenClient, OAuthTokenClient
from .types import TDebugHTTPResponse, TIntFilter, TStringFilter, TRecord, TSortFilter
from .validation import validate_model, validate_lambda


class Storage:
    HTTP_DEBUG_KEY = "http_response"

    @validate_model(
        {"model": StorageWithEnv, "validation_exception": StorageConfigValidationException},
        {"model": SecretsValidation, "validation_exception": SecretsValidationException},
        {"model": CustomEncryptionValidation, "validation_exception": StorageConfigValidationException},
    )
    def __init__(
        self,
        environment_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        oauth_token: Optional[str] = None,
        endpoint: Optional[str] = None,
        debug: Optional[bool] = False,
        options: Optional[Dict[str, Any]] = {},
        encrypt: Optional[Union[bool, str]] = EncryptionType.LOCAL,
        secret_key_accessor: Optional[SecretKeyAccessor] = None,
        custom_encryption_configs: Optional[List[dict]] = None,
    ):
        """Returns a client to talk to the InCountry storage network.

        Args:
            environment_id:
                The id of the environment you want to store records in. Defaults to None.
                Can also be set via INC_ENVIRONMENT_ID environment variable.
            client_id:
                Client Id used for oAuth authorization. Defaults to None.
                Can also be set via INC_CLIENT_ID environment variable.
            client_secret:
                Client Secret used for oAuth authorization. Defaults to None.
                Can also be set via INC_CLIENT_SECRET environment variable.
            oauth_token:
                OAuth token acquired prior to Storage initialization.
                Mutually exclusive with client_id, client_secret.
            endpoint:
                Custom storage server endpoint to use. Defaults to None.
                Can also be set via INC_ENDPOINT environment variable.
            encrypt:
                Switch encryption modes:
                    EncryptionType.LOCAL - Enables encryption using SDK
                    EncryptionType.SSE - Enables the server side encryption (SSE) mode
                    EncryptionType.OFF - Disables SDK decryption and sends base64 encoded data
                Also supports boolean values as backward compatibility:
                    True = EncryptionType.LOCAL
                    False = EncryptionType.OFF
            secret_key_accessor:
                SecretKeyAccessor class instance which provides encryption keys details. Defaults to None.
            custom_encryption_configs:
                List of custom encryption configurations. Defaults to None.
            debug:
                Pass True to enable some debug logging. Defaults to False.
            options:
                Options dict to tweak various Storage instance aspects. Defaults to {}.

        Raises:
            StorageClientException: in case constructor param validation fails,
            StorageCryptoException: in case any encryption-related error occurs.
            StorageException: in any other cases
        """

        self.debug = debug
        self.env_id = environment_id
        self.options = StorageOptions(**options)
        self.encrypt = encrypt

        if self.encrypt == EncryptionType.LOCAL:
            self.crypto = InCrypto(secret_key_accessor, custom_encryption_configs)
        elif self.encrypt == EncryptionType.OFF:
            self.crypto = InCrypto()

        if oauth_token is not None:
            token_client = StaticTokenClient(token=oauth_token)
        else:
            token_client = OAuthTokenClient(
                client_id=client_id,
                client_secret=client_secret,
                scope=self.env_id,
                auth_endpoints=self.options.auth_endpoints,
                options=self.options.http_options,
                debug=self.debug,
            )
        self.http_client = HttpClient(
            env_id=self.env_id,
            token_client=token_client,
            endpoint=endpoint,
            debug=self.debug,
            endpoint_mask=self.options.endpoint_mask,
            countries_cache=CountriesCache(
                countries_endpoint=self.options.countries_endpoint, options=self.options.http_options
            ),
            server_side_encryption=self.encrypt == EncryptionType.SSE,
            options=self.options.http_options,
        )

    @validate_model(
        Country,
        RequestOptions,
        {
            "model": Record,
            "condition": lambda instance: instance.is_option_enabled("hash_search_keys") is True
            and instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordNonHashed,
            "condition": lambda instance: instance.is_option_enabled("hash_search_keys") is False
            and instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordRaw,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def write(
        self, country: str, record_key: str, request_options: dict = {}, **record_data: Union[str, int]
    ) -> Dict[str, TRecord]:
        """Writes record to InCountry storage network.

        Args:
            country: Country to write record to
            record_key: Record primary key/identifier
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}
            **record_data: Various record attributes.
                Available String attributes:
                - body, precommit_body, profile_key, service_key1, service_key2, key1, ..., key20.
                Available Int attributes:
                - range_key1, ..., range_key10

        Returns:
            Dict[str, TRecord]:
                A dict with record data you just wrote {"record": {"record_key": record_key, **record}}

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error.
            StorageCryptoException: in case any encryption-related error occurs.
            StorageException: in any other cases.
        """
        record_to_send = self.prepare_outbound_record({"record_key": record_key, **record_data})
        (data, http_response) = self.http_client.write(
            country=country, data=record_to_send, request_options=request_options
        )
        res = {"record": self.process_inbound_record(data)}
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        RequestOptions,
        {
            "model": RecordListForBatch,
            "condition": lambda instance: instance.is_option_enabled("hash_search_keys") is True
            and instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordListNonHashedForBatch,
            "condition": lambda instance: instance.is_option_enabled("hash_search_keys") is False
            and instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordListRawForBatch,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def batch_write(self, country: str, records: List[TRecord], request_options: dict = {}) -> Dict[str, List[TRecord]]:
        """Writes multiple records to InCountry storage network.

        Args:
            country: Country to write records to
            records: List of records. See Storage.write() for details on record attributes
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, List[TRecord]]:
                A dict with record data you just wrote {"record": {"record_key": record_key, **record}}

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error.
            StorageCryptoException: in case any encryption-related error occurs.
            StorageException: in any other cases.
        """
        records_to_send = [self.prepare_outbound_record(record) for record in records]
        data_to_send = {"records": records_to_send}
        (data, http_response) = self.http_client.batch_write(
            country=country, data=data_to_send, request_options=request_options
        )

        res = {"records": [self.process_inbound_record(r) for r in data["records"]]}
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        RequestOptions,
        {
            "model": Record,
            "condition": lambda instance: instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordRaw,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def read(self, country: str, record_key: str, request_options: dict = {}) -> Dict[str, TRecord]:
        """Reads record for the given record_key

        Args:
            country: Country to search record in
            record_key: Record primary key/identifier
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, TRecord]:
                A dict with record data {"record": TRecord}

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error
                (e.g. if record does not exist for the given record_key).
            StorageCryptoException: in case any encryption-related error occurs.
            StorageException: in any other cases.
        """
        record_key_to_send = self.prepare_record_key(record_key)
        (data, http_response) = self.http_client.read(
            country=country, record_key=record_key_to_send, request_options=request_options
        )

        res = {"record": self.process_inbound_record(data)}
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        SortFilter,
        RequestOptions,
        {
            "model": FindFilter,
            "condition": lambda instance: instance.is_option_enabled("hash_search_keys") is True,
        },
        {
            "model": FindFilterNonHashed,
            "condition": lambda instance: instance.is_option_enabled("hash_search_keys") is False
            or instance.encrypt == EncryptionType.SSE,
        },
    )
    def find(
        self,
        country: str,
        limit: Optional[int] = FIND_LIMIT,
        offset: Optional[int] = 0,
        sort: Optional[List[TSortFilter]] = None,
        request_options: dict = {},
        **filters: Union[TIntFilter, TStringFilter],
    ) -> Dict[str, Any]:
        """Finds records that satisfy provided filters

        Args:
            country: Country to search records in
            limit: Maximum amount of records to be returned. Max limit is 100. Defaults to 100.
            offset: Search offset. Should be non-negative int. Defaults to 0.
            sort: Sort filter.
                An array of single-key dicts allowing to sort result data, e.g:
                [{"key1": "asc"}, {"key2": "desc"}]
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}
            **filters: Various filters to tweak the search query.
                Available String filter keys:
                - profile_key, service_key1, service_key2, key1, ..., key20.
                Available String filter types:
                - single value: Storage.find(..., key1="v1"),
                - list of values: Storage.find(..., key1=["v1", "v2"]),
                - with $not operator: Storage.find(..., key1={"$not": "v1"}, key2={"$not":["v1", "v2"]}).

                Available Int filter keys:
                - version, range_key1, ..., range_key10.
                Available Int filter types:
                - single value: Storage.find(..., range_key1=1),
                - list of values: Storage.find(..., range_key1=[1, 2]),
                - with $not operator: Storage.find(..., range_key1={"$not": 1}, range_key2={"$not":[1, 2]}),
                - with $gt operator: Storage.find(..., range_key1={"$gt": 1}),
                - with $gte operator: Storage.find(..., range_key1={"$gte": 1}),
                - with $lt operator: Storage.find(..., range_key1={"$lt": 1}),
                - with $lte operator: Storage.find(..., range_key1={"$lte": 1}),
                - with comparison operators combination: Storage.find(..., range_key1={"$gt": 1, $lte": 10}),

        Returns:
            Dict[str, Any]:
                Found records with some meta information and errors data (if any) as dict:
                    {
                        "meta": {
                            "count": int,
                            "limit": int,
                            "offset": int,
                            "total": int,
                        },
                        "records": List[TRecord],
                        "errors": List,
                    }

                In case of any error occurs during records decryption, method will not raise StorageCryptoException
                but rather add raw record and the exception itself to "errors" list in reponse dict
                ({"errors": [..., {"rawData": TRecord, "error": StorageCryptoException}]})

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error.
            StorageException: in any other cases.
        """
        filters = self.prepare_outbound_filters(filters)

        options = {"limit": limit, "offset": offset}

        if sort is not None and len(sort) > 0:
            options["sort"] = sort

        (data, http_response) = self.http_client.find(
            country=country, data={"filter": filters, "options": options}, request_options=request_options
        )

        decoded_records = []
        undecoded_records = []
        for record in data["data"]:
            try:
                decoded_records.append(self.process_inbound_record(record))
            except StorageCryptoException as error:
                undecoded_records.append({"rawData": record, "error": error})

        res = {
            "meta": data["meta"],
            "records": decoded_records,
        }
        if len(undecoded_records) > 0:
            res["errors"] = undecoded_records
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        SortFilter,
        RequestOptions,
        {
            "model": FindFilter,
            "condition": lambda instance: instance.is_option_enabled("hash_search_keys") is True,
        },
        {
            "model": FindFilterNonHashed,
            "condition": lambda instance: instance.is_option_enabled("hash_search_keys") is False
            or instance.encrypt == EncryptionType.SSE,
        },
    )
    def find_one(
        self,
        country: str,
        offset: Optional[int] = 0,
        sort: Optional[List[TSortFilter]] = None,
        request_options: dict = {},
        **filters: Union[TIntFilter, TStringFilter],
    ) -> Union[None, Dict[str, Dict]]:
        """Finds record that satisfies provided filters

        Args:
            country: Country to search record in
            offset: Search offset. Should be non-negative int. Defaults to 0.
            sort: Sort filter.
                An array of single-key dicts allowing to sort result data, e.g:
                [{"key1": "asc"}, {"key2": "desc"}]
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}
            **filters: Various filters to tweak the search query.
                Available String filter keys:
                - profile_key, service_key1, service_key2, key1, ..., key20,
                - search_keys - for partial match search on key1, ..., key20.
                Available String filter types:
                - single value: Storage.find_one(..., key1="v1"),
                - list of values: Storage.find_one(..., key1=["v1", "v2"]),
                - with $not operator: Storage.find_one(..., key1={"$not": "v1"}, key2={"$not":["v1", "v2"]}).

                Available Int filter keys:
                - version, range_key1, ..., range_key10.
                Available Int filter types:
                - single value: Storage.find_one(..., range_key1=1),
                - list of values: Storage.find_one(..., range_key1=[1, 2]),
                - with $not operator: Storage.find_one(..., range_key1={"$not": 1}, range_key2={"$not":[1, 2]}),
                - with $gt operator: Storage.find_one(..., range_key1={"$gt": 1}),
                - with $gte operator: Storage.find_one(..., range_key1={"$gte": 1}),
                - with $lt operator: Storage.find_one(..., range_key1={"$lt": 1}),
                - with $lte operator: Storage.find_one(..., range_key1={"$lte": 1}),
                - with comparison operators combination: Storage.find_one(..., range_key1={"$gt": 1, $lte": 10}).

        Returns:
            Union[None, Dict[str, Dict]]:
                Found record (if any) or None:
                    {
                        "record": TRecord,
                    }

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error.
            StorageException: in any other cases.
        """

        find_res = self.find(
            country=country, limit=1, offset=offset, sort=sort, request_options=request_options, **filters
        )

        res = {"record": find_res["records"][0] if len(find_res["records"]) else None}
        if self.debug:
            return self.add_http_response_debug(res, find_res[Storage.HTTP_DEBUG_KEY])
        return res if res["record"] else None

    @validate_model(
        Country,
        RequestOptions,
        {
            "model": Record,
            "condition": lambda instance: instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordRaw,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def delete(self, country: str, record_key: str, request_options: dict = {}) -> Dict[str, bool]:
        """Deletes record for the given record_key

        Args:
            country:  Country to search record in
            record_key: Record primary key/identifier
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, bool]:
                {"success": True} in case the record is successfully deleted

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error
                (e.g. if record does not exist for the given record_key).
            StorageException: in any other cases.
        """

        record_key_to_send = self.prepare_record_key(record_key)
        (_, http_response) = self.http_client.delete(
            country=country, record_key=record_key_to_send, request_options=request_options
        )

        res = {"success": True}
        return self.add_http_response_debug(res, http_response)

    @validate_model(Country, RequestOptions, BatchDeleteFilter)
    def batch_delete(self, country: str, record_key: List[str], request_options: dict = {}) -> Dict[str, bool]:
        """Deletes records for the given list of 'record_key's

        Args:
            country:  Country to search record in
            record_key: List of record primary keys
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, bool]:
                {"success": True} in case records are successfully deleted

        Raises:
            StorageClientException: in case method param validation fails.
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error
                (e.g. if record does not exist for one of the given 'record_key's).
            StorageException: in any other cases.
        """
        filters = self.prepare_outbound_filters({"record_key": record_key})

        (_, http_response) = self.http_client.batch_delete(
            country=country, data={"filter": filters}, request_options=request_options
        )

        res = {"success": True}
        return self.add_http_response_debug(res, http_response)

    @validate_lambda(
        lambda instance: instance.encrypt == EncryptionType.LOCAL,
        "This method is only allowed with encryption enabled",
    )
    @validate_model(Country, RequestOptions, FindFilter)
    def migrate(self, country: str, limit: Optional[int] = FIND_LIMIT, request_options: dict = {}) -> Dict[str, int]:
        """Migrates records in InCountry storage to the latest encryption key.

        Unavailable when encrypt=False is passed to Storage constructor

        Args:
            country: Country to migrate records in
            limit: Maximum amount of records to be migrated at once. Max limit is 100. Defaults to 100
            request_options: Requst options
                Available options:
                - "http_headers", e.g. {"http_headers": {"request-id": "<uuid>"}}

        Returns:
            Dict[str, int]:
                Migration result - total amount of successfully migrated records and total records left to migrate
                (total records left with other encryption key versions):
                {
                    "migrated": int,
                    "total_left": int,
                }

        Raises:
            StorageClientException: in case method param validation fails (or in case encryption is disabled).
            StorageServerException: in case InCountry server (either storage server or auth server) responds with error
                (e.g. if record does not exist for the given record_key).
            StorageException: in any other cases.
        """
        current_secret_version = self.crypto.get_current_secret_version()
        find_res = self.find(
            country=country, limit=limit, version={"$not": current_secret_version}, request_options=request_options
        )
        records_to_migrate_count = len(find_res["records"])

        batch_write_res = None

        if records_to_migrate_count > 0:
            batch_write_res = self.batch_write(
                country=country, records=find_res["records"], request_options=request_options
            )

        res = {
            "migrated": records_to_migrate_count,
            "total_left": find_res["meta"]["total"] - records_to_migrate_count,
        }
        if "errors" in find_res:
            res["errors"] = find_res["errors"]

        if not self.debug:
            return res

        return self.add_http_response_debug(
            res,
            [find_res[Storage.HTTP_DEBUG_KEY], batch_write_res[Storage.HTTP_DEBUG_KEY]]
            if batch_write_res
            else [find_res[Storage.HTTP_DEBUG_KEY]],
        )

    @validate_model(Country, RequestOptions)
    def health_check(
        self,
        country: str,
        request_options: dict = {},
    ) -> Dict[str, bool]:
        (data, http_response) = self.http_client.health_check(
            country=country,
            request_options=request_options,
        )

        res = {"result": data}
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        RequestOptions,
        AttachmentCreate,
        {
            "model": Record,
            "condition": lambda instance: instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordRaw,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def add_attachment(
        self,
        country: str,
        record_key: str,
        file: Union[BinaryIO, str],
        mime_type: str = None,
        upsert: bool = False,
        request_options: dict = {},
    ) -> Dict[str, Union[str, int, datetime]]:
        record_key_to_send = self.prepare_record_key(record_key)
        (data, http_response) = self.http_client.add_attachment(
            country=country,
            record_key=record_key_to_send,
            file=file,
            upsert=upsert,
            mime_type=mime_type,
            request_options=request_options,
        )

        res = {"attachment_meta": data}
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        RequestOptions,
        AttachmentRequest,
        {
            "model": Record,
            "condition": lambda instance: instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordRaw,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def get_attachment_file(
        self, country: str, record_key: str, file_id: str, request_options: dict = {}
    ) -> Dict[str, Dict]:
        record_key_to_send = self.prepare_record_key(record_key)
        (data, http_response) = self.http_client.get_attachment_file(
            country=country, record_key=record_key_to_send, file_id=file_id, request_options=request_options
        )

        res = {
            "attachment_data": data,
        }
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        RequestOptions,
        AttachmentRequest,
        {
            "model": Record,
            "condition": lambda instance: instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordRaw,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def get_attachment_meta(
        self, country: str, record_key: str, file_id: str, request_options: dict = {}
    ) -> Dict[str, Union[str, int, datetime]]:
        record_key_to_send = self.prepare_record_key(record_key)
        (data, http_response) = self.http_client.get_attachment_meta(
            country=country, record_key=record_key_to_send, file_id=file_id, request_options=request_options
        )

        res = {"attachment_meta": data}
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        RequestOptions,
        AttachmentRequest,
        AttachmentMetaUpdate,
        {
            "model": Record,
            "condition": lambda instance: instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordRaw,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def update_attachment_meta(
        self,
        country: str,
        record_key: str,
        file_id: str,
        filename: str = None,
        mime_type: str = None,
        request_options: dict = {},
    ) -> Dict[str, Union[str, int, datetime]]:
        record_key_to_send = self.prepare_record_key(record_key)
        meta = {}
        if filename is not None:
            meta["filename"] = filename
        if mime_type is not None:
            meta["mime_type"] = mime_type
        (data, http_response) = self.http_client.update_attachment_meta(
            country=country, record_key=record_key_to_send, file_id=file_id, meta=meta, request_options=request_options
        )

        res = {"attachment_meta": data}
        return self.add_http_response_debug(res, http_response)

    @validate_model(
        Country,
        RequestOptions,
        AttachmentRequest,
        {
            "model": Record,
            "condition": lambda instance: instance.encrypt != EncryptionType.SSE,
        },
        {
            "model": RecordRaw,
            "condition": lambda instance: instance.encrypt == EncryptionType.SSE,
        },
    )
    def delete_attachment(
        self, country: str, record_key: str, file_id: str, request_options: dict = {}
    ) -> Dict[str, bool]:
        record_key_to_send = self.prepare_record_key(record_key)
        (_, http_response) = self.http_client.delete_attachment(
            country=country, record_key=record_key_to_send, file_id=file_id, request_options=request_options
        )

        res = {"success": True}
        return self.add_http_response_debug(res, http_response)

    ###########################################
    # Common functions
    ###########################################
    def add_http_response_debug(
        self,
        data: dict,
        http_response_data: TDebugHTTPResponse,
    ) -> dict:
        if self.debug:
            data[Storage.HTTP_DEBUG_KEY] = http_response_data
        return data

    def log(self, *args):
        if self.debug:
            print("[incountry] ", args)

    def is_option_enabled(self, option):
        return getattr(self.options, option, None) is True

    def prepare_record_key(self, record_key):
        if self.encrypt == EncryptionType.SSE:
            return record_key

        return get_salted_hash(self.normalize_key(record_key), self.env_id)

    def prepare_outbound_filters(self, filters):
        out_filters = deepcopy(filters)
        if self.encrypt == EncryptionType.SSE:
            return out_filters

        if self.options.normalize_keys:
            out_filters = normalize_object_record_keys(out_filters)

        return hash_object_record_keys(
            out_filters,
            self.env_id,
            hash_search_keys=self.options.hash_search_keys,
        )

    def prepare_outbound_record(self, record):
        out_record = dict(record)
        if self.encrypt == EncryptionType.SSE:
            return out_record

        if self.options.normalize_keys:
            out_record = normalize_object_record_keys(out_record)

        return encrypt_record(
            self.crypto,
            out_record,
            self.env_id,
            hash_search_keys=self.options.hash_search_keys,
        )

    def process_inbound_record(self, record):
        in_record = dict(record)
        if self.encrypt == EncryptionType.SSE:
            return in_record
        return decrypt_record(self.crypto, in_record)

    def normalize_key(self, key):
        if self.options.normalize_keys:
            return normalize_key(key)
        return key
