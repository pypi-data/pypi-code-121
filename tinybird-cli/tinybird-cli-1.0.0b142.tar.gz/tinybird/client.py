import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, Set

import requests
from requests import Response
from requests_toolbelt.multipart.encoder import MultipartEncoder
import logging
import ssl
from urllib.parse import quote, urlencode
from tinybird.syncasync import sync_to_async


HOST = 'https://api.tinybird.co'
LOGIN_URL = 'https://ui.tinybird.co/auth/google'
LIMIT_RETRIES = 10

requests_get = sync_to_async(requests.get, thread_sensitive=False)
requests_post = sync_to_async(requests.post, thread_sensitive=False)
requests_put = sync_to_async(requests.put, thread_sensitive=False)
requests_delete = sync_to_async(requests.delete, thread_sensitive=False)


class AuthException(Exception):
    pass


class AuthNoTokenException(AuthException):
    pass


class DoesNotExistException(Exception):
    pass


class CanNotBeDeletedException(Exception):
    pass


class OperationCanNotBePerformed(Exception):
    pass


class TimeoutException(Exception):
    pass


class ReachRetryLimit(Exception):
    pass


class ConnectorNothingToLoad(Exception):
    pass


def connector_equals(connector, datafile_params):
    if not connector:
        return False
    if connector['name'] == datafile_params['kafka_connection_name']:
        return True
    return False


def parse_error_response(response: Response) -> str:
    try:
        content: Dict = response.json()
        if content.get('error', None):
            error = content['error']
            if content.get('errors', None):
                error += f' -> errors: {content.get("errors")}'
        else:
            error = json.dumps(response, indent=4)
        return error
    except json.decoder.JSONDecodeError:
        return f"Server error, cannot parse response. {response.content.decode('utf-8')}"


class TinyB(object):

    def __init__(self, token: str, host: str = HOST, version: Optional[str] = None):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        self.token = token
        self.host = host
        self.version = version

    async def _req(self, endpoint: str, data=None, method: str = 'GET', retries: int = 1, **kwargs):  # noqa: C901
        url = self.host + endpoint

        if self.token:
            url += ('&' if '?' in endpoint else '?') + 'token=' + self.token
        if self.version:
            url += ('&' if '?' in url else '?') + 'cli_version=' + quote(self.version)

        try:
            response: requests.Response
            if method == 'POST':
                response = await requests_post(url, data=data, **kwargs)
            elif method == 'PUT':
                response = await requests_put(url, data=data, **kwargs)
            elif method == 'DELETE':
                response = await requests_delete(url, **kwargs)
            else:
                response = await requests_get(url, **kwargs)

        except Exception as e:
            raise AuthException(f"Error on auth: {e}") from e

        logging.debug("== server response ==")
        logging.debug(response.content)
        logging.debug("==      end        ==")

        if response.status_code == 403:
            error = parse_error_response(response)
            if not self.token:
                raise AuthNoTokenException(f"Forbidden: {error}")
            raise AuthException(f"Forbidden: {error}")
        if response.status_code == 204 or response.status_code == 205:
            return None
        if response.status_code == 404:
            error = parse_error_response(response)
            raise DoesNotExistException(error)
        if response.status_code == 400:
            error = parse_error_response(response)
            raise OperationCanNotBePerformed(error)
        if response.status_code == 409:
            error = parse_error_response(response)
            raise CanNotBeDeletedException(error)
        if response.status_code == 599:
            raise TimeoutException("timeout")
        if response.status_code == 429:
            if retries > LIMIT_RETRIES:
                error = parse_error_response(response)
                raise ReachRetryLimit(error)
            retry_after = int(response.headers['Retry-After']) + retries
            await asyncio.sleep(retry_after)
            return await self._req(endpoint, data, method, retries + 1, **kwargs)
        if 'Content-Type' in response.headers and (response.headers['Content-Type'] == 'text/plain' or 'text/csv' in response.headers['Content-Type']):
            return response.content.decode('utf-8')
        if response.status_code >= 400 and response.status_code not in [400, 403, 404, 409, 429, 500]:
            error = parse_error_response(response)
            raise Exception(error)
        if response.content:
            try:
                return response.json()
            except json.decoder.JSONDecodeError:
                raise Exception(f"Server error, cannot parse response. {response.content.decode('utf-8')}")

        return response

    async def tokens(self):
        tokens = await self._req("/v0/tokens")
        return tokens['tokens']

    async def get_token_by_name(self, name: str):
        tokens = await self.tokens()
        for tk in tokens:
            if tk['name'] == name:
                return tk
        return None

    async def datasources(self, branch=None):
        response = await self._req("/v0/datasources")
        ds = response['datasources']

        if branch:
            ds = [x for x in ds if x['name'].startswith(branch)]
        return ds

    async def connections(self, connector: Optional[str] = None):
        response = await self._req('/v0/connectors')
        connectors = response['connectors']

        if connector:
            return [{
                'id': c['id'],
                'service': c['service'],
                'name': c['name'],
                'connected_datasources': len(c['linkers']),
                **c['settings']
            } for c in connectors if c['service'] == connector]
        return [{
            'id': c['id'],
            'service': c['service'],
            'name': c['name'],
            'connected_datasources': len(c['linkers']),
            **c['settings']
        } for c in connectors]

    async def get_datasource(self, ds_name: str) -> Dict[str, Any]:
        return await self._req(f"/v0/datasources/{ds_name}")

    async def alter_datasource(self, ds_name: str, new_schema: Optional[str] = None, description: Optional[str] = None, dry_run: bool = False):
        params = {'dry': 'true' if dry_run else 'false'}
        if new_schema:
            params.update({'schema': new_schema})
        if description:
            params.update({'description': description})
        res = await self._req(f'/v0/datasources/{ds_name}/alter?{urlencode(params)}', method='POST', data=b'')

        if 'Error' in res:
            raise Exception(res['error'])

        return res

    async def pipe_file(self, pipe: str):
        return await self._req(f"/v0/pipes/{pipe}.pipe")

    async def datasource_file(self, datasource: str):
        try:
            return await self._req(f"/v0/datasources/{datasource}.datasource")
        except DoesNotExistException:
            raise Exception(f"Data Source {datasource} not found.")

    async def datasource_analyze(self, url):
        params = {
            'url': url
        }
        return await self._req(f"/v0/analyze?{urlencode(params)}", method='POST', data='')

    async def datasource_analyze_file(self, data):
        return await self._req("/v0/analyze", method='POST', data=data)

    async def datasource_create_from_definition(self, parameter_definition: Dict[str, str]):
        return await self._req("/v0/datasources", method='POST', data=parameter_definition)

    async def datasource_create_from_url(self, table_name: str, url: str, mode: str = 'create', status_callback=None, sql_condition: Optional[str] = None, format: str = 'csv', replace_options: Optional[Set[str]] = None):
        params = {
            'name': table_name,
            'url': url,
            'mode': mode,
            'debug': 'blocks_block_log',
            'format': format
        }

        if sql_condition:
            params['replace_condition'] = sql_condition
        if replace_options:
            for option in list(replace_options):
                params[option] = 'true'

        req_url = f"/v0/datasources?{urlencode(params, safe='')}"
        res = await self._req(req_url, method='POST', data=b'')

        if 'error' in res:
            raise Exception(res['error'])

        return await self.wait_for_job(res['id'], status_callback, backoff_multiplier=1.5, maximum_backoff_seconds=20)

    async def datasource_delete(self, datasource_name: str):
        return await self._req(f"/v0/datasources/{datasource_name}", method='DELETE')

    async def datasource_append_data(self, datasource_name: str, f, mode: str = 'append', status_callback=None, sql_condition: Optional[str] = None, format: str = 'csv', replace_options: Optional[Set[str]] = None):
        params = {
            'name': datasource_name,
            'mode': mode,
            'format': format,
            'debug': 'blocks_block_log'
        }

        if sql_condition:
            params['replace_condition'] = sql_condition
        if replace_options:
            for option in list(replace_options):
                params[option] = 'true'
        if self.version:
            params['cli_version'] = self.version

        url = f"{self.host}/v0/datasources?{urlencode(params, safe='')}"
        if format == 'csv':
            m = MultipartEncoder(fields={'csv': ('csv', f, 'text/csv')})
        else:
            m = MultipartEncoder(fields={'ndjson': ('ndjson', f, 'application/x-ndjson')})

        r: Response = await requests_post(
            url,
            data=m,
            headers={
                'Authorization': 'Bearer ' + self.token, 'Content-Type': m.content_type
            }
        )

        if r.status_code == 400:
            raise OperationCanNotBePerformed(parse_error_response(r))

        if r.status_code != 200:
            raise Exception(r.json())

        res = r.json()

        if status_callback:
            status_callback(res)

        return res

    async def datasource_truncate(self, datasource_name: str):
        return await self._req(f"/v0/datasources/{datasource_name}/truncate", method='POST', data='')

    async def datasource_delete_rows(self, datasource_name: str, delete_condition: str):
        params = {
            "delete_condition": delete_condition
        }
        return await self._req(f'/v0/datasources/{datasource_name}/delete', method='POST', data=params)

    async def datasource_dependencies(self, no_deps: bool, match: str, pipe: str, datasource: str, check_for_partial_replace: bool):
        params = {
            "no_deps": 'true' if no_deps else 'false',
            "check_for_partial_replace": 'true' if check_for_partial_replace else 'false'
        }
        if match:
            params['match'] = match
        if pipe:
            params['pipe'] = pipe
        if datasource:
            params['datasource'] = datasource

        return await self._req(f'/v0/dependencies?{urlencode(params)}', timeout=60)

    async def analyze_pipe_node(self, pipe_name: str, node_name: str, ds_name: Optional[str] = None, dry_run: str = 'false'):
        params = urlencode({
            'include_datafile': 'true',
            'datasource': ds_name,
            'dry_run': dry_run
        })
        response = await self._req(f"/v0/pipes/{pipe_name}/nodes/{node_name}/analyze?{params}")
        return response

    async def populate_node(self, pipe_name: str, node_name: str, populate_subset=False):
        params: Dict[str, Any] = {}
        if populate_subset:
            params.update({'populate_subset': populate_subset})
        response = await self._req(f"/v0/pipes/{pipe_name}/population/{node_name}?{urlencode(params)}", method='POST')
        return response

    async def pipes(self, branch=None, dependencies: bool = False, node_attrs=None, attrs=None):
        params = {
            'dependencies': 'true' if dependencies else 'false',
            'attrs': attrs if attrs else '',
            'node_attrs': node_attrs if node_attrs else '',
        }
        response = await self._req(f"/v0/pipes?{urlencode(params)}")
        pipes = response['pipes']
        if branch:
            pipes = [x for x in pipes if x['name'].startswith(branch)]
        return pipes

    async def pipe(self, pipe: str):
        return await self._req(f"/v0/pipes/{pipe}")

    async def pipe_data(self, pipe_name_or_uid: str, sql: Optional[str] = None):
        if not sql:
            sql = f"SELECT * FROM {pipe_name_or_uid} LIMIT 50"
        return await self._req(f"/v0/pipes/{pipe_name_or_uid}.json?q={quote(sql, safe='')}")

    async def pipe_create(self, pipe_name: str, sql: str):
        return await self._req(f"/v0/pipes?name={pipe_name}&sql={quote(sql, safe='')}", method='POST', data=sql.encode())

    async def pipe_delete(self, pipe_name: str):
        return await self._req(f"/v0/pipes/{pipe_name}", method='DELETE')

    async def pipe_append_node(self, pipe_name_or_uid: str, sql: str):
        return await self._req(f"/v0/pipes/{pipe_name_or_uid}/append", method='POST', data=sql.encode())

    async def pipe_set_endpoint(self, pipe_name_or_uid: str, published_node_uid: str):
        return await self._req(f"/v0/pipes/{pipe_name_or_uid}/endpoint", method='PUT', data=published_node_uid.encode())

    async def query(self, sql):
        return await self._req(f"/v0/sql?q={quote(sql, safe='')}")

    async def jobs(self, status=None):
        jobs = (await self._req("/v0/jobs"))['jobs']
        if status:
            status = [status] if isinstance(status, str) else status
            jobs = [j for j in jobs if j['status'] in status]
        return jobs

    async def job(self, job_id: str):
        return await self._req(f"/v0/jobs/{job_id}")

    async def job_cancel(self, job_id: str):
        return await self._req(f"/v0/jobs/{job_id}/cancel", method='POST', data=b'')

    async def workspaces(self):
        return await self._req("/v0/user/workspaces")

    async def create_workspace(self, name: str):
        return await self._req(f"/v0/workspaces?name={name}", method='POST', data=b'')

    async def delete_workspace(self, id: str):
        return await self._req(f"/v0/workspaces/{id}", method='DELETE')

    async def workspace(self, workspace_id: str, with_token: bool = False):
        params = {
            'with_token': 'true' if with_token else 'false'
        }
        return await self._req(f"/v0/workspaces/{workspace_id}?{urlencode(params)}")

    async def workspace_info(self):
        return await self._req("/v0/workspace")

    async def wait_for_job(
            self,
            job_id: str,
            status_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
            backoff_seconds: float = 2.0,
            backoff_multiplier: float = 1,
            maximum_backoff_seconds: float = 2.0):
        done: bool = False
        while not done:
            res: Dict[str, Any] = await self._req("/v0/jobs/" + job_id + '?debug=blocks,block_log')

            if res['status'] == 'error':
                error_message = 'There has been an error'
                if not isinstance(res.get('error', True), bool):
                    error_message = str(res['error'])
                if 'errors' in res:
                    error_message += f": {res['errors']}"
                raise Exception(error_message)

            if res['status'] == 'cancelled':
                raise Exception('Job has been cancelled')

            done = res['status'] == 'done'

            if status_callback:
                status_callback(res)

            if not done:
                backoff_seconds = min(backoff_seconds * backoff_multiplier, maximum_backoff_seconds)
                await asyncio.sleep(backoff_seconds)

        return res

    async def datasource_kafka_connect(self, connection_id, datasource_name, topic, group, auto_offset_reset):
        return await self._req(f"/v0/datasources?connector={connection_id}&name={datasource_name}&"
                               f"kafka_topic={topic}&kafka_group_id={group}&kafka_auto_offset_reset={auto_offset_reset}",
                               method='POST', data=b'')

    async def connection_create_kafka(
        self,
        kafka_bootstrap_servers,
        kafka_key,
        kafka_secret,
        kafka_connection_name,
        kafka_auto_offset_reset=None,
        kafka_schema_registry_url=None
    ):

        params = {
            'service': 'kafka',
            'kafka_security_protocol': 'SASL_SSL',
            'kafka_sasl_mechanism': 'PLAIN',
            'kafka_bootstrap_servers': kafka_bootstrap_servers,
            'kafka_sasl_plain_username': kafka_key,
            'kafka_sasl_plain_password': kafka_secret,
            'name': kafka_connection_name
        }

        if kafka_schema_registry_url:
            params['kafka_schema_registry_url'] = kafka_schema_registry_url
        if kafka_auto_offset_reset:
            params['kafka_auto_offset_reset'] = kafka_auto_offset_reset

        connection_params = {
            key: value
            for key, value in params.items() if value is not None
        }

        return await self._req(f"/v0/connectors?{urlencode(connection_params)}", method='POST', data='')

    async def kafka_list_topics(self, connection_id: str, timeout=5):
        resp = await self._req(f"/v0/connector/preview?connector_id={connection_id}&preview_activity=false",
                               connect_timeout=timeout, request_timeout=timeout)
        return [x['topic'] for x in resp['preview']]

    async def connector_delete(self, connection_id):
        return await self._req(f"/v0/connectors/{connection_id}", method='DELETE')

    @staticmethod
    def _sql_get_used_tables_local(sql: str, raising: bool = False) -> List[str]:
        from tinybird.sql_toolset import sql_get_used_tables
        tables = sql_get_used_tables(sql, raising, table_functions=False)
        return [t[1] if t[0] == "" else f"{t[0]}.{t[1]}" for t in tables]

    async def _sql_get_used_tables_remote(self, sql: str, raising: bool = False) -> List[str]:
        params = {
            'q': sql,
            'raising': 'true' if raising else 'false',
            'table_functions': 'false'
        }
        result = await self._req('/v0/sql_tables', data=params, method='POST')
        return [t[1] if t[0] == "" else f"{t[0]}.{t[1]}" for t in result['tables']]

    # Get used tables from a query. Does not include table functions
    async def sql_get_used_tables(self, sql: str, raising: bool = False) -> List[str]:
        try:
            return self._sql_get_used_tables_local(sql, raising)
        except ModuleNotFoundError:
            return await self._sql_get_used_tables_remote(sql, raising)

    @staticmethod
    def _replace_tables_local(q: str, replacements):
        from tinybird.sql_toolset import replace_tables, replacements_to_tuples
        return replace_tables(q, replacements_to_tuples(replacements))

    async def _replace_tables_remote(self, q: str, replacements):
        params = {
            'q': q,
            'replacements': json.dumps({k[1] if isinstance(k, tuple) else k: v
                                        for k, v in replacements.items()})
        }
        result = await self._req('/v0/sql_replace', data=params, method='POST')
        return result['query']

    async def replace_tables(self, q: str, replacements):
        try:
            return self._replace_tables_local(q, replacements)
        except ModuleNotFoundError:
            return await self._replace_tables_remote(q, replacements)

    async def get_connection(self, **kwargs):
        result = await self._req('/v0/connectors')
        return next((connector for connector in result['connectors'] if connector_equals(connector, kwargs)), None)

    async def regions(self):
        return await self._req('/v0/regions')
