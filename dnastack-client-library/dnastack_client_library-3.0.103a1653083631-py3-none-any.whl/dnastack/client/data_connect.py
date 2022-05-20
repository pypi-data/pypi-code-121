import re
from dataclasses import dataclass
from datetime import datetime, time, date, timedelta
from decimal import Decimal
from pprint import pformat
from typing import Optional, Any, Dict, List, Iterator, Union, Callable, Iterable
from urllib.parse import urljoin

from pydantic import BaseModel, ValidationError

from dnastack.client.base_client import BaseServiceClient
from dnastack.client.base_exceptions import UnauthenticatedApiAccessError, UnauthorizedApiAccessError, ApiError, \
    MissingResourceError, ServerApiError
from dnastack.client.result_iterator import ResultLoader, ResultIterator
from dnastack.client.service_registry.models import ServiceType
from dnastack.common.logger import get_logger
from dnastack.http.session import HttpSession

_logger = get_logger('module/data_connect')

DATA_CONNECT_TYPE_V1_0 = ServiceType(group='org.ga4gh',
                                     artifact='data-connect',
                                     version='1.0.0')


class InactiveQuerySessionError(StopIteration):
    """ Raised when the query loader has ended its session """


class TableNotFoundError(MissingResourceError):
    """ Raised when the requested table is not found """


class DataConversionError(RuntimeError):
    """ Raised when the data conversion fails """


class Error(BaseModel):
    """ Error representation """
    status: Any
    title: str
    details: Optional[str]


class Table(BaseModel):
    """ Table metadata """
    name: str
    description: Optional[str]
    data_model: Optional[Dict[str, Any]]
    errors: Optional[List[Error]]


class Pagination(BaseModel):
    """ Pagination """
    next_page_url: Optional[str]


class TableDataResponse(BaseModel):
    """ Table data """
    data: Optional[List[Dict[str, Any]]]
    data_model: Optional[Dict[str, Any]] = list()
    pagination: Optional[Pagination]
    errors: Optional[List[Error]]


class ListTablesResponse(BaseModel):
    """ Representation of the list of table """
    tables: Optional[List[Table]]
    pagination: Optional[Pagination]
    errors: Optional[List[Error]]


class TableListLoader(ResultLoader):
    def __init__(self,
                 initial_url: str,
                 http_session: Optional[HttpSession] = None):
        self.__http_session = http_session
        self.__initial_url = initial_url
        self.__current_url: Optional[str] = None
        self.__active = True

    def load(self) -> List[Table]:
        if not self.__active:
            raise InactiveQuerySessionError(self.__initial_url)

        with self.__http_session as session:
            current_url = self.__current_url or self.__initial_url
            response = session.get(current_url)
            status_code = response.status_code
            response_text = response.text

            if status_code == 401:
                raise UnauthenticatedApiAccessError(self.__generate_api_error_feedback(response_text))
            elif status_code == 403:
                raise UnauthorizedApiAccessError(self.__generate_api_error_feedback(response_text))
            elif status_code >= 400:  # Catch all errors
                self.logger.error(f'{self.__initial_url}: Unexpectedly received HTTP {status_code} from {current_url}')
                raise ApiError(current_url, status_code, response_text)

            try:
                response_body = response.json() if response_text else dict()
            except Exception as error:
                self.logger.error(f'{self.__initial_url}: Unexpectedly non-JSON response body from {current_url}')
                raise ApiError(current_url, status_code,
                               f"Could not deserialize JSON. Actual response:\n{response.text}") from error

            try:

                if isinstance(response_body, list):
                    api_response = ListTablesResponse(tables=response_body)
                else:
                    api_response = ListTablesResponse(**response_body)
            except ValidationError:
                raise ServerApiError(f'Invalid Response Body: {response_body}')

            self.logger.debug(f'Response:\n{pformat(response_body, indent=2)}')

            if api_response.errors:
                extracted_errors = [e.title for e in api_response.errors]

                self.__active = False

                if self.__current_url:
                    # The iterator encounters an unexpected error while iterating the result. Return an empty list.
                    self.logger.warning(
                        f'While listing tables from {self.__initial_url}, the server failed to respond to the request to '
                        f'{self.__current_url} due to errors and the client will return the data received so far.'
                    )
                else:
                    # The iterator encounters an error on the first request.
                    self.logger.error(f'The server responds an error while making a request to {self.__initial_url}.')

                self.logger.warning(f'The errors are: {extracted_errors}')
                return []

            # FIXME The failed build is due that listing table from publisher_data fails. The code should throw
            #  an exception if all requests during listing fails.

            self.__current_url = api_response.pagination.next_page_url if api_response.pagination else None
            if not self.__current_url:
                self.__active = False

            return api_response.tables

    def has_more(self) -> bool:
        return self.__active or self.__current_url

    def __generate_api_error_feedback(self, response_body) -> str:
        if self.__current_url:
            return f'Failed to load a follow-up page of the table list from {self.__current_url} ({response_body})'
        else:
            return f'Failed to load the first page of the table list from {self.__initial_url} ({response_body})'


@dataclass(frozen=True)
class DataMapper:
    str_pattern: re.Pattern
    map: Callable[[Any], Any]

    @classmethod
    def init(cls,
             str_pattern: re.Pattern,
             map: Callable[[Any], Any]):
        return cls(str_pattern, map)

    def can_handle(self, content: Any) -> bool:
        return self.str_pattern.match(content) is not None


class IntervalDayToSecondMapper(DataMapper):
    def __init__(self):
        super().__init__(
            re.compile(r'P((?P<days>\d+)D)?(T((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?)?'),
            self._map
        )

    def _map(self, s: Any) -> Any:
        raw_delta = self.str_pattern.match(s).groupdict()
        return timedelta(**{
            p: int(v) if v is not None else 0
            for p, v in raw_delta.items()
        })


@dataclass(frozen=True)
class DataMapperGroup:
    json_type: str
    formats: List[str]
    mappers: List[DataMapper]

    def can_handle(self, given_json_types: List[str], given_data_format: str) -> bool:
        return self.json_type in given_json_types and given_data_format in self.formats

    def __str__(self):
        return f'{type(self).__name__}(json_type={self.json_type}, formats={self.formats})'


class QueryLoader(ResultLoader):
    _data_mapper_groups: Iterable[DataMapperGroup] = [
        # numbers
        DataMapperGroup(
            'string',
            ['bigint'],
            [
                DataMapper.init(
                    re.compile(r'^\d+$'),
                    lambda s: int(s)
                )
            ]
        ),
        DataMapperGroup(
            'string',
            ['decimal'],
            [
                DataMapper.init(
                    re.compile(r'^(\d+\.\d+|\d+|\.\d+)$'),
                    lambda s: Decimal(s)
                )
            ]
        ),
        # date
        DataMapperGroup(
            'string',
            ['date'],
            [
                DataMapper.init(
                    re.compile(r'^\d{4}-\d{2}-\d{2}$'),
                    lambda s: date.fromisoformat(s)
                ),
            ]
        ),
        # time without time zone
        DataMapperGroup(
            'string',
            ['time', 'time without time zone'],
            [
                DataMapper.init(
                    re.compile(r'^\d{2}:\d{2}:\d{2}(\.\d{,6})?$'),
                    lambda s: time.fromisoformat(s)
                ),
            ]
        ),
        # time with time zone
        DataMapperGroup(
            'string',
            ['time with time zone'],
            [
                DataMapper.init(
                    re.compile(r'^\d{2}:\d{2}:\d{2}(\.\d{,6})?Z$'),
                    lambda s: time.fromisoformat(s[:-1] + '+00:00')
                ),
                DataMapper.init(
                    re.compile(r'^\d{2}:\d{2}:\d{2}(\.\d{,6})?\s*(-|\+)\d{2}$'),
                    lambda s: time.fromisoformat(s + ':00')
                ),
                DataMapper.init(
                    re.compile(r'^\d{2}:\d{2}:\d{2}(\.\d{,6})?\s*(-|\+)\d{2}:\d{2}$'),
                    lambda s: time.fromisoformat(s)
                ),
            ]
        ),
        # timestamp without time zone
        DataMapperGroup(
            'string',
            ['timestamp', 'timestamp without time zone'],
            [
                DataMapper.init(
                    re.compile(r'^\d{4}-\d{2}-\d{2}(T| )\d{2}:\d{2}:\d{2}(\.\d{,6})?$'),
                    lambda s: datetime.fromisoformat(s)
                ),
            ]
        ),
        # timestamp with time zone
        DataMapperGroup(
            'string',
            ['timestamp with time zone'],
            [
                DataMapper.init(
                    re.compile(r'^\d{4}-\d{2}-\d{2}(T| )\d{2}:\d{2}:\d{2}(\.\d{,6})?Z$'),
                    lambda s: datetime.fromisoformat(s[:-1] + '+00:00')
                ),
                DataMapper.init(
                    re.compile(r'^\d{4}-\d{2}-\d{2}(T| )\d{2}:\d{2}:\d{2}(\.\d{,6})?(-|\+)\d{2}$'),
                    lambda s: datetime.fromisoformat(s + ':00')
                ),
                DataMapper.init(
                    re.compile(r'^\d{4}-\d{2}-\d{2}(T| )\d{2}:\d{2}:\d{2}(\.\d{,6})?(-|\+)\d{2}:\d{2}$'),
                    lambda s: datetime.fromisoformat(s)
                ),
            ]
        ),
        # NOTE: the "interval year to month" type is not supported.
        # interval day to second
        DataMapperGroup(
            'string',
            ['interval day to second'],
            [
                IntervalDayToSecondMapper()
            ]
        )
    ]

    def __init__(self,
                 initial_url: str,
                 query: Optional[str] = None,
                 http_session: Optional[HttpSession] = None):
        self.__http_session = http_session
        self.__initial_url = initial_url
        self.__current_url: Optional[str] = None
        self.__query = query
        self.__active = True
        self.__schema: Dict[str, Any] = dict()

    def load(self) -> List[Dict[str, Any]]:
        if not self.__active:
            raise InactiveQuerySessionError(self.__initial_url)

        with self.__http_session as session:
            if not self.__current_url:
                # Load the initial page.
                if self.__query:
                    # Send a search request
                    self.logger.debug(f'Initial Page: QUERY: {self.__initial_url}: {self.__query}')
                    response = session.post(self.__initial_url, json=dict(query=self.__query))
                else:
                    # Fetch the table data
                    self.logger.debug(f'Initial Page: URL: {self.__initial_url}')
                    response = session.get(self.__initial_url)
            else:
                # Load a follow-up page.
                self.logger.debug(f'Follow-up: URL: {self.__current_url}')
                response = session.get(self.__current_url)

            status_code = response.status_code
            response_body = response.text
            self.logger.debug(f'Response (JSON):\n{response_body}')

            if status_code == 401:
                raise UnauthenticatedApiAccessError(self.__generate_api_error_feedback(response_body))
            elif status_code == 403:
                raise UnauthorizedApiAccessError(self.__generate_api_error_feedback(response_body))
            elif status_code == 404:
                raise MissingResourceError(self.__generate_api_error_feedback(response_body))
            elif status_code >= 400:  # Catch all errors
                try:
                    error_response = TableDataResponse(**response.json())
                    error_feedback = ', '.join([e.title for e in error_response.errors])
                except:
                    error_feedback = response_body
                raise ApiError(self.__initial_url, status_code, error_feedback)

            api_response = TableDataResponse(**response.json())

            if api_response.errors:
                extracted_errors = [e.title for e in api_response.errors ]

                self.__active = False

                if self.__current_url:
                    # The iterator encounters an unexpected error while iterating the result. Return an empty list.
                    self.logger.warning(
                        f'While listing tables from {self.__initial_url}, the server failed to respond to the request to '
                        f'{self.__current_url} due to errors and the client will return the data received so far.'
                    )
                else:
                    # The iterator encounters an error on the first request.
                    self.logger.error(f'The server responds an error while making a request to {self.__initial_url}.')

                self.logger.warning(f'The errors are: {extracted_errors}')
                return []

            self.__current_url = api_response.pagination.next_page_url if api_response.pagination else None
            if not self.__current_url:
                self.__active = False

            if not self.__schema and api_response.data_model:
                self.__schema = api_response.data_model

            return self.__remap_array(self.__schema, api_response.data)

    def has_more(self) -> bool:
        return self.__active or self.__current_url

    def __remap_array(self, schema: Dict[str, Any], array: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not schema:
            return array
        else:
            return [self.__remap_obj(schema, row) for row in array]

    def __remap_obj(self, schema: Dict[str, Any], obj: Any) -> Any:
        if not schema:
            return obj

        obj_types = (
            ([schema['type']] if isinstance(schema['type'], str) else schema['type'])
            if 'type' in schema
            else ['object']
        )

        if 'array' in obj_types and isinstance(obj, (tuple, list)):
            return self.__remap_array(schema['items'], obj)
        elif 'object' in obj_types and isinstance(obj, dict):
            if schema.get('properties'):
                return {
                    property_name: (
                        self.__remap_obj(schema['properties'][property_name], property_value)
                        if property_name in schema['properties'] and schema['properties'][property_name]
                        else property_value
                    )
                    for property_name, property_value in obj.items()
                }
            else:
                return obj
        else:
            return self.__remap_value(obj_types, schema.get('format'), obj)

    def __remap_value(self, json_types: List[str], data_format: str, value: Any):
        # Source: https://github.com/ga4gh-discovery/data-connect/blob/develop/SPEC.md#correspondence-between-sql-and-json-data-types-in-the-search-result
        # NOTE: Non-standard data type will also not be handled and the original value will be returned.
        for mapper_group in self._data_mapper_groups:
            if not mapper_group.can_handle(json_types, data_format):
                continue

            mapper_index = 0
            for mapper in mapper_group.mappers:
                if not mapper.can_handle(value):
                    mapper_index += 1
                    continue

                if not mapper.map:
                    raise NotImplementedError(f'The mapper #{mapper_index} is not fully implemented for {mapper_group.formats}.')

                try:
                    return mapper.map(value)
                except Exception:
                    raise DataConversionError(f'{mapper_group}#{mapper_index}: Unexpected error during data '
                                              f'conversion with {mapper.str_pattern.pattern}')

        return value

    def __generate_api_error_feedback(self, response_body=None) -> str:
        if self.__query:
            if self.__current_url:
                return f'Failed to load a follow-up page of the result from this query:\n\n{self.__query}\n\nResponse:\n{response_body}'
            else:
                return f'Failed to load the first page of the result from this query:\n\n{self.__query}\n\nResponse:\n{response_body}'
        else:
            if self.__current_url:
                return f'Failed to load a follow-up page of {self.__current_url}'
            else:
                return f'Failed to load the first page of {self.__initial_url}'


class TableWrapper:
    """ Table API Wrapper """

    def __init__(self,
                 table_name: str,
                 url: str,
                 http_session: Optional[HttpSession] = None):
        self.__http_session = http_session
        self.__table_name = table_name
        self.__url = url

    @property
    def name(self):
        """ The name of the table """
        return self.__table_name

    @property
    def info(self):
        """ The information of the table, such as schema """
        with self.__http_session as session:
            table_name = self.__table_name
            response = session.get(urljoin(self.__url, 'info'))

            status_code = response.status_code

            if status_code == 401:
                raise UnauthenticatedApiAccessError('Authentication required')
            elif status_code == 403:
                raise UnauthorizedApiAccessError('Insufficient privilege')
            elif status_code == 404:
                raise TableNotFoundError(table_name)
            elif status_code >= 400:  # Catch all errors
                raw_response_body = response.text
                raise ApiError(self.__url, status_code, raw_response_body)

            response_body = response.json()

            return Table(**response_body)

    @property
    def data(self) -> Iterator[Dict[str, Any]]:
        """ The iterator to the data in the table """
        return ResultIterator(QueryLoader(http_session=self.__http_session,
                                          initial_url=urljoin(self.__url, 'data')))


class DataConnectClient(BaseServiceClient):
    """
    A Client for the GA4GH Data Connect standard
    """

    @staticmethod
    def get_adapter_type() -> str:
        return 'data_connect'

    @staticmethod
    def get_supported_service_types() -> List[ServiceType]:
        return [
            DATA_CONNECT_TYPE_V1_0,
        ]

    def query(self, query: str) -> Iterator[Dict[str, Any]]:
        """ Run an SQL query """
        return ResultIterator(QueryLoader(http_session=self.create_http_session(),
                                          initial_url=urljoin(self.url, r'search'),
                                          query=query))

    def iterate_tables(self) -> Iterator[Table]:
        """ Iterate the list of tables """
        return ResultIterator(TableListLoader(http_session=self.create_http_session(),
                                              initial_url=urljoin(self.url, r'tables')))

    def list_tables(self) -> List[Table]:
        """ List all tables """
        return [t for t in self.iterate_tables()]

    def table(self, table: Union[Table, TableWrapper, str]) -> TableWrapper:
        """ Get the table wrapper """
        table_name = self._get_table_name(table)
        table_url = urljoin(self.url, f'table/{table_name}/')
        return TableWrapper(http_session=self.create_http_session(),
                            table_name=table_name,
                            url=table_url)

    def get_table(self, table: Union[Table, TableWrapper, str]) -> Table:
        """ Get the table metadata """
        self._logger.warning(
            'This method will be deprecated in v3.1. Please use <client>.table(table_name).info instead.'
        )
        return self.table(table).info

    @staticmethod
    def _get_table_name(table: Union[Table, TableWrapper, str]) -> str:
        return table.name if hasattr(table, 'name') else table
