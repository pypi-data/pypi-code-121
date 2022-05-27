from ._pandas_helper import (have_pandas, have_pyarrow, ensure_df_native_compat, PandasImportError, pyarrow_supports_cdata)
from ._dataflow_script_resolver import resolve_script
from .engineapi.api import get_engine_api
from .engineapi.engine import CancellationToken
from .engineapi.typedefinitions import ExecuteAnonymousActivityMessageArguments, AnonymousActivityData, IfDestinationExists
from .errorhandlers import OperationCanceled, UnexpectedError, ExecutionError
from .step import steps_to_block_datas
from ._rslex_executor import get_rslex_executor, use_rslex, _RsLexDisabledException
import io
import os
import json
import math
import warnings
from shutil import rmtree
from threading import Event, Thread, RLock
from typing import List
from uuid import uuid4
from ._loggerfactory import _LoggerFactory, trace

logger = _LoggerFactory.get_logger("DataframeReader")
tracer = trace.get_tracer(__name__)


# 20,000 rows gives a good balance between memory requirement and throughput by requiring that only
# (20000 * CPU_CORES) rows are materialized at once while giving each core a sufficient amount of
# work.
PARTITION_SIZE = 20000


class _InconsistentSchemaError(Exception):
    def __init__(self, reason: str):
        super().__init__('Inconsistent or mixed schemas detected across partitions: ' + reason)


# noinspection PyPackageRequirements
class _PartitionIterator:
    def __init__(self, partition_id, table):
        self.id = partition_id
        self.is_canceled = False
        self._completion_event = Event()
        self._current_idx = 0
        import pandas as pd
        self._dataframe = table.to_pandas() if not isinstance(
            table, pd.DataFrame) else table

    def __next__(self):
        if self._current_idx == len(self._dataframe):
            self._completion_event.set()
            raise StopIteration

        value = self._dataframe.iloc[self._current_idx]
        self._current_idx = self._current_idx + 1
        return value

    def wait_for_completion(self):
        self._completion_event.wait()

    def cancel(self):
        self.is_canceled = True
        self._completion_event.set()


# noinspection PyProtectedMember
class RecordIterator:
    def __init__(self, dataflow: 'azureml.dataprep.Dataflow', cancellation_token: CancellationToken):
        self._iterator_id = str(uuid4())
        self._partition_available_event = Event()
        self._partitions = {}
        self._current_partition = None
        self._next_partition = 0
        self._done = False
        self._cancellation_token = cancellation_token
        get_dataframe_reader().register_iterator(self._iterator_id, self)
        _LoggerFactory.trace(logger, "RecordIterator_created", {'iterator_id': self._iterator_id})

        def start_iteration():
            dataflow_to_execute = dataflow.add_step('Microsoft.DPrep.WriteFeatherToSocketBlock', {
                'dataframeId': self._iterator_id,
            })

            try:
                get_engine_api().execute_anonymous_activity(
                    ExecuteAnonymousActivityMessageArguments(anonymous_activity=AnonymousActivityData(
                        blocks=steps_to_block_datas(dataflow_to_execute._steps))),
                    cancellation_token=self._cancellation_token)
            except OperationCanceled:
                pass
            self._clean_up()

        iteration_thread = Thread(target=start_iteration, daemon=True)
        iteration_thread.start()

        cancellation_token.register(self.cancel_iteration)

    def __next__(self):
        while True:
            if self._done and self._current_partition is None and len(self._partitions) == 0:
                raise StopIteration()

            if self._current_partition is None:
                if self._next_partition not in self._partitions:
                    self._partition_available_event.wait()
                    self._partition_available_event.clear()
                    continue
                else:
                    self._current_partition = self._partitions[self._next_partition]
                    self._next_partition = self._next_partition + 1

            if self._current_partition is not None:
                try:
                    return next(self._current_partition)
                except StopIteration:
                    self._partitions.pop(self._current_partition.id)
                    self._current_partition = None

    def cancel_iteration(self):
        for partition in self._partitions.values():
            partition.cancel()
        self._clean_up()

    def process_partition(self, partition: int, table: 'pyarrow.Table'):
        if self._cancellation_token.is_canceled:
            raise RuntimeError('IteratorClosed')

        partition_iter = _PartitionIterator(partition, table)
        self._partitions[partition] = partition_iter
        self._partition_available_event.set()
        partition_iter.wait_for_completion()
        if partition_iter.is_canceled:
            raise RuntimeError('IteratorClosed')

    def _clean_up(self):
        _LoggerFactory.trace(logger, "RecordIterator_cleanup", {'iterator_id': self._iterator_id})
        get_dataframe_reader().complete_iterator(self._iterator_id)
        self._done = True
        self._partition_available_event.set()


class RecordIterable:
    def __init__(self, dataflow):
        self._dataflow = dataflow
        self._cancellation_token = CancellationToken()

    def __iter__(self) -> RecordIterator:
        return RecordIterator(self._dataflow, self._cancellation_token)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._cancellation_token.cancel()

def log_rslex_error_diff(action: str, rslex_error: Exception, clex_error: Exception):
    try:
        if clex_error is None or type(clex_error) is ExecutionError:
            _LoggerFactory.trace(logger, action, {
                'only_rslex_failed': clex_error is None,
                'rslex_error_code': 'N/A',
                'rslex_error_message': str(rslex_error),
                'clex_error_code': clex_error.error_code if clex_error is not None else '',
                'clex_error_message': clex_error.compliant_message if clex_error is not None else '',
                })
        else:
            _LoggerFactory.trace(logger, action, {
                    'only_rslex_failed': clex_error is None,
                    'rslex_error_type': str(rslex_error),
                    'clex_error_type': type(clex_error).__name__ if clex_error is not None else ''
            })
    except Exception:
        pass

def _write_preppy_with_fallback(activity, dataflow, force_clex=False, span_context=None):
    import tempfile
    from pathlib import Path
    import os

    random_id = uuid4()
    subfolder = "{}_{}".format(random_id, os.getpid())
    intermediate_path = Path(os.path.join(tempfile.gettempdir(), subfolder))
    dataflow_to_execute = dataflow.add_step('Microsoft.DPrep.WritePreppyBlock', {
        'outputPath': {
            'target': 0,
            'resourceDetails': [{'path': str(intermediate_path)}]
        },
        'profilingFields': ['Kinds', 'MissingAndEmpty'],
        'ifDestinationExists': IfDestinationExists.REPLACE
    })

    _execute_with_fallback(activity, dataflow_to_execute, force_clex=force_clex, span_context=span_context)

    if not (intermediate_path / '_SUCCESS').exists():
        error = 'Missing _SUCCESS sentinel in preppy folder.'
        logger.error(error)
        raise UnexpectedError(error)

    intermediate_files = [str(p) for p in intermediate_path.glob('part-*')]
    intermediate_files.sort()
    return intermediate_files

def _execute_with_fallback(activity, dataflow_to_execute, force_clex=False, span_context=None):
    def rslex_execute():
        executor = get_rslex_executor()
        script = resolve_script(dataflow_to_execute)
        _ = executor.execute_script(script,
                                    False,
                                    # Following 3 arguments don't matter for execution that doesn't collect 
                                    fail_on_error=False,
                                    fail_on_mixed_types=False,
                                    fail_on_out_of_range_datetime=False,
                                    traceparent=span_context.span_id if span_context else '')

    def clex_execute():
        from .dataflow import Dataflow
        activity_data = Dataflow._dataflow_to_anonymous_activity_data(dataflow_to_execute)
        dataflow_to_execute._engine_api.execute_anonymous_activity(
            ExecuteAnonymousActivityMessageArguments(
                anonymous_activity=activity_data,
                span_context=span_context
            )
        )

    rslex_error = None
    clex_error = None
    try:
        if not force_clex:
            try:
                rslex_execute()
            except _RsLexDisabledException:
                _LoggerFactory.trace(logger, "RusteLex disabled. Falling back to CLex.", {'activity': activity})
                force_clex = True
            except Exception as e:
                rslex_error = e
                logger.info('rslex write preppy failed, falling back to clex.')    
        
        if force_clex or rslex_error is not None:
            try:
                clex_execute()
            except Exception as e:
                clex_error = e
                raise
    finally:
        if not force_clex and rslex_error is not None:
            log_rslex_error_diff("write_preppy_error", rslex_error, clex_error)

def _get_partition_count_with_rslex(dataflow, span_context=None):
    executor = get_rslex_executor()
    script = resolve_script(dataflow)
    return executor.get_partition_count(script, traceparent=span_context.span_id if span_context else '')


# noinspection PyProtectedMember,PyPackageRequirements
class _DataFrameReader:
    def __init__(self, script=None):
        self._outgoing_dataframes = {}
        self._incoming_dataframes = {}
        self._iterators = {}
        self._script= script
        _LoggerFactory.trace(logger, "DataframeReader_create")

    def to_pandas_dataframe(self,
                            dataflow: 'azureml.dataprep.Dataflow',
                            extended_types: bool = False,
                            nulls_as_nan: bool = True,
                            on_error: str = 'null',
                            out_of_range_datetime: str = 'null',
                            span_context: 'DPrepSpanContext' = None) -> 'pandas.DataFrame':
        def to_pandas_preppy(force_clex=False):
            if not extended_types:
                warnings.warn('Please install pyarrow>=0.16.0 for improved performance of to_pandas_dataframe. '
                              'You can ensure the correct version is installed by running: pip install '
                              'pyarrow>=0.16.0 --upgrade')
            try:
                intermediate_files = _write_preppy_with_fallback('to_pandas_preppy', dataflow, force_clex, span_context)

                try:
                    from azureml.dataprep.native import preppy_to_ndarrays
                    from collections import OrderedDict
                    dataset = preppy_to_ndarrays(intermediate_files, extended_types, nulls_as_nan)
                except Exception as e:
                    error = 'Error from preppy_to_ndarrays: {}'.format(repr(e))
                    logger.error(error)
                    
                    try:
                        intermediate_files = _write_preppy_with_fallback('to_pandas_preppy_fallback', dataflow, True, span_context)
                        dataset = preppy_to_ndarrays(intermediate_files, extended_types, nulls_as_nan)
                    except Exception as ex:
                        error = 'Error from preppy_to_ndarrays_fallback: {}'.format(repr(ex))
                        logger.error(error)
                        raise UnexpectedError(error) from ex
                
                df = pandas.DataFrame.from_dict(OrderedDict(dataset))
                return df
            finally:
                try:
                    rmtree(intermediate_path, ignore_errors=True)
                except:
                    pass  # ignore exception

        def clex_feather_to_pandas():
            random_id = str(uuid4())
            self.register_incoming_dataframe(random_id)
            dataflow_to_execute = dataflow.add_step('Microsoft.DPrep.WriteFeatherToSocketBlock', {
                'dataframeId': random_id,
                'errorStrategy': dataflow._on_error_to_enum_value(on_error),
                'dateTimeSettings': dataflow._out_of_range_datetime_to_block_value(out_of_range_datetime)
            })

            activity_data = dataflow_to_execute._dataflow_to_anonymous_activity_data(dataflow_to_execute)
            dataflow._engine_api.execute_anonymous_activity(
                ExecuteAnonymousActivityMessageArguments(anonymous_activity=activity_data, span_context=span_context))

            try:
                return self.complete_incoming_dataframe(random_id)
            except _InconsistentSchemaError as e:
                reason = e.args[0]
                warnings.warn('Using alternate reader. ' + reason)
                return to_pandas_preppy()

        def rslex_arrow_to_pandas():
            random_id = str(uuid4())
            self.register_incoming_dataframe(random_id)
            executor = get_rslex_executor()
            script = resolve_script(dataflow)
            (record_batches, stream_columns) = executor.execute_script(script,
                                                     True, 
                                                     fail_on_error=on_error != 'null',
                                                     fail_on_mixed_types=on_error != 'null',
                                                     fail_on_out_of_range_datetime=out_of_range_datetime != 'null',
                                                     traceparent=span_context.span_id if span_context is not None else '')

            if record_batches is None:
                raise RuntimeError("Got no record batches from rslex execution.")

            incoming_dfs = {}
            import pyarrow
            self._incoming_dataframes[random_id] = incoming_dfs
            for i in range(0, len(record_batches)):
                incoming_dfs[i] = pyarrow.Table.from_batches([record_batches[i]])

            return self.complete_incoming_dataframe(random_id, partition_stream_columns=stream_columns)

        if not have_pandas():
            raise PandasImportError()
        else:
            import pandas

        dataflow._raise_if_missing_secrets()
        
        # Test forcing a specific path section
        if '_TEST_USE_CLEX' in os.environ and os.environ['_TEST_USE_CLEX'] == 'False':
            if self._script:
                return self._to_pandas_arrow_rslex(self._script)
            else:
                return rslex_arrow_to_pandas()
        elif '_TEST_USE_CLEX' in os.environ and os.environ['_TEST_USE_CLEX'] == 'True':
            if have_pyarrow() and not extended_types:
                try:
                    return clex_feather_to_pandas()
                except _InconsistentSchemaError as e:
                    pass
            
            return to_pandas_preppy(force_clex=True)
        
        inconsistent_schema = False
        rslex_error = None
        clex_error = None
        try:
            if have_pyarrow() and pyarrow_supports_cdata() and not extended_types:
                try:
                    if self._script:
                        return self._to_pandas_arrow_rslex(self._script)
                    else:
                        return rslex_arrow_to_pandas()
                except _InconsistentSchemaError as e:
                    inconsistent_schema = True
                    reason = e.args[0]
                    warnings.warn('Using alternate reader. ' + reason)
                except Exception as e:
                    logger.info('rslex arrow failed, falling back to clex.')  
                    rslex_error = e
                    pass
            if have_pyarrow() and not extended_types and not inconsistent_schema:
                # if arrow is supported, and we didn't get inconsistent schema, and extended typed were not asked for - fallback to feather
                return clex_feather_to_pandas()
        except _InconsistentSchemaError as e:
            reason = e.args[0]
            warnings.warn('Using alternate reader. ' + reason)
        except Exception as e:
            clex_error = e
            raise
        finally:
            if rslex_error is not None:
                log_rslex_error_diff("get_arrow_error", rslex_error, clex_error)
        # this will do write to preppy attempt with fallback    
        return to_pandas_preppy(force_clex=False)

    def _to_pandas_arrow_rslex(self, script):
        executor = get_rslex_executor()
        (record_batches, _, stream_columns) = executor.execute_rsdataflow(script)
        random_id = str(uuid4())

        incoming_dfs = {}
        import pyarrow
        self._incoming_dataframes[random_id] = incoming_dfs
        for i in range(0, len(record_batches)):
            incoming_dfs[i] = pyarrow.Table.from_batches([record_batches[i]])

        return self.complete_incoming_dataframe(random_id, partition_stream_columns=stream_columns)


    def register_outgoing_dataframe(self, dataframe: 'pandas.DataFrame', dataframe_id: str):
        _LoggerFactory.trace(logger, "register_outgoing_dataframes", {'dataframe_id': dataframe_id})
        self._outgoing_dataframes[dataframe_id] = dataframe

    def unregister_outgoing_dataframe(self, dataframe_id: str):
        self._outgoing_dataframes.pop(dataframe_id)

    def _get_partitions(self, dataframe_id: str) -> int:
        dataframe = self._outgoing_dataframes[dataframe_id]
        partition_count = math.ceil(len(dataframe) / PARTITION_SIZE)
        return partition_count

    def _get_data(self, dataframe_id: str, partition: int) -> bytes:
        from azureml.dataprep import native
        dataframe = self._outgoing_dataframes[dataframe_id]
        start = partition * PARTITION_SIZE
        end = min(len(dataframe), start + PARTITION_SIZE)
        dataframe = dataframe.iloc[start:end]

        (new_schema, new_values) = ensure_df_native_compat(dataframe)

        return native.preppy_from_ndarrays(new_values, new_schema)

    def register_incoming_dataframe(self, dataframe_id: str):
        _LoggerFactory.trace(logger, "register_incoming_dataframes", {'dataframe_id': dataframe_id})
        self._incoming_dataframes[dataframe_id] = {}

    def complete_incoming_dataframe(self, dataframe_id: str, partition_stream_columns=None) -> 'pandas.DataFrame':
        import pyarrow
        import pandas as pd
        partitions_dfs = self._incoming_dataframes[dataframe_id]
        if any(isinstance(partitions_dfs[key], pd.DataFrame) for key in partitions_dfs):
            raise _InconsistentSchemaError('A partition has no columns.')

        partitions_dfs = \
            [partitions_dfs[key] for key in sorted(partitions_dfs.keys()) if partitions_dfs[key].num_rows > 0]
        _LoggerFactory.trace(logger, "complete_incoming_dataframes", {'dataframe_id': dataframe_id, 'count': len(partitions_dfs)})
        self._incoming_dataframes.pop(dataframe_id)

        if len(partitions_dfs) == 0:
            return pd.DataFrame({})

        def get_column_names(partition: pyarrow.Table) -> List[str]:
            return partition.schema.names

        def verify_column_names():
            def make_schema_error(prefix, p1_cols, p2_cols):
                return _InconsistentSchemaError(
                    '{0} The first partition has {1} columns. Found partition has {2} columns.\n'.format(prefix,
                                                                                                         len(p1_cols),
                                                                                                         len(p2_cols)) +
                    'First partition columns (ordered): {0}\n'.format(p1_cols) +
                    'Found Partition has columns (ordered): {0}'.format(p2_cols))

            expected_names = get_column_names(partitions_dfs[0])
            expected_count = partitions_dfs[0].num_columns
            row_count = 0
            size = 0
            for partition in partitions_dfs:
                row_count += partition.num_rows
                size += partition.nbytes
                found_names = get_column_names(partition)
                if partition.num_columns != expected_count:
                    _LoggerFactory.trace(logger, "complete_incoming_dataframes.column_count_mismatch", {'dataframe_id': dataframe_id})
                    raise make_schema_error('partition had different number of columns.', expected_names, found_names)
                for (a, b) in zip(expected_names, found_names):
                    if a != b:
                        _LoggerFactory.trace(logger, "complete_incoming_dataframes.column_names_mismatch", {'dataframe_id': dataframe_id})
                        raise make_schema_error('partition column had different name than expected.',
                                                expected_names,
                                                found_names)
            
            _LoggerFactory.trace(logger, "complete_incoming_dataframes.info", {'dataframe_id': dataframe_id, 'count': len(partitions_dfs), 'row_count': row_count, 'size_bytes': size})

        def determine_column_type(index: int) -> pyarrow.DataType:
            for partition in partitions_dfs:
                column = partition.column(index)
                if column.type != pyarrow.bool_() or column.null_count != column.length():
                    return column.type
            return pyarrow.bool_()

        def apply_column_types(fields: List[pyarrow.Field]):
            for i in range(0, len(partitions_dfs)):
                partition = partitions_dfs[i]
                column_types = partition.schema.types
                for j in range(0, len(fields)):
                    column_type = column_types[j]
                    if column_type != fields[j].type:
                        if column_type == pyarrow.bool_():
                            column = partition.column(j)
                            import numpy as np

                            def gen_n_of_x(n, x):
                                k = 0
                                while k < n:
                                    yield x
                                    k = k + 1
                            if isinstance(column, pyarrow.ChunkedArray):
                                typed_chunks = []
                                for chunk in column.chunks:
                                    typed_chunks.append(
                                        pyarrow.array(gen_n_of_x(chunk.null_count, None),
                                                      fields[j].type,
                                                      mask=np.full(chunk.null_count, True)))

                                partition = partition.remove_column(j)
                                try:
                                    partition = partition.add_column(j, fields[j], pyarrow.chunked_array(typed_chunks))
                                except Exception as e:
                                    message = "Failed to add colum to partition. Target type: {}, actual type: bool, partition id: {}, column idx: {}, error: {}, ".format(fields[j].type, i, j, e)
                                    logger.error(message)
                                    raise _InconsistentSchemaError(
                                        'A partition has a column with a different type than expected during append.\nThe type of column '
                                        '\'{0}\' in the first partition is {1}. In partition \'{2}\' found type is {3}.'
                                        .format(partition.schema.names[j], str(fields[j].type), i, str(column_type)))
                            else:
                                new_col = pyarrow.column(
                                    fields[j],
                                    pyarrow.array(gen_n_of_x(column.null_count, None),
                                                  fields[j].type,
                                                  mask=np.full(column.null_count, True)))
                                partition = partition.remove_column(j)
                                partition = partition.add_column(j, new_col)
                            partitions_dfs[i] = partition
                        elif column_type != pyarrow.null():
                            if fields[j].type == pyarrow.null():
                                fields[j] = pyarrow.field(fields[j].name, column_type)
                            else:
                                _LoggerFactory.trace(logger, "complete_incoming_dataframes.column_type_mismatch", {'dataframe_id': dataframe_id})
                                raise _InconsistentSchemaError(
                                    'A partition has a column with a different type than expected.\nThe type of column '
                                    '\'{0}\' in the first partition is {1}. In partition \'{2}\' found type is {3}.'
                                    .format(partition.schema.names[j], str(fields[j].type), i, str(column_type)))

        def get_concatenated_stream_columns():
            first_partition_stream_columns = partition_stream_columns[0]
            stream_columns = {}
            # initialize dictionary
            for (paths, values) in first_partition_stream_columns:
                if len(paths) == 1:
                    stream_columns[paths[0]] = values
                else:
                    _LoggerFactory.trace(logger, "get_concatenated_stream_columns.failure_path_count", {'path_count': len(paths), 'partition': 0})
                    return None
            stream_column_count = len(stream_columns.keys())
            for i in range(1, len(partition_stream_columns)):
                if len(partition_stream_columns[i]) != stream_column_count:
                    # found different count of stream columns as compared to first partition
                    _LoggerFactory.trace(logger, "get_concatenated_stream_columns.failure_stream_count", {'stream_count': len(partition_stream_columns[i]), 'partition': i, 'first_partition_count': stream_column_count})
                    return None
                for (paths, values) in partition_stream_columns[i]:
                    if len(paths) != 1 or paths[0] not in stream_columns.keys():
                        _LoggerFactory.trace(logger, "get_concatenated_stream_columns.failure_column_mismatch", {'path_count': len(paths), 'partition': i})
                        return None
                    stream_columns[paths[0]].extend(values)
            
            return stream_columns

        def set_stream_columns(df, stream_columns):
            if stream_columns is not None:
                value_count = 0
                for (column, values) in stream_columns.items():
                    df[column] = values
                    value_count = len(values)
                _LoggerFactory.trace(logger, "set_stream_columns.success", {'shape': '({},{})'.format(len(stream_columns.keys()), value_count)})

        with tracer.start_as_current_span('_DataFrameReader.complete_incoming_dataframe', trace.get_current_span()):
            verify_column_names()
            first_partition = partitions_dfs[0]
            column_fields = []
            names = first_partition.schema.names
            for i in range(0, first_partition.num_columns):
                f = pyarrow.field(names[i], determine_column_type(i))
                column_fields.append(f)
            apply_column_types(column_fields)

            import pyarrow
            df = pyarrow.concat_tables(partitions_dfs, promote=True).to_pandas(use_threads=True)
            if partition_stream_columns:
                stream_columns = get_concatenated_stream_columns()
                set_stream_columns(df, stream_columns)
            _LoggerFactory.trace(logger, "complete_incoming_dataframes.success", {'dataframe_id': dataframe_id, 'shape': str(df.shape)})
            return df

    def register_iterator(self, iterator_id: str, iterator: RecordIterator):
        _LoggerFactory.trace(logger, "register_iterator", {'iterator_id': iterator_id})
        self._iterators[iterator_id] = iterator

    def complete_iterator(self, iterator_id: str):
        _LoggerFactory.trace(logger, "complete_iterator", {'iterator_id': iterator_id})
        if iterator_id in self._iterators:
            self._iterators.pop(iterator_id)

    def _read_incoming_partition(self, dataframe_id: str, partition: int, partition_bytes: bytes, is_from_file: bool):
        if not have_pyarrow():
            raise ImportError('PyArrow is not installed.')
        else:
            from pyarrow import feather, ArrowInvalid
        _LoggerFactory.trace(logger, "read_incoming_partition", {'dataframe_id': dataframe_id, 'partition': partition})

        if is_from_file:
            import os
            name = partition_bytes.decode('utf-8')
            try:
                table = feather.read_table(name)
            except ArrowInvalid as e:
                size = os.path.getsize(name)
                if size != 8:
                    raise e

                with open(name, 'rb') as file:
                    count_bytes = file.read(8)
                    row_count = int.from_bytes(count_bytes, 'little')
                    import pandas as pd
                    table = pd.DataFrame(index=pd.RangeIndex(row_count))
            finally:
                # noinspection PyBroadException
                try:
                    os.remove(name)
                except:
                    pass
        else:
            # Data is transferred as either Feather or just a count of rows when the partition consisted of records with
            # no columns. Feather streams are always larger than 8 bytes, so we can detect that we are dealing with only
            # a row count by checking if we received exactly 8 bytes.
            if len(partition_bytes) == 8:  # No Columns partition.
                row_count = int.from_bytes(partition_bytes, 'little')
                import pandas as pd
                table = pd.DataFrame(index=pd.RangeIndex(row_count))
            else:
                table = feather.read_table(io.BytesIO(partition_bytes))

        if dataframe_id in self._incoming_dataframes:
            partitions_dfs = self._incoming_dataframes[dataframe_id]
            partitions_dfs[partition] = table
        elif dataframe_id in self._iterators:
            self._iterators[dataframe_id].process_partition(partition, table)
        else:
            _LoggerFactory.trace(logger,
                                 "dataframe_id_not_found",
                                 {
                                     'dataframe_id': dataframe_id,
                                     'current_dataframe_ids': str(list(self._incoming_dataframes.keys()))
                                 })
            raise ValueError('Invalid dataframe_id: {}'.format(dataframe_id))

    def _cancel(self, dataframe_id: str):
        if dataframe_id in self._iterators:
            self._iterators[dataframe_id].cancel_iteration()
        elif dataframe_id in self._incoming_dataframes:
            self._incoming_dataframes[dataframe_id] = {}


_dataframe_reader = None
_dataframe_reader_with_script = None
_dataframe_reader_lock = RLock()

def get_dataframe_reader():
    global _dataframe_reader
    if _dataframe_reader is None:
        with _dataframe_reader_lock:
            if _dataframe_reader is None:
                _dataframe_reader = _DataFrameReader()

    return _dataframe_reader


def ensure_dataframe_reader_handlers(requests_channel):
    requests_channel.register_handler('get_dataframe_partitions', process_get_partitions)
    requests_channel.register_handler('get_dataframe_partition_data', process_get_data)
    requests_channel.register_handler('send_dataframe_partition', process_send_partition)


def process_get_partitions(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    try:
        partition_count = get_dataframe_reader()._get_partitions(dataframe_id)
        writer.write(json.dumps({'result': 'success', 'partitions': partition_count}))
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': repr(e)}))


def process_get_data(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    partition = request.get('partition')
    try:
        partition_bytes = get_dataframe_reader()._get_data(dataframe_id, partition)
        byte_count = len(partition_bytes)
        byte_count_bytes = byte_count.to_bytes(4, 'little')
        socket.send(byte_count_bytes)
        socket.send(partition_bytes)
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': repr(e)}))


def process_send_partition(request, writer, socket):
    dataframe_id = request.get('dataframe_id')
    partition = request.get('partition')
    is_from_file = request.get('is_from_file')
    try:
        writer.write(json.dumps({'result': 'success'}) + '\n')
        writer.flush()
        byte_count = int.from_bytes(socket.recv(8), 'little')
        with socket.makefile('rb') as input:
            partition_bytes = input.read(byte_count)
            get_dataframe_reader()._read_incoming_partition(dataframe_id, partition, partition_bytes, is_from_file)
            writer.write(json.dumps({'result': 'success'}) + '\n')
    except Exception as e:
        get_dataframe_reader()._cancel(dataframe_id)
        writer.write(json.dumps({'result': 'error', 'error': _get_error_details(e)}))


def _get_error_details(e):
    errorCode = type(e).__name__
    errorMessage = str(e)
    return {
        'errorCode': errorCode,
        'errorMessage': errorMessage
    }
