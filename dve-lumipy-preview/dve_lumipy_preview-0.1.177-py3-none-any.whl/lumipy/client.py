import io
import json
from json.decoder import JSONDecodeError
import time
from math import ceil
from typing import Callable, Dict, Optional

import luminesce
import pandas as pd
from fbnsdkutilities import ApiClientFactory
from luminesce.exceptions import ApiException

import lumipy
from lumipy.common.string_utils import indent_str


def _add_lumipy_tag(sql: str):
    if hasattr(lumipy, '__version__'):
        version = lumipy.__version__
    else:
        version = ''
    return f'-- lumipy {version}\n{sql}'


class Client:
    """Higher level client that wraps the low-level luminesce python sdk. This client offers a smaller collection of
    methods for starting, monitoring and retrieving queries as Pandas DataFrames.

    """

    def __init__(self, max_retries: Optional[int] = 5, retry_wait: Optional[float] = 0.5, **kwargs):
        """__init__ method of the lumipy client class. It is recommended that you use the lumipy.get_client() function
        at the top of the library.

        Args:
            max_retries (Optional[int]): number of times to retry a request after receiving an error code.
            code.
            retry_wait (Optional[float]):time in seconds to wait to try again after receiving an error code.
            code.

        Keyword Args:
            token (str): Bearer token used to initialise the API
            api_secrets_filename (str): Name of secrets file (including full path)
            api_url (str): luminesce API url
            app_name (str): Application name (optional)
            certificate_filename (str): Name of the certificate file (.pem, .cer or .crt)
            proxy_url (str): The url of the proxy to use including the port e.g. http://myproxy.com:8888
            proxy_username (str): The username for the proxy to use
            proxy_password (str): The password for the proxy to use
            correlation_id (str): Correlation id for all calls made from the returned finbournesdkclient API instances

        """

        self._factory = ApiClientFactory(luminesce, **kwargs)

        self._catalog_api = self._factory.build(luminesce.api.CurrentTableFieldCatalogApi)
        self._sql_exec_api = self._factory.build(luminesce.api.SqlExecutionApi)
        self._sql_bkg_exec_api = self._factory.build(luminesce.api.SqlBackgroundExecutionApi)
        self._history_api = self._factory.build(luminesce.api.HistoricallyExecutedQueriesApi)

        self.max_retries = max_retries
        self.retry_wait = retry_wait

    def get_token(self):
        return self._factory.api_client.configuration.access_token

    def _retry_handling(self, action: Callable, label: str, retry=False):
        """Wrap an api call to handle error retries and present more readable information from exceptions.

        Args:
            action (Callable): Parameterless function wrapping method call to luminesce, so it can be called repeatedly.
            label (str): name of the method being called.

        Returns:
            Any: the result of the luminesce python sdk api method call.
        """

        attempts = 0
        while True:
            try:
                return action()
            except ApiException as ae:
                if retry and attempts < self.max_retries:
                    attempts += 1
                    time.sleep(self.retry_wait)
                    print(f"Received {ae.status} status code. Retrying {attempts}/{self.max_retries}...")
                else:
                    if retry:
                        print(f"Max number of retries ({attempts + 1}) exceeded {self.max_retries}.")
                    print(f"Request to {label} failed with status code {ae.status}, reason: '{ae.reason})'.")
                    try:
                        body = json.loads(ae.body)
                        if 'detail' in body.keys():
                            detail = body['detail']
                            print(indent_str(f"Details:\n{indent_str(detail, n=4)}", n=4))
                    except JSONDecodeError:
                        print(indent_str(f"Details:\n{indent_str(str(ae.body), n=4)}", n=4))
                    raise ae

    def table_field_catalog(self) -> pd.DataFrame:
        """Get the table field catalog as a DataFrame.

        The table field catalog contains a row describing each field on each provider you have access to.

        Returns:
            DataFrame: dataframe containing table field catalog information.
        """
        res = self._retry_handling(
            self._catalog_api.get_catalog,
            'table field catalog'
        )
        return pd.DataFrame(json.loads(res))

    def query_and_fetch(self, sql: str, name: Optional[str] = 'query', timeout: Optional[int] = 3600) -> pd.DataFrame:
        """Send a query to Luminesce and get it back as a pandas dataframe.

        Args:
            sql (str): query sql to be sent to Luminesce
            name (str): name of the query (defaults to just 'query')
            timeout (int): max time for the query to run in seconds (defaults to 3600)

        Returns:
            DataFrame: result of the query as a pandas dataframe.
        """
        res = self._retry_handling(
            lambda: self._sql_exec_api.put_by_query_csv(
                body=_add_lumipy_tag(sql),
                query_name=name,
                timeout_seconds=timeout
            ),
            'query and fetch'
        )
        buffer_result = io.StringIO(res)
        return pd.read_csv(buffer_result, encoding='utf-8')

    def start_query(self, sql: str, name: Optional[str] = "query", timeout: Optional[int] = 3600, keep_for: Optional[int] = 7200) -> str:
        """Send an asynchronous query to Luminesce. Starts the query but does not wait and fetch the result.

        Args:
            sql (str): query sql to be sent to Luminesce
            name (str): name of the query (defaults to just 'query')
            timeout (int): max time for the query to run in seconds (defaults to 3600)
            keep_for (int): time to keep the query result for in seconds (defaults to 7200)

        Returns:
            str: string containing the execution ID

        """
        res = self._retry_handling(
            lambda: self._sql_bkg_exec_api.start_query(
                body=_add_lumipy_tag(sql),
                query_name=name,
                timeout_seconds=timeout,
                keep_for_seconds=keep_for
            ),
            'start query'
        )
        return res.execution_id

    def get_status(self, execution_id: str) -> Dict[str, str]:
        """Get the status of a Luminesce query

        Args:
            execution_id (str): unique execution ID of the query.

        Returns:
            Dict[str, str]: dictionary containing information on the query status.
        """
        return self._retry_handling(
            lambda: self._sql_bkg_exec_api.get_progress_of(execution_id).to_dict(),
            'get query status'
        )

    def delete_query(self, execution_id: str) -> Dict[str, str]:
        """Deletes a Luminesce query.

        Args:
            execution_id (str): unique execution ID of the query.

        Returns:
            Dict[str, str]: dictionary containing information on the deletion.

        """
        return self._retry_handling(
            lambda: self._sql_bkg_exec_api.cancel_query(execution_id).to_dict(),
            'delete query'
        )

    def _get_page(self, execution_id, page, page_size, sort_by, filter_str):
        """Gets a single page of a completed luminesce query and returns it as a pandas dataframe.

        Args:
            execution_id (str): execution ID of the query.
            page (int): page number to fetch.
            sort_by (str): string representing a sort to apply to the result before downloading it.
            filter_str (str): string representing a filter to apply to the result before downloading it.
            page_size (int, Optional): page size when getting the result via pagination. Default = 100000.

        Returns:
            DataFrame: downloaded page from result of the query as a pandas dataframe.

        """

        res = self._retry_handling(
            lambda: self._sql_bkg_exec_api.fetch_query_result_csv(
                execution_id,
                page=page,
                limit=page_size,
                sort_by=sort_by,
                filter=filter_str
            ),
            'get result',
            True
        )
        buffer_result = io.StringIO(res)
        return pd.read_csv(buffer_result, encoding='utf-8')

    def get_result(self, execution_id: str, page_size: Optional[int] = 100000, sort_by: Optional[str] = None, filter_str: Optional[str] = None, verbose: bool = False):
        """Gets the result of a completed luminesce query and returns it as a pandas dataframe.

        Args:
            execution_id (str): execution ID of the query.
            sort_by (Optional[str]): string representing a sort to apply to the result before downloading it.
            filter_str (Optional[str]): optional string representing a filter to apply to the result before downloading it.
            page_size (Optional[int]): page size when getting the result via pagination. Default = 100000.
            verbose (Optional[bool]):
        Returns:
            DataFrame: result of the query as a pandas dataframe.

        """

        n_tries = 0
        row_count = -1

        while row_count == -1 and n_tries < self.max_retries:
            status = self.get_status(execution_id)

            if status['status'] == 'Faulted':
                raise ValueError("Can't fetch query results: query status = 'Faulted'.")

            row_count = int(status['row_count'])
            n_tries += 1
            time.sleep(0.5)

        if verbose:
            print(f'Fetching {row_count} row{"" if row_count == 1 else "s"} of data... 📡')

        chunks = []
        n_pages = max(1, ceil(row_count / page_size))
        for page in range(n_pages):
            if verbose:
                print(f"   Downloading page {page+1}/{n_pages}... ", end='')
            chunk = self._get_page(execution_id, page, page_size, sort_by, filter_str)
            if verbose:
                print('done!')

            chunks.append(chunk)

        return pd.concat(chunks)

    def start_history_query(self):
        """Start a query that get data on queries that have run historically

        Returns:
            str: execution ID of the history query
        """
        res = self._retry_handling(
            lambda: self._history_api.get_history(),
            'start history query'
        )
        return res.execution_id

    def get_history_status(self, execution_id: str):
        """Get the status of a history query

        Args:
            execution_id (str): execution ID to check status for

        Returns:
            Dict[str,str]: dictionary containing the information from the status response json
        """
        return self._retry_handling(
            lambda: self._history_api.get_progress_ot_history(execution_id),
            'get history query status'
        )

    def get_history_result(self, execution_id: str):
        """Get result of history query

        Args:
            execution_id: execution ID to get the result for

        Returns:
            DataFrame: pandas dataframe containing the history query result.
        """
        res = self._retry_handling(
            lambda: self._history_api.fetch_history_result_json(execution_id),
            'get history query result'
        )
        return pd.DataFrame(json.loads(res))

    def delete_view(self, name: str):
        """Deletes a Luminesce view provider with the given name.

        Args:
            name (str): name of the view provider to delete.

        Returns:
            DataFrame: result of the view deletion query as a pandas dataframe.

        """
        return self.query_and_fetch(f"""
            @x = use Sys.Admin.SetupView
                --provider={name}
                --deleteProvider
                --------------
                select 1;
                enduse;
            select * from @x;
            """)


def get_client(**kwargs) -> Client:
    """Build a lumipy client by passing any of the following: a token, api_url and app_name; a path to a secrets file
       via api_secrets_filename; or by passing in proxy information. If none of these are provided then lumipy will try
       to find the credentials information as environment variables.

       Keyword Args:
           token (str): Bearer token used to initialise the API
           api_secrets_filename (str): Name of secrets file (including full path)
           api_url (str): luminesce API url
           app_name (str): Application name (optional)
           certificate_filename (str): Name of the certificate file (.pem, .cer or .crt)
           proxy_url (str): The url of the proxy to use including the port e.g. http://myproxy.com:8888
           proxy_username (str): The username for the proxy to use
           proxy_password (str): The password for the proxy to use
           correlation_id (str): Correlation id for all calls made from the returned finbournesdkclient API instances

    Returns:
        Client: the lumipy client.
    """
    return Client(**kwargs)
