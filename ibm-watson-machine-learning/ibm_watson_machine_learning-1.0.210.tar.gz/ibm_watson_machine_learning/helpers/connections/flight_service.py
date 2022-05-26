################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2019, 2020, 2021
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################
import os
import logging
import json
import sys
import time
import threading
import queue
import pandas as pd

from contextlib import nullcontext
from functools import partial
from typing import List, Optional, Iterable, Generator

from ibm_watson_machine_learning.utils.autoai.errors import InvalidSamplingType
from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, SamplingTypes
from ibm_watson_machine_learning.wml_client_error import (
    DataStreamError, WrongLocationProperty, WrongFileLocation, SpaceIDandProjectIDCannotBeNone)
from ibm_watson_machine_learning.utils.utils import is_lib_installed, prepare_interaction_props_for_cos

is_lib_installed(lib_name='pyarrow', install=True)
import pyarrow as pa
from pyarrow import flight

logger = logging.getLogger("automl")

DEFAULT_PARTITIONS_NUM = 4


class FakeCallback:
    def __init__(self):
        self.logger = logger

    def status_message(self, msg: str):
        self.logger.debug(msg)


class FlightConnection:
    """FlightConnection object unify the work for data reading from different types of data sources,
        including databases. It uses a Flight Service and `pyarrow` library to connect and transfer the data.

        # Note:
        # All available and supported connection types could be found on:
        # https://connectivity-matrix.us-south.cf.test.appdomain.cloud
        # -- end note

    Parameters
    ----------
    headers: dictionary, required
        WML authorization headers to connect with Flight Service.

    project_id: str, required

    space_id: str, required

    label: string, required
        Y column name. It is required for subsampling.

    sampling_type: str, required
        A sampling strategy required of choice.

    learning_type: string, required
        Type of the dataset: 'classification', 'multiclass', 'regression'. Needed for resampling.
        If value is equal to None 'first_n_records' strategy will be used no mather what is specified in
        'sampling_type'.

    data_location: dict, optional
        Data location information passed by user.

    enable_subsampling: bool, optional
        Tells to activate sampling mode for large data.

    callback: StatusCallback, required
        Required for sending messages.

    data_size_limit: int, optional
        Upper limit for overall data that should be downloaded in Bytes, Default: 1GB.

    logical_batch_size_limit: int, optional
        Upper limit for logical batch when subsampling is turned on (in Bytes). Default 2GB.
        The logical batch is the batch that is merged to the subsampled batch (eg. 2GB + 1GB) and then we
        perform subsampling on top of that 3GBs and rewrite 1GB batch (subsampled one) again.

    flight_parameters: dictionary, optional
        Pure unchanged flight service parameters that need to be passed to the service.

    fallback_to_one_connection: bool, optional
        Indicates if in case of failure we should switch to the one connection and try again.
        Default True.
    """

    def __init__(self,
                 headers: dict,
                 sampling_type: str,
                 label: str,
                 learning_type: str,
                 params: dict,
                 project_id: Optional[str] = None,
                 space_id: Optional[str] = None,
                 asset_id: Optional[str] = None,
                 connection_id: Optional[str] = None,
                 data_location: Optional[dict] = None,
                 enable_subsampling: Optional[bool] = False,
                 callback: Optional['Callback'] = None,
                 data_size_limit: Optional[int] = 1073741824,  # 1GB in Bytes
                 logical_batch_size_limit: Optional[int] = 1073741824 * 2,  # 2GB in Bytes
                 flight_parameters: dict = None,
                 extra_interaction_properties: dict = None,
                 fallback_to_one_connection: Optional[bool] = True,
                 number_of_batch_rows: int = None,
                 stop_after_first_batch: bool = False,
                 **kwargs
                 ) -> None:

        if project_id is None and space_id is None:
            raise SpaceIDandProjectIDCannotBeNone(
                reason="'space_id' and 'project_id' are None. Please set one of them.")

        self.headers = headers  # WML authorization headers

        self.number_of_batch_rows = number_of_batch_rows
        self.stop_after_first_batch = stop_after_first_batch

        # Note: Upper bound limitation for data in memory
        self.data_size_limit = data_size_limit  # size of normal or subsampled batch in RAM (Bytes)
        self.logical_batch_size_limit = logical_batch_size_limit  # size of larger not subsampled batch in RAM (Bytes)
        # --- end note

        # callback is used in the backend to send status messages
        self.callback = callback if callback is not None else FakeCallback()

        # Note: Variables from AutoAI training
        self.sampling_type = sampling_type
        self.label = label
        self.learning_type = learning_type
        self.params = params
        self.project_id = project_id
        self.space_id = space_id
        self.asset_id = asset_id
        self.connection_id = connection_id
        self.data_source_type = None
        # --- end note

        self.data_location = data_location

        # Note: control and store variables of flight reading mechanism
        self.lock_read = threading.Lock()
        self.stop_reading = False
        self.row_size = 0
        self.threads_exceptions: List['str'] = []
        self.q = queue.Queue()
        # a threading.Condition() to notify of q or
        # stop_reading changes
        self.read_status_change = threading.Condition()

        self.subsampled_data: 'pd.DataFrame' = pd.DataFrame()
        self.data: 'pd.DataFrame' = pd.DataFrame()
        self.enable_subsampling = enable_subsampling
        self.total_size = 0  # total size of downloaded data in Bytes (only in single thread)
        self.downloaded_data_size = 0  # total size of downloaded data in Bytes (every case)
        self.batch_queue = []

        self.flight_parameters = flight_parameters if flight_parameters is not None else {}
        self._wml_client = kwargs.get('_wml_client')

        # user can define how many parallel connections initiate to database
        self.max_flight_batch_number = self.params.get('n_parallel_data_connections', DEFAULT_PARTITIONS_NUM)
        if 'num_partitions' in self.flight_parameters:
            self.max_flight_batch_number = self.flight_parameters['num_partitions']
        # --- end note

        self.fallback_to_one_connection = fallback_to_one_connection

        self.read_binary = False
        self.write_binary = False

        additional_connection_args = {}
        if os.environ.get('TLS_ROOT_CERTS_PATH'):
            additional_connection_args['tls_root_certs'] = os.environ.get('TLS_ROOT_CERTS_PATH')

        self.extra_interaction_properties = extra_interaction_properties

        self.flight_location = None
        self.flight_port = None

        self._set_default_flight_location()

        self.flight_client = flight.FlightClient(
            location=f"grpc+tls://{self.flight_location}:{self.flight_port}",
            disable_server_verification=True,
            override_hostname=self.flight_location,
            **additional_connection_args
        )

    def _q_put_nowait(self, item):
        # we are not interested in q size increase, so no Condition waiting
        self.q.put_nowait(item)

    def _q_get(self, **kwargs):
        # return item in q, and notify interest threads that q is changing
        item = None
        with self.read_status_change:
            item = self.q.get(**kwargs)
            self.read_status_change.notify_all()
        return item

    def _q_reset(self):
        with self.read_status_change:
            self.q = queue.Queue()
            self.read_status_change.notify_all()

    def _set_stop_reading(self, value):
        # we don't need to change value while holding the lock, we just want
        # to notify waiting threads
        with self.read_status_change:
            self.stop_reading = value
            self.read_status_change.notify_all()

    def _set_default_flight_location(self) -> None:
        """Try to set default flight location and port from WS."""
        if not os.environ.get('FLIGHT_SERVICE_LOCATION') and self._wml_client and self._wml_client.CLOUD_PLATFORM_SPACES:
            try:
                flight_location = self._wml_client.PLATFORM_URLS_MAP[self._wml_client.wml_credentials['url']].replace('https://', '')
            except Exception as e:
                if self._wml_client.wml_credentials['url'] in self._wml_client.PLATFORM_URLS_MAP.values():
                    flight_location = self._wml_client.wml_credentials['url'].replace('https://', '')
                else:
                    raise e
            flight_port = 443
        else:
            host = os.environ.get('ASSET_API_SERVICE_HOST', os.environ.get('CATALOG_API_SERVICE_HOST'))

            if host is None or 'api.' not in host:
                default_service_url = os.environ.get('RUNTIME_FLIGHT_SERVICE_URL', 'grpc+tls://wdp-connect-flight:443')
                default_service_url = default_service_url.split('//')[-1]
                flight_location = os.environ.get('FLIGHT_SERVICE_LOCATION')
                flight_port = os.environ.get('FLIGHT_SERVICE_PORT')

                if flight_location is None or flight_location == '':
                    flight_location = default_service_url.split(':')[0]

                if flight_port is None or flight_port == '':
                    flight_port = default_service_url.split(':')[-1]

            else:
                flight_location = host
                flight_port = '443'

        self.flight_location = flight_location
        self.flight_port = flight_port

        logger.debug(f"Flight location: {self.flight_location}")
        logger.debug(f"Flight port: {self.flight_port}")

    def authenticate(self) -> 'flight.ClientAuthHandler':
        """Creates an authenticator object for Flight Service."""

        class TokenClientAuthHandler(flight.ClientAuthHandler):
            """Authenticator implementation from pyarrow flight."""

            def __init__(self, token, _type: str, impersonate: bool = False):
                super().__init__()
                if impersonate:
                    self.token = bytes(f'{token}', 'utf-8')
                else:
                    self.token = bytes(f'{_type} ' + token, 'utf-8')

            def authenticate(self, outgoing, incoming):
                outgoing.write(self.token)
                self.token = incoming.read()

            def get_token(self):
                logger.debug(f"Flight service get_token() {self.token}")
                return self.token

        if 'Bearer' in self.headers.get('Authorization', ''):
            if "impersonate" in self.headers:
                authorization_header = self.headers.get('Authorization', 'Bearer  ')
                impersonate_header = self.headers.get('impersonate')
                auth_json_str = json.dumps(dict(authorization=authorization_header, impersonate=impersonate_header))
                return TokenClientAuthHandler(token=auth_json_str, _type='json_string', impersonate=True)
            else:
                return TokenClientAuthHandler(token=self.headers.get('Authorization', 'Bearer  ').split('Bearer ')[-1],
                                              _type='Bearer')

        elif 'Basic' in self.headers.get('Authorization', ''):
            if "impersonate" in self.headers:
                authorization_header = self.headers.get('Authorization', 'Basic  ')
                impersonate_header = self.headers.get('impersonate')
                auth_json_str = json.dumps(dict(authorization=authorization_header, impersonate=impersonate_header))
                return TokenClientAuthHandler(token=auth_json_str, _type='json_string', impersonate=True)
            else:
                return TokenClientAuthHandler(token=self.headers.get('Authorization', 'Basic  ').split('Basic ')[-1],
                                              _type='Basic')

        else:
            return TokenClientAuthHandler(token=self.headers.get('Authorization'), _type='Bearer')

    def get_endpoints(self) -> Iterable[List['flight.FlightEndpoint']]:
        """Listing all available Flight Service endpoints (one endpoint corresponds to one batch)"""
        try:
            self.flight_client.authenticate(self.authenticate())
        except Exception as e:
            # suggest CPD users to check the Flight variables
            if hasattr(self._wml_client, 'ICP'):
                if self._wml_client.ICP:
                    raise ConnectionError(f"Cannot connect to the Flight service. Please make sure you set correct "
                                          f"FLIGHT_SERVICE_LOCATION and FLIGHT_SERVICE_PORT environmental variables."
                                          f"Error: {e}")
            else:
                raise ConnectionError(f"Cannot connect to the Flight service. Error: {e}")

        try:

            for source_command in self._select_source_command():
                info = self.flight_client.get_flight_info(
                    flight.FlightDescriptor.for_command(source_command)
                )

                yield info.endpoints

        except flight.FlightInternalError as e:
            logger.debug(f"Caught FlightInternalError in get_endpoints: {str(e)}")
            if 'CDICO2034E' in str(e):
                if 'The property [infer_schema] is not supported.' in str(e):
                    for source_command in self._select_source_command(infer_schema=False):
                        info = self.flight_client.get_flight_info(
                            flight.FlightDescriptor.for_command(source_command)
                        )
                        yield info.endpoints

                elif 'The property [infer_as_varchar] is not supported.' in str(e):
                    # Don't sent infer_as_varchar in flight command and try again.
                    for source_command in self._select_source_command(_use_infer_as_varchar=False):
                        info = self.flight_client.get_flight_info(
                            flight.FlightDescriptor.for_command(source_command)
                        )
                        yield info.endpoints
                elif 'The property [quote_character]' in str(e):
                    # Don't sent quote_character in flight command if it is not yet supported and try again.
                    self.params['quote_character'] = None
                    for source_command in self._select_source_command():
                        info = self.flight_client.get_flight_info(
                            flight.FlightDescriptor.for_command(source_command)
                        )
                        yield info.endpoints

                else:
                    raise WrongLocationProperty(reason=str(e))

            elif 'CDICO2015E' in str(e):
                raise WrongFileLocation(reason=str(e))

            elif 'CDICO9999E' in str(e):
                if 'Bad Request' in str(e):
                    for source_command in self._select_source_command(infer_schema=False):
                        info = self.flight_client.get_flight_info(
                            flight.FlightDescriptor.for_command(source_command)
                        )
                        yield info.endpoints

                else:
                    raise WrongLocationProperty(reason=str(e))
            else:
                raise e

    def _get_data(self,
                  thread_number: int,
                  endpoint: 'flight.FlightEndpoint') -> None:
        """
        Read data from Flight Service (only one batch).

        Properties
        ----------
        thread_number: int, required
            Specific number of the downloading thread.

        endpoint: flight.FlightEndpoint, required

        Returns
        -------
        pd.DataFrame with batch data
        """
        try:
            reader = self.flight_client.do_get(endpoint.ticket)
            mb_counter = 0

            while True:
                mb_counter += 1
                data, row_size = self._read_chunk(thread_number=thread_number, reader=reader, mb_counter=mb_counter)

                if row_size != 0:  # append batches only when we have data
                    if not self.stop_reading:
                        self._chunk_queue_check(data=data, thread_number=thread_number)

                        if self.enable_subsampling:
                            # put all data into further subsampling
                            logger.debug(f"GD {thread_number}: putting mini batch to the queue...")
                            self._q_put_nowait((thread_number, data))
                            logger.debug(f"GD {thread_number}: mini batch already put.")

                        else:
                            with self.lock_read:
                                self.total_size = self.total_size + row_size * len(data)

                                # note: what to do when we have total size nearly under the limit
                                if self.total_size <= self.data_size_limit:
                                    upper_row_limit = (self.data_size_limit - self.total_size) // row_size
                                    data = data.iloc[:upper_row_limit]
                                    self._q_put_nowait((thread_number, data))
                                # --- end note
                                else:
                                    self._q_put_nowait((thread_number, 0))  # finish this thread
                                    self._set_stop_reading(True)

                    else:
                        break

            logger.debug(f"GD {thread_number}: Finishing thread work...")
            self._q_put_nowait((thread_number, 0))  # finish this thread

        except StopIteration:
            # Reading of batch finished, result commited."
            self._q_put_nowait((thread_number, 0))

        except Exception as e:
            logger.debug(f"GD {thread_number}: Some error occurred. Error: {e}")
            self._q_put_nowait((thread_number, 0))
            self.threads_exceptions.append(str(e))

    @staticmethod
    def _cast_columns_to_float_64(data: 'pd.DataFrame') -> 'pd.DataFrame':
        """Flight Service will cast decfloat types to strings, we need to cast them to correct types."""
        for i, (col_name, col_type) in enumerate(zip(data.dtypes.index, data.dtypes)):

            if col_type == 'object':
                try:
                    data[col_name] = data[col_name].astype('float64')

                except ValueError:  # ignore when column cannot be cast to other type than string
                    logger.debug(f"Column '{col_name}' cannot be casted to float64 as it has normal strings inside")
                    pass

                except Exception as e:
                    logger.debug(f"Casting data column '{col_name}' error: {e}")
                    pass

        return data

    def _process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Process data columns and log data size"""
        data = self._cast_columns_to_float_64(data)
        if len(data) < 100 and self.enable_subsampling:
            raise ValueError(f"We do not have enough rows {len(data)} / minimum 100")

        logger.debug(f"BATCH SIZE: {sys.getsizeof(data)} Bytes")
        return data

    def _read_chunk(self, thread_number: int, reader: 'flight.FlightStreamReader', mb_counter: int):
        """Provides unified reading method for flight chunks."""
        logger.debug(f"RC {thread_number}: Waiting for next mini batch from Flight Service...")
        # Flight Service could split one batch into several chunks to have better performance
        mini_batch, metadata = reader.read_chunk()
        logger.debug(f"RC {thread_number}: Mini batch received from Flight Service.")
        data = pa.Table.from_batches(batches=[mini_batch]).to_pandas()
        if len(data) == 1:
            row_size = sys.getsizeof(data.iloc[0].values)

        else:
            row_size = sys.getsizeof(data.iloc[:2]) - sys.getsizeof(data.iloc[:1])

        if self.row_size == 0:
            self.row_size = row_size

        mini_batch_size = sys.getsizeof(data)
        logger.debug(f"RC {thread_number}: downloading mini_batch: {mb_counter} / shape: {data.shape} "
                     f"/ size: {mini_batch_size}")

        with self.lock_read:
            self.downloaded_data_size += mini_batch_size

        if mb_counter % 10 == 0:
            logger.debug(f"RC {thread_number}: Total downloaded data size: "
                         f"{self.downloaded_data_size / 1024 / 1024}MB")

        return data, row_size

    def _chunk_queue_check(self, data: 'pd.DataFrame', thread_number: int):
        # note: check if queue is not too large, if it is, wait 3 sec and check again
        while True:
            if self.number_of_batch_rows is not None:
                data_rows = len(data) * self.q.qsize()
                if data_rows > self.number_of_batch_rows and not self.stop_reading:
                    logger.debug(f"QC {thread_number}: Waiting 3 sec as data queue is too large.")
                    logger.debug(
                        f"QC {thread_number}: Data queue size: {data_rows} rows, max rows per batch: "
                        f"{self.number_of_batch_rows}")
                    with self.read_status_change:
                        self.read_status_change.wait(timeout=3)
                    continue
                else:
                    break
            else:
                data_size = sys.getsizeof(data) * self.q.qsize()
                if data_size >= self.data_size_limit and not self.stop_reading:
                    logger.debug(f"QC {thread_number}: Waiting 3 sec as data queue is too large.")
                    logger.debug(
                        f"QC {thread_number}: Data queue size: {data_size / 1024 / 1024}MB, available memory: "
                        f"{self.data_size_limit / 1024 / 1024}MB")
                    with self.read_status_change:
                        self.read_status_change.wait(timeout=3)
                    continue
                else:
                    break
        # --- end note

    def _get_all_data_in_batches(self,
                                 thread_number: int,
                                 endpoint: 'flight.FlightEndpoint') -> None:
        """
        Read data from Flight Service.

        Properties
        ----------
        thread_number: int, required
            Specific number of the downloading thread.

        endpoint: flight.FlightEndpoint, required

        Returns
        -------
        pd.DataFrame with batch data
        """
        try:
            reader = self.flight_client.do_get(endpoint.ticket)
            mb_counter = 0

            while True:
                mb_counter += 1
                data, row_size = self._read_chunk(thread_number=thread_number, reader=reader, mb_counter=mb_counter)

                if row_size != 0 and not self.stop_reading:  # append batches only when we have data
                    self._chunk_queue_check(data=data, thread_number=thread_number)
                    logger.debug(f"RT {thread_number}: putting mini batch to the queue...")
                    self._q_put_nowait((thread_number, data))
                    logger.debug(f"RT {thread_number}: mini batch already put.")

                else:
                    break

            logger.debug(f"RT {thread_number}: Finishing thread work...")
            self._q_put_nowait((thread_number, 0))  # finish this thread

        except Exception as e:
            logger.debug(f"RT {thread_number}: Some error occurred. Error: {e}")
            self._q_put_nowait((thread_number, 0))
            self.threads_exceptions.append(str(e))

    def iterable_read(self) -> Generator:
        """
            Iterate over batches of data from Flight Service.

            How does it work?

            0. Read, create and yield a subsampled batch.
            1. Start separate threads per Flight partition to read mini batches.
            2. Eg. we have 5 separate threads that read the data (batch by batch and updates the queue).
            3. Start creating the logical batch by create_logical_batch() method. It will consume mini batches
                from the queue and try to create a logical bigger batch.
            4. We have defined a 'batch_queue' list variable that will be storing maximum of 2 logical batches at once.
                For each generated logical batch we perform the following actions:
                a) If 'batch_queue' is empty, append it with first logical batch
                b) Continue logical batch creation...
                c) If 'batch_queue' has one element (batch), append a new batch to it,
                    indicates that all Flight data reading threads need to stop downloading the data,
                d) Yield batch from the beginning of the list 'batch_queue'
                e) If we have control back, delete the first batch
                f) Unblock all Flight reading threads
                g) Yield second batch from 'batch_queue'
            5. When we do not have a control flow right now and something other is processing our batch,
                all Flight Threads are working and downloading next data... (we need to ensure that overall queue
                will not overwhelm RAM)
            6. When we get a control flow back, there will be a really fast logical bach creation as
                all of the mini batches needed are already stored in the memory.
        """
        self.callback.status_message("Starting reading training data in batches...")

        if self.enable_subsampling:
            for data in self.read():
                yield data
            self.enable_subsampling = False

        sequences = []

        for n, endpoints in enumerate(self.get_endpoints()):
            self.max_flight_batch_number = len(endpoints)  # when flight does not want to open more endpoints
            threads = []
            sequences.append(threads)

            for i, endpoint in enumerate(endpoints):
                reading_thread = threading.Thread(target=self._get_all_data_in_batches, args=(i, endpoint))
                threads.append(reading_thread)
                logger.debug(f"IR: Starting batch reading thread: {i}, sequence: {n}...")
                reading_thread.start()


        for n, batch in enumerate(self.create_logical_batch(timeout=60 * 60, _type='data')):
            logger.debug(f"IR: Logical batch number {n} received.")
            logger.debug(f"IR: Passing batch to upper layer.")
            yield batch
            logger.debug(f"IR: We have control back, creating next batch...")
            if n == 0 and self.stop_after_first_batch:
                self._set_stop_reading(True)
                break

    def read(self) -> 'pd.DataFrame':
        """Fetch the data from Flight Service. Fetching is done in batches.
            There is an upper top limit of data size to be fetched configured to 1 GB.

        Returns
        -------
        Pandas DataFrame with fetched data.
        """
        self.callback.status_message("Starting reading training data...")
        sequences = []

        def start_reading_threads():
            # Note: endpoints are created by Flight Service based on number of partitions configured
            # one endpoint serves multiple mini batches of the data
            try:
                if self.enable_subsampling:
                    subsampling_thread = threading.Thread(target=self._get_sampling_strategy(), args=(self.label,))
                    subsampling_thread.start()

                else:
                    normal_read_thread = threading.Thread(target=self.normal_read)
                    normal_read_thread.start()
                    

                for n, endpoints in enumerate(self.get_endpoints()):
                    self.max_flight_batch_number = len(endpoints)  # when flight does not want to open more endpoints
                    threads = []
                    sequences.append(threads)

                    for i, endpoint in enumerate(endpoints):
                        reading_thread = threading.Thread(target=self._get_data, args=(i, endpoint))
                        threads.append(reading_thread)
                        logger.debug(f"R: Starting batch reading thread: {i}, sequence: {n}...")

                        reading_thread.start()

            except Exception as e:
                self.row_size = -1  # further we raise an error to finish thread
                raise e
            finally:

                for n, sequence in enumerate(sequences):
                    for i, thread in enumerate(sequence):
                        logger.debug(f"R: Joining batch reading thread {i}, sequence: {n}...")

                        thread.join()

                self._q_put_nowait((-1, -1))  # send close queue message (stop reading logical batches)

                if self.enable_subsampling:
                    subsampling_thread.join()

                else:
                    normal_read_thread.join()

        try:
            start_reading_threads()

            # Log every partition thread error (should be the flight service info included)
            if self.threads_exceptions:
                logger.debug(f"R: Partitions Thread Errors: {self.threads_exceptions}")

                for msg in self.threads_exceptions:
                    if "Data could not be read" in msg:
                        raise TypeError(msg)

            if self.enable_subsampling:
                self.subsampled_data = self._process_data(self.subsampled_data)
                yield self.subsampled_data
            else:
                self.data = self._process_data(self.data)
                yield self.data

        except ValueError as e:
            if not self.fallback_to_one_connection:
                raise e

            timeout = 60 * 10
            self.callback.status_message(f"Parallel data connection problem, "
                                         f"fallback to 1 connection with {timeout} timeout.")
            logger.debug(f"Data merging error: {e}")
            logger.debug(f"Fallback to 1 connection. Timeout: {timeout}s")
            time.sleep(timeout)

            self.max_flight_batch_number = 1
            sequences = []
            self._q_reset()
            start_reading_threads()

            # Log every partition thread error (should be the flight service info included)
            if self.threads_exceptions:
                logger.debug(f"Partitions Thread Errors: {self.threads_exceptions}")

            try:
                if self.enable_subsampling:
                    self.subsampled_data = self._process_data(self.subsampled_data)
                    yield self.subsampled_data

                else:
                    self.data = self._process_data(self.data)
                    yield self.data

            except ValueError:
                raise DataStreamError(reason=str(self.threads_exceptions))

    def _get_max_rows(self, _type: str) -> int:
        if self.number_of_batch_rows is not None:
            return self.number_of_batch_rows

        while True:
            if self.row_size == -1:
                raise TypeError("Data could not be read. Try to use a binary read mode.")

            if self.row_size != 0:
                if _type == 'data':
                    return self.data_size_limit // self.row_size

                else:
                    return self.logical_batch_size_limit // self.row_size

            else:
                time.sleep(1)

    def regression_random_sampling(self, label_column: str) -> None:
        """Start collecting sampled data (random sample for regression problem)"""
        logger.debug(f"Starting regression random sampling.")
        max_rows = self._get_max_rows(_type='data')
        downloaded_data_size = 0

        for data in self.create_logical_batch():
            data_size = sys.getsizeof(data)
            downloaded_data_size += data_size
            self.callback.status_message(f"Downloaded data size: {downloaded_data_size // 1024 // 1024} MB")
            logger.debug(f"Logical batch size: {data_size}")

            # simple preprocess before sampling
            data.dropna(inplace=True, subset=[label_column])

            # join previous sampled batch with new one
            if self.subsampled_data is not None:
                data = pd.concat([self.subsampled_data, data])

            if len(data) <= max_rows:
                self.subsampled_data = data

            else:
                self.subsampled_data = data.sample(n=max_rows, random_state=0, axis=0)

            logger.debug(f"Subsampled batch size: {sys.getsizeof(self.subsampled_data)}")

    def stratified_subsampling(self, label_column: str) -> None:
        """Start collecting sampled data (stratified sample for classification problem)"""
        logger.debug(f"Starting classification stratified sampling.")
        max_rows = self._get_max_rows(_type='data')
        downloaded_data_size = 0

        for data in self.create_logical_batch():
            data_size = sys.getsizeof(data)
            downloaded_data_size += data_size
            self.callback.status_message(f"Downloaded data size: {downloaded_data_size // 1024 // 1024} MB")
            logger.debug(f"Logical batch size: {data_size}")

            # simple preprocess before sampling
            data.dropna(inplace=True, subset=[label_column])
            stats = data[label_column].value_counts()
            indexes = stats[stats == 1].index.values
            for i in indexes:
                logger.debug(f"Unique value in label column: {i}")
                data = data[data[label_column] != i]

            # join previous sampled batch with new one
            if self.subsampled_data is not None:
                data = pd.concat([self.subsampled_data, data])

            if len(data) <= max_rows:
                self.subsampled_data = data

            else:
                from sklearn.model_selection import StratifiedShuffleSplit
                sss = StratifiedShuffleSplit(n_splits=1, train_size=max_rows, random_state=0)

                # start sampling and rewrite new subsampled batch
                for train_index, _ in sss.split(data.drop([label_column], axis=1).values, data[label_column].values):
                    self.subsampled_data = data.iloc[train_index]

            logger.debug(f"Subsampled batch size: {sys.getsizeof(self.subsampled_data)}")

    def normal_read(self):
        """Start collecting all the data when user do not want to subsample.
        This should be limited to the max data size 1GB, see limitation implementation in self._read_data().
        """
        for data in self.create_logical_batch():
            self.data = data
            break

    def create_logical_batch(self, timeout: int = 60 * 10, _type: str = 'logical') -> 'pd.DataFrame':
        """Creates a logical batch for sampling, logical batch is larger ~2GB.
        If used with normal read, it will return all of the collected data, max 1GB based on a limitation.
        """
        max_rows = self._get_max_rows(_type=_type)
        logical_batch = []
        mini_batch_counter = 0
        threads_finished = 0

        while True:
            try:
                if threads_finished == self.max_flight_batch_number:
                    yield pd.concat(logical_batch)  # flush last data
                    break

                logger.debug("LB: Waiting for mini batch to appear in the queue...")
                thread_number, data = self._q_get(timeout=timeout)  # wait max 10 min

                self.q.task_done()
                logger.debug(f"LB: Mini batch received and taken from the queue. Batch from thread: {thread_number}")

                # when the last thread finish reading (finish sequence (-1, -1))
                if isinstance(data, int) and thread_number == -1 and data == -1:
                    yield pd.concat(logical_batch)  # flush last data
                    break

                # when not the last thread finished reading, continue
                elif isinstance(data, int):
                    threads_finished += 1
                    continue

                mini_batch_counter += 1

                logger.debug(f"LB: Mini batch number: {mini_batch_counter}")

            except queue.Empty:
                raise DataStreamError(reason=f'LB: Timeout on waiting for data batch... max {timeout / 60} minutes.')

            logical_batch.append(data.iloc[:max_rows])
            max_rows = max_rows - len(logical_batch[-1])

            if max_rows > 0:
                continue

            else:
                logger.debug("LB: Yielding logical batch!")
                yield pd.concat(logical_batch)

                rows = len(logical_batch[-1])
                logical_batch = [data.iloc[rows + 1:]]
                max_rows = self._get_max_rows(_type=_type) - len(logical_batch[-1])

    def _select_source_command(self, infer_schema: bool = True, _use_infer_as_varchar: bool = True) -> List[str]:
        """Based on a data source type, select appropriate commands for flight service configuration."""

        infer_schema = infer_schema
        if self.read_binary:
            infer_schema = False

        if self.write_binary:
            command = {"interaction_properties": {'write_mode': "write_raw"}}

        else:
            # limitation for number of rows passed within one mini batch
            # from flight service (can be between 100 and 10000)
            # need to test performance with big data
            default_batch_size = 10000
            # when reading binary batches, default row is one value of 32k.
            # If we keep a large default batch size like 10k, we end up with
            # batches of 300MB being read and kept in memory as 10k chunks
            # of 32k. This clutters the memory and is more work for GC.
            # Defaulting to 1000 when reading binary to decrease footprint.
            if self.read_binary:
                default_batch_size = 1000
            # when dataset is small we received empty dfs, it is ok (4 is optimum for larger than 1 GB)
            command = {
                "num_partitions": self.max_flight_batch_number if self.max_flight_batch_number is not None else DEFAULT_PARTITIONS_NUM,
                "batch_size": default_batch_size,
                "interaction_properties": {}
            }

        if self.extra_interaction_properties is not None:
            command["interaction_properties"].update(self.extra_interaction_properties)

        command.update(self.flight_parameters)

        if self.number_of_batch_rows is not None:
            command['batch_size'] = self.number_of_batch_rows

        if self.space_id is not None:
            command['space_id'] = self.space_id

        elif self.project_id is not None:
            command['project_id'] = self.project_id

        if self.read_binary:
            command['interaction_properties'].update({'read_mode': "read_raw"})

        if self.asset_id:
            command['asset_id'] = self.asset_id
            if infer_schema:
                command['interaction_properties'].update({'infer_schema': "true"})

        elif self.connection_id:
            command['asset_id'] = self.connection_id

        if 'bucket' in self.data_location['location']:
            if self.data_location.get('location', {}).get('path', None) is None \
                    and 'file_name' in self.data_location.get('location', ''):
                self.data_location['location']['path'] = self.data_location['location']['file_name']
            command['interaction_properties'].update(prepare_interaction_props_for_cos(
                self.params, self.data_location['location']['path']))

            if 'file_format' in command['interaction_properties'] and ('write_mode' in command[
                'interaction_properties'] or self.read_binary):
                del command['interaction_properties']['file_format']

            if 'sheet_name' in command['interaction_properties'] and ('write_mode' in command[
                'interaction_properties'] or self.read_binary):
                del command['interaction_properties']['sheet_name']

            if 'encoding' in command['interaction_properties'] and ('write_mode' in command[
                'interaction_properties'] or self.read_binary):
                del command['interaction_properties']['encoding']

            if infer_schema:
                command['interaction_properties']['infer_schema'] = "true"
            command['interaction_properties']['file_name'] = self.data_location['location']['path']
            command['interaction_properties']['bucket'] = self.data_location['location']['bucket']

        elif 'schema_name' in self.data_location['location']:
            command['interaction_properties']['schema_name'] = self.data_location['location']['schema_name']
            command['interaction_properties']['table_name'] = self.data_location['location']['table_name']

        elif not self.asset_id:
            command['interaction_properties'].update(self.data_location['location'])
            if infer_schema:
                command['interaction_properties']['infer_schema'] = "true"

        # Property 'infer_as_varchar` needs to be false, when 'infer_schema' is true
        if command['interaction_properties'].get('infer_schema', "false") == "true" and _use_infer_as_varchar:
            command['interaction_properties'].update({'infer_as_varchar': "false"})

        # Git based project assets property
        if self.data_location is not None and self.data_location['location'].get('userfs'):
            command.update({'userfs': True})

        if 'path' in command['interaction_properties']:
            command['interaction_properties']['file_name'] = command['interaction_properties']['path']
            del command['interaction_properties']['path']

        if 'connection_properties' not in command:
            logger.debug(f"Command: {command}")

        return [json.dumps(command)]

    def read_binary_data(self, read_to_file=None) -> None:
        """Try to read data from flight service using the 'read_raw' parameter. This will allow to fetch binary data.
            Binary read should be used for small data, like json files, zip files etc. not for the big datasets as
            each data batch is joined to the previous one in-memory.
        """
        self.read_binary = True

        if self.flight_parameters.get('num_partitions') is None:
            self.flight_parameters['num_partitions'] = 1
            self.max_flight_batch_number = 1

        cm = open(read_to_file, 'wb') if read_to_file else nullcontext()
        with cm as sink:
            binary_data_array = []
            for n, endpoints in enumerate(self.get_endpoints()):
                for i, endpoint in enumerate(endpoints):
                    reader = self.flight_client.do_get(endpoint.ticket)
                    try:
                        while True:
                            mini_batch, metadata = reader.read_chunk()
                            if read_to_file:
                                sink.write(b''.join(mini_batch.columns[0].tolist()))
                            else:
                                binary_data_array.extend(mini_batch.columns[0].tolist())
                    except StopIteration:
                        pass
        if read_to_file:
            return [read_to_file]
        else:
            binary_data_container = b''.join(binary_data_array)
            yield binary_data_container

    def write_binary_data(self, file_path: str) -> None:
        """Write data in 16MB binary data blocks. 16MB upper limit is set by the Flight Service.
            The writer will open the source local file and will stream one batch of 16MB to the Flight.
            Only 16MB of data is loaded into the memory at a time.

        Parameters
        ----------
        file_path: str, required
            Path to the source file.
        """
        self.write_binary = True
        schema = pa.schema([
            ('content', pa.binary())
        ])
        commands = self._select_source_command(infer_schema=False)

        self.flight_client.authenticate(self.authenticate())
        writer, reader = self.flight_client.do_put(flight.FlightDescriptor.for_command(commands[0]), schema)

        with writer:
            batch_max_size = 16770000  # almost 16MB

            with open(file_path, 'rb') as file:
                for block in iter(partial(file.read, batch_max_size), b''):
                    writer.write_batch(pa.record_batch([pa.array([block], type=pa.binary())], schema=schema))
                    self.flight_client.wait_for_available()

    def write_data(self, data: 'pd.DataFrame'):
        """Write data from pandas DataFrame. The limit is 16MB dataframe as this is the upper batch size limit.
        Upper layer should fallback to use binary write.
        """
        schema = pa.Schema.from_pandas(data)
        commands = self._select_source_command(infer_schema=False)

        self.flight_client.authenticate(self.authenticate())
        writer, reader = self.flight_client.do_put(flight.FlightDescriptor.for_command(commands[0]), schema)

        with writer:
            writer.write_table(pa.Table.from_pandas(data))
            self.flight_client.wait_for_available()

        return writer, reader

    def get_batch_writer(self, schema: 'pa.Schema') -> 'FlightStreamWriter':
        """Prepare FlightStreamWriter and return it."""
        commands = self._select_source_command(infer_schema=False)

        self.flight_client.authenticate(self.authenticate())
        writer, reader = self.flight_client.do_put(flight.FlightDescriptor.for_command(commands[0]), schema)
        return writer


    def _get_sampling_strategy(self):
        """
        Return sampling strategy for given sampling and learning type.
        """
        random_sampling_pred_types = (
            PredictionType.REGRESSION,
        )
        stratified_sampling_pred_types = (
            PredictionType.CLASSIFICATION, PredictionType.BINARY, PredictionType.MULTICLASS
        )

        if self.sampling_type == SamplingTypes.RANDOM and self.learning_type in random_sampling_pred_types:
            return self.regression_random_sampling
        elif self.sampling_type == SamplingTypes.STRATIFIED and self.learning_type in stratified_sampling_pred_types:
            return self.stratified_subsampling
        else:
            raise InvalidSamplingType(self.sampling_type, self.learning_type)
