import os
import uuid
from errno import EFBIG, ENOENT
from platform import system
from stat import S_IFDIR, S_IFREG
from time import perf_counter
from typing import List, Optional

from azureml.dataprep import (Dataflow, SummaryColumnsValue, SummaryFunction,
                              col, cond, get_stream_properties)
from azureml.dataprep.api._loggerfactory import (_LoggerFactory, trace)
from azureml.dataprep.api._rslex_executor import ensure_rslex_environment
from azureml.dataprep.api.engineapi.typedefinitions import DownloadStreamInfoMessageArguments
from azureml.dataprep.api.expressions import (FunctionExpression,
                                              IdentifierExpression,
                                              InvokeExpression)
from azureml.dataprep.api.functions import get_portable_path
from azureml.dataprep.api.tracing._context import Context
from azureml.dataprep.api.tracing._open_telemetry_adapter import to_dprep_span_context
from azureml.dataprep.native import DataPrepError
from azureml.dataprep.rslex import (Copier, PyIfDestinationExists,
                                    PyLocationInfo, StreamInfo)

from ._cached_dataflow import BypassCacheDataflow, CachedDataflow
from ._dataflow_path_helpers import get_stream_details
from ._dataflowconstants import *
from ._filecache import FileCache
from ._fuse_base import FuseBase
from ._stat import create_stat, stat_to_dict
from ._streaminfo import StreamDetails, get_stream_info_value, get_value
from ._streamingreader import StreamingReader, UnknownStreamSizeError
from .daemon import MountContext
from .vendor.fuse import FUSE, FuseOSError

log = _LoggerFactory.get_logger('dprep.fuse')
tracer = trace.get_tracer(__name__)
SENTINEL_FILE_NAME = '__dprep_sentinel_fac0fa29-1396-4461-9056-f34bdd8dc3c6__'
_SENTINEL_PATH = '/' + SENTINEL_FILE_NAME


class MountOptions:
    def __init__(self,
                 data_dir: str = None,
                 max_size: int = None,
                 free_space_required: int = None,
                 default_permission=0o777,
                 allow_other=False,
                 **kwargs):
        """
        Configuration options for file mounting.

        .. remarks::

            Depending on the source of the streams mounted, it might be necessary to fully download a file locally
                before it can be opened by the file system. For sources that support streaming, access to the file
                can be provided without this requirement. In both cases, it is possible to configure the system
                to cache the data locally. This can be useful when specific files will be accessed multiple times
                and the source of the data is remote to the current compute. These downloaded and cached files will
                be stored in the system's tmp folder by default, but this can be overridden by manually specifying a
                data_dir.

            The max_size and free_space_required parameters can be used to limit how much data will be downloaded
                or cached locally. If accessing a file requires that it be downloaded, then the least recently used
                files will be deleted after the download completes in order to stay within these parameters. If a file
                that needs to be downloaded before it can be opened by the file system does not fit within the available
                space, an error will be returned.

        :param data_dir: The directory to use to download or cache files locally. If None is provided, the system's
            temp folder is used.
        :param max_size: The maximum amount of memory, in bytes, that can be stored in data_dir.
        :param free_space_required: How much space should be kept available in the data_dir volume.
        :param default_permission: The default permissions for all files.
        :param allow_other: By default fuse mounts are accessable by only the user which creates the mount.
            allow_other=True extends access permission to any user (including root).
        """
        self.data_dir = data_dir
        self.max_size = max_size
        self.free_space_required = free_space_required
        self.default_permission = default_permission
        self.allow_other = allow_other
        self._data_dir_suffix = kwargs.get(
            'data_dir_suffix', str(uuid.uuid4()))
        self._cached_dataflow_override = kwargs.get('cached_dataflow_override')
        self._disable_dataflow_cache = kwargs.get(
            'disableMetadataCache', "False").lower() == "true"
        self.read_only = kwargs.get('read_only', True)
        self.create_destination = kwargs.get('create_destination', False)

    @property
    def final_data_dir(self):
        return os.path.join(self.data_dir, self._data_dir_suffix) if self._data_dir_suffix else self.data_dir


class _DPrepFuse(FuseBase):
    """Read-only fuse."""

    def __init__(self,
                 dataflow: Dataflow,
                 files_column: str,
                 base_path: str = None,
                 mount_options: MountOptions = None,
                 invocation_id: str = None,
                 caller_session_id: str = None,
                 span_context: Optional[Context] = None,
                 show_not_found_error: bool = True):
        parent = span_context or tracer.start_span(
            self.__class__.__name__, user_facing_name='Dataset Mount')
        mount_options = mount_options or MountOptions(default_permission=0o555)
        super().__init__(log, invocation_id, mount_options, parent)
        self._files_column = files_column
        self._cache = FileCache(self._mount_options.final_data_dir,
                                self._mount_options.max_size,
                                self._mount_options.free_space_required,
                                self._download_stream,
                                self._get_handle,
                                invocation_id=invocation_id)
        dataflow = dataflow \
            .add_column(get_portable_path(col(files_column), base_path), PORTABLE_PATH, files_column) \
            .add_column(get_stream_properties(col(files_column)), STREAM_PROPERTIES, PORTABLE_PATH)

        if mount_options._disable_dataflow_cache:
            self._cached_dataflow = BypassCacheDataflow(dataflow)
            self._bypass_attributes_cache = True
        else:
            self._cached_dataflow = CachedDataflow(
                dataflow, self._mount_options._cached_dataflow_override or self._mount_options.final_data_dir,
                show_not_found_error=show_not_found_error
            )
            self._bypass_attributes_cache = False
        self._streaming_reader = StreamingReader(self._cached_dataflow,
                                                 files_column,
                                                 self._mount_timestamp,
                                                 self._engine_api,
                                                 self._get_handle,
                                                 self._mount_options.default_permission)
        self._open_dirs = {}
        self._cached_dirs = {}
        self._known_dirs = set()
        self._cached_entry_details = {}
        # Starts at 1 because 0 is reserved for _SENTINEL_PATH
        self._handle = 1

        try:
            log.debug("Ensuring RsLex Environment...")
            ensure_rslex_environment(caller_session_id)
            self._copier = Copier(PyLocationInfo('Local', self._cache.data_dir, {
            }), base_path, PyIfDestinationExists.MERGE_WITH_OVERWRITE)
        except Exception as e:
            self._copier = None

    def _get_handle(self):
        self._handle += 1
        return self._handle

    def _list_entries(self, path: str) -> List[str]:
        with tracer.start_as_current_span('_DPrepFuse._list_entries', trace.get_current_span()):
            path = _ensure_directory_path(path)
            entries = self._cached_dirs.get(
                path) if not self._bypass_attributes_cache else None

            if entries is not None:
                return entries

            path_col = col(PORTABLE_PATH)
            child_path_fn = FunctionExpression([DELIMITER_INDEX],
                                               {},
                                               cond(IdentifierExpression(DELIMITER_INDEX) != -1,
                                                    col(RELATIVE_PATH).substring(
                                                        0, IdentifierExpression(DELIMITER_INDEX)),
                                                    col(RELATIVE_PATH)))

            # Summary of the below Dataflow transformations:
            # 1. filter in only paths which start with the requested path to list
            # 2. add a column which contains relative path under the requested path
            # 3. add a column which has only 2nd level children (based on the relative path), will be equal to relative
            #    path if there are no 2nd level children.
            # 4. add a column which has only StreamInfos for immediate children of the requested path, otherwise empty
            # 5. group the data by child path columns and summarize using Single Value aggreagte. This results in a
            #    single Record per immediate child of the requested path. (2nd level children were grouped together)
            # 6. summarize files, immediate children, portable paths and stream properties from records into flat lists
            results = self._cached_dataflow.dataflow(wait_for_cache=True) \
                .filter(path_col.starts_with(path)) \
                .add_column(col(PORTABLE_PATH).substring(len(path)), RELATIVE_PATH, PORTABLE_PATH) \
                .add_column(InvokeExpression(child_path_fn, [col(RELATIVE_PATH).index_of('/')]), CHILD_PATH, RELATIVE_PATH) \
                .add_column(cond(col(RELATIVE_PATH) == col(CHILD_PATH), col(self._files_column), None), CHILD_FILE, CHILD_PATH) \
                .summarize([
                    SummaryColumnsValue(
                        CHILD_FILE, SummaryFunction.SINGLE, self._files_column),
                    SummaryColumnsValue(
                        PORTABLE_PATH, SummaryFunction.SINGLE, PORTABLE_PATH),
                    SummaryColumnsValue(
                        STREAM_PROPERTIES, SummaryFunction.SINGLE, STREAM_PROPERTIES)
                ], group_by_columns=[CHILD_PATH]) \
                .summarize([
                    SummaryColumnsValue(self._files_column,
                                        SummaryFunction.TOLIST, STREAMS_LIST),
                    SummaryColumnsValue(
                        CHILD_PATH, SummaryFunction.TOLIST, CHILD_PATHS_LIST),
                    SummaryColumnsValue(
                        PORTABLE_PATH, SummaryFunction.TOLIST, PORTABLE_PATHS_LIST),
                    SummaryColumnsValue(
                        STREAM_PROPERTIES, SummaryFunction.TOLIST, STREAMS_PROPERTIES_LIST)
                ]) \
                ._to_pyrecords()
            entries = ['.', '..']
            if len(results) == 0:
                return entries

            children = results[0][CHILD_PATHS_LIST]
            matching_streams = results[0][STREAMS_LIST]
            portable_paths = results[0][PORTABLE_PATHS_LIST]
            stream_properties = results[0][STREAMS_PROPERTIES_LIST]
            children_data = zip(
                matching_streams, portable_paths, stream_properties, children)
            for matching_stream, portable_path, properties, relative_path in children_data:
                if isinstance(matching_stream, DataPrepError):
                    if matching_stream.errorCode == "Microsoft.DPrep.ErrorCodes.SingleValueExpected":
                        self._known_dirs.add(
                            _ensure_directory_path(path + relative_path))
                    continue

                if matching_stream is None:
                    continue

                if not portable_path.endswith(relative_path):
                    self._known_dirs.add(_ensure_directory_path(relative_path))

                # caching entry should be skipped for stream with unknown size, which will
                # make getattr download the stream into filecache for its true size
                if properties.get(STREAM_SIZE) is None:
                    continue

                self._cached_entry_details[portable_path] = {
                    STREAM_INFO: matching_stream,
                    PORTABLE_PATH: portable_path,
                    STREAM_SIZE: properties.get(STREAM_SIZE),
                    LAST_MODIFIED: properties.get(LAST_MODIFIED),
                    CAN_SEEK: properties.get(CAN_SEEK)
                }

            entries = entries + children

            if not self._bypass_attributes_cache:
                self._cached_dirs[path] = entries

            return entries

    def _download_stream(self, stream_details: StreamDetails, target_path: str) -> str:
        span = trace.get_current_span()
        try:
            if self._copier is None:
                raise Exception("copier is None")
            stream_info = StreamInfo(
                stream_details.stream_info.handler,
                stream_details.stream_info.resource_identifier,
                stream_details.stream_info.arguments)

            stream_info.with_session_properties({
                'size': stream_details.size,
                'createdTime': stream_details.last_modified,
                'modifiedTime': stream_details.last_modified,
                'isSeekable': stream_details.can_seek
            })
            downloaded_path = self._copier.copy_stream_info(
                stream_info, span.to_w3c_traceparent())
            # if download path is different from target path, try to rename it to correct file name
            if downloaded_path != target_path:
                log.warning('Downloaded path is different from target path')
                print(
                    'Downloaded path: {} is different from target path: {}'.format(downloaded_path, target_path))
                try:
                    os.rename(downloaded_path, target_path)
                except Exception:
                    # if rename fails, remove the downloaded file and fall back to clex
                    os.remove(downloaded_path)
                    raise
            return target_path
        except Exception as e:
            err_msg = 'Download failed with rslex due to {}.'.format(repr(e))
            if '_TEST_DISABLE_DOWNLOAD_FALLBACK' in os.environ:
                raise Exception(err_msg) from e
            self._engine_api.download_stream_info(DownloadStreamInfoMessageArguments(
                to_dprep_span_context(span.get_context() if span else None), get_stream_info_value(stream_details.stream_info), target_path))
            return target_path

    def _get_stream_details_for_path(self, path) -> Optional[StreamDetails]:
        log.debug('Getting stream details for path %s', path)
        with tracer.start_as_current_span('_DPrepFuse._get_stream_details_for_path', trace.get_current_span()):
            cached_entry = self._cached_entry_details.get(path)
            if cached_entry is not None:
                log.debug('Stream details in cache.')
                return StreamDetails(cached_entry[STREAM_INFO],
                                     cached_entry[PORTABLE_PATH],
                                     cached_entry[STREAM_SIZE],
                                     cached_entry[LAST_MODIFIED],
                                     cached_entry[CAN_SEEK])

            log.debug('Executing to retrieve stream details.')
            stream_details = get_stream_details(
                self._cached_dataflow.dataflow(
                    wait_for_cache=False), path, self._files_column
            )

            if stream_details is None:
                return None

            cached_entry = {
                STREAM_INFO: stream_details.stream_info,
                PORTABLE_PATH: stream_details.portable_path,
                STREAM_SIZE: stream_details.size,
                LAST_MODIFIED: stream_details.last_modified,
                CAN_SEEK: stream_details.can_seek
            }
            self._cached_entry_details[path] = cached_entry

            return stream_details

    def _cache_path(self, path: str):
        stream_details = self._get_stream_details_for_path(path)
        stream_last_modified = int(stream_details.last_modified.timestamp() if stream_details.last_modified is not None
                                   else self._mount_timestamp)
        stat = create_stat(S_IFREG,
                           stream_details.size,
                           stream_last_modified,
                           stream_last_modified,
                           stream_last_modified,
                           self._mount_options.default_permission)
        self._cache.push(path, stream_details, stat)

    def getattr(self, path: str, fh=None):
        with tracer.start_as_current_span('_DPrepFuse.getattr', self._span_context):
            log.debug('getattr(path=%s)', path, extra=dict(path=path))

            if path == _SENTINEL_PATH:
                return self._sentinel_attr

            if path.startswith('/.Trash'):
                # .Trash files are used by Ubuntu to store deleted files in a mounted volume. As such, we can't actually
                # mount files with this name. Since this is also a read-only file system, we don't support deletion.
                # We'll take a shortcut and just return ENOENT instead of doing a lookup.
                raise FuseOSError(ENOENT)

            if path in self._cache:
                log.debug('Path found in cache.', extra=dict(path=path))
                return stat_to_dict(self._cache.get_attributes(path))

            ensured_path = _ensure_directory_path(path)
            if ensured_path in self._cached_dirs or ensured_path in self._known_dirs:
                log.debug('Path found in directory cache.',
                          extra=dict(path=path))
                return {
                    'st_mode': S_IFDIR,
                    'st_size': 0,
                    'st_atime': self._mount_timestamp,
                    'st_mtime': self._mount_timestamp,
                    'st_ctime': self._mount_timestamp
                }

            # Ensure the entries cache for this path is populated if the Dataflow cache is available
            if self._cached_dataflow.cache_available:
                parent_dir = os.path.dirname(path)
                self._list_entries(parent_dir)
            if path in self._cached_entry_details:
                log.debug('Path found in cached entries.',
                          extra=dict(path=path))
                entry = self._cached_entry_details[path]
                stream_last_modified = int(entry[LAST_MODIFIED].timestamp() if entry[LAST_MODIFIED] is not None
                                           else self._mount_timestamp)
                return {
                    'st_mode': self._mount_options.default_permission | S_IFREG,
                    'st_size': entry[STREAM_SIZE],
                    'st_atime': stream_last_modified,
                    'st_mtime': stream_last_modified,
                    'st_ctime': stream_last_modified
                }

            # If we didn't find the entry in the cache after populating it could be because attribute caching
            # has been disabled or the entry did not fit in the cache. Go ahead and stream the attributes.
            try:
                log.debug('Attempting to stream attributes. (path=%s)',
                          path, extra=dict(path=path))
                stat, stream_details = self._streaming_reader.get_attributes_and_stream_details(
                    path)
                if stream_details:
                    self._cached_entry_details[path] = {
                        STREAM_INFO: stream_details.stream_info,
                        PORTABLE_PATH: stream_details.portable_path,
                        STREAM_SIZE: stream_details.size,
                        LAST_MODIFIED: stream_details.last_modified,
                        CAN_SEEK: stream_details.can_seek
                    }
                else:
                    self._known_dirs.add(ensured_path)
                return stat_to_dict(stat)
            except UnknownStreamSizeError:
                log.debug('Unknown size for specified path. (path=%s)',
                          path, extra=dict(path=path))
                self._cache_path(path)
                return stat_to_dict(self._cache.get_attributes(path))

    def opendir(self, path):
        with tracer.start_as_current_span('_DPrepFuse.opendir', self._span_context):
            log.debug('opendir(path=%s)', path)
            handle = self._get_handle()
            self._open_dirs[handle] = self._list_entries(path)
            log.debug('Entries retrieved.')
            return handle

    def readdir(self, path, fh):
        with tracer.start_as_current_span('_DPrepFuse.readdir', self._span_context):
            log.debug('readdir(path=%s, fh=%s)',
                      path, fh, extra=dict(handle=fh))
            dir_entries = self._open_dirs.get(fh)
            if dir_entries is None:
                log.warning(
                    'No entries found in cache. Was opendir not called?', extra=dict(handle=fh))
                dir_entries = self._list_entries(path)

            log.debug('Returning entries.', extra=dict(handle=fh))
            return dir_entries

    def releasedir(self, path, fh):
        try:
            log.debug('releasedir(handle=%s)', fh)
            self._open_dirs.pop(fh)
        except KeyError:
            log.warning('Failed to release directory.', extra=dict(handle=fh))
            log.error('Unexpected error during releasedir.')
            raise FuseOSError(ENOENT)

    def open(self, path, flags, raw_fi=None):
        log.debug('open(path=%s, flags=%s)', path, flags,
                  extra=dict(path=path, flags=flags))

        with tracer.start_as_current_span('_DPrepFuse.open', self._span_context):
            if path == _SENTINEL_PATH:
                log.debug('_SENTINEL_PATH opened: %s (handle=%s)',
                          path, 0, extra=dict(path=path, handle=0))
                return 0

            try:
                if path not in self._cache:
                    log.debug('Caching path: %s', path, extra=dict(path=path))
                    self._cache_path(path)

                log.debug('Reading from cache: %s',
                          path, extra=dict(path=path))
                handle = self._cache.open(path)
                log.debug('File opened from cache: %s (handle=%s)',
                          path, handle, extra=dict(path=path, handle=handle))
                return handle
            except Exception as e:
                log.debug('Error encountered while opening file: %s',
                          path, extra=dict(path=path))
                if type(e).__name__ != FuseOSError.__name__ or e.errno != EFBIG:
                    raise

            # If we failed because the file is too big to download, try to stream it
            log.debug('File too big to download. Streaming: %s',
                      path, extra=dict(path=path))
            try:
                return self._streaming_reader.open(path)
            except Exception:
                log.debug('Failed to stream file: %s',
                          path, extra=dict(path=path))
                self._trace('Failed to stream file.')
                raise

    def read(self, path, size, offset, fh, buffer):
        log.debug('read(path=%s, size=%s, offset=%s, fh=%s)',
                  path,
                  size,
                  offset,
                  fh,
                  extra=dict(path=path, size=size, offset=offset, fh=fh))

        if path == _SENTINEL_PATH and fh == 0:
            log.debug('Reading _SENTINEL_PATH: %s (handle=%s)',
                      path, fh, extra=dict(path=path, handle=fh))
            contents = self._sentinel_contents
            contents_len = len(contents)
            for i, c in enumerate(contents):
                buffer[offset + i] = contents[i]
            return contents_len

        if path in self._cache:
            log.debug('Reading file from cache: %s (handle=%s)',
                      path, fh, extra=dict(path=path, handle=fh))
            return self._cache.read(fh, size, offset, buffer)
        else:
            log.debug('Streaming file read: %s (handle=%s)',
                      path, fh, extra=dict(path=path, handle=fh))
            return self._streaming_reader.read(fh, size, offset, buffer)

    def release(self, path, fh):
        log.debug('release(path=%s, fh=%s)', path, fh,
                  extra=dict(path=path, handle=fh))

        if path == _SENTINEL_PATH and fh == 0:
            log.debug('Releasing _SENTINEL_PATH: %s (handle=%s)',
                      path, fh, extra=dict(path=path, handle=fh))
            return

        if path in self._cache:
            log.debug('Releasing file from cache: %s (handle=%s)',
                      path, fh, extra=dict(path=path, handle=fh))
            return self._cache.release(fh)
        else:
            log.debug('Releasing file from streaming reader: %s (handle=%s)',
                      path, fh, extra=dict(path=path, handle=fh))
            return self._streaming_reader.release(fh)

    def destroy(self, path):
        log.info('Tearing down mount (%s)', self._invocation_id,
                 extra=dict(invocation_id=self._invocation_id))
        self._cache.clear()


def _ensure_directory_path(path):
    # Ensure directories end with /
    return path + '/' if path[-1] != '/' else path


def mount(dataflow: Optional[Dataflow],
          files_column: Optional[str],
          mount_point: str,
          base_path: str = None,
          options: MountOptions = None,
          destination: tuple = None,
          foreground=True,
          invocation_id: str = None,
          span_context: Optional[Context] = None,
          client_id=None,
          identity_endpoint_type=None,
          enable_rslex_mount: Optional[bool] = None,
          **kwargs) -> Optional[MountContext]:

    disable_fallback = os.getenv('RSLEX_DIRECT_VOLUME_MOUNT_DISABLE_FALLBACK', default="false").lower() == "true"
    
    try:
        rslex_mount_context = rslex_direct_volume_mount(
            dataflow, mount_point, options, destination, client_id=client_id,
            identity_endpoint_type=identity_endpoint_type, enable_rslex_mount=enable_rslex_mount,
            invocation_id=invocation_id, span_context=span_context)

        if rslex_mount_context is not None:
            return rslex_mount_context
    except VolumeMountNotEnabled as e:
        log.info("RslexDirectVolumeMount is not enabled")
        if disable_fallback:
            raise e
    except VolumeMountNotSupported as e:
        message = str(e)
        log.info('Failed to run rslex based mount due to exception of type {} with message {}. Falling back to dataflow mount.'.format(
                type(e).__name__, message))
        print('Not mounting as a volume: {}. \nFalling back to dataflow mount.'.format(message))
    except VolumeMountFailed as e:
        message = str(e)
        print('Volume mount failed with: {}'.format(message))
        log.error('Failed to run rslex based mount due to exception of type {} with message {}'.format(
            type(e).__name__, message))
        raise e
    except BaseException as e:
        message = str(e)
        log.warning('Unexpected error during volume mount: {}'.format(message))

        if disable_fallback:
            raise e

    return clex_mount(dataflow, files_column, mount_point, base_path, options, destination, foreground,
        invocation_id, span_context, client_id, identity_endpoint_type, **kwargs)

def clex_mount(dataflow: Optional[Dataflow],
          files_column: Optional[str],
          mount_point: str,
          base_path: str = None,
          options: MountOptions = None,
          destination: tuple = None,
          foreground=True,
          invocation_id: str = None,
          span_context: Optional[Context] = None,
          client_id=None,
          identity_endpoint_type=None,
          **kwargs) -> Optional[MountContext]:
    if client_id or identity_endpoint_type:
        raise ValueError(
            'client_id {} and identity_endpoint_type {} is not supported in dprepfuse.'.format(client_id, identity_endpoint_type))

    if foreground:
        spawn_process_timestamp = float(
            kwargs.get('spawn_process_timestamp', -1))
        caller_session_id = kwargs.get('caller_session_id')

        def calculate_elapsed():
            return -1 if spawn_process_timestamp == -1 else perf_counter() - spawn_process_timestamp

        _LoggerFactory.trace(log, 'starting dataprep mount in foreground', {
            'invocationId': invocation_id,
            'elapsed_since_process_spawn': calculate_elapsed()
        })
        if not dataflow and not destination:
            raise ValueError(
                'Invalid mount arguments. You must either pass in a dataflow or a destination.')
        if dataflow is not None:
            _LoggerFactory.trace(log, 'Creating _DPrepFuse.')
            fuse_opts = _DPrepFuse(dataflow, files_column, base_path,
                                   options, invocation_id, caller_session_id, span_context)
            _LoggerFactory.trace(log, 'Created _DPrepFuse.')
        else:
            from azureml.dataprep.fuse._writable_fuse import WritableFuse
            _LoggerFactory.trace(log, 'Creating WritableFuse.')
            fuse_opts = WritableFuse(
                destination, options, invocation_id, span_context, caller_session_id)
            _LoggerFactory.trace(log, 'Created WritableFuse.')
        try:
            _LoggerFactory.trace(log, 'Initializing FUSE with fuse options.', {
                'elapsed_since_process_spawn': calculate_elapsed()
            })
            # ensure mount_point exists otherwise FUSE will fail
            try:
                os.makedirs(mount_point, exist_ok=True)
            except Exception as e:
                log.warning('Failed to ensure mount point "{}" due to exception of type {} with message {}'.format(
                    mount_point, type(e).__name__, e))

            additional_options = {}

            if system() == 'Darwin':
                # Additional options for MACos
                # daemon_timeout - override default 60 seond per operation timemout;
                # noappledouble -  reject call to ._ and .DS_Store;
                # noapplexattr - deny access to extended attributes that begin with the com.apple. prefix
                # nobrowse - do not index with finder automatically
                additional_options = {
                    'daemon_timeout': 3600, 'noappledouble': True, 'noapplexattr': True, 'nobrowse': True}
            if options is not None and options.allow_other:
                additional_options['allow_other'] = True

            FUSE(fuse_opts, mount_point, foreground=True, **additional_options)
            _LoggerFactory.trace(log, 'Initialized FUSE with fuse options.')
            return None
        except Exception as e:
            log.error('An unexpected exception of type {} occurred during dataprep mount with message {}'.format(
                type(e).__name__, e))
            raise
    else:
        return MountContext(dataflow, files_column, mount_point, base_path, options, invocation_id, destination, span_context=span_context)


def rslex_uri_volume_mount(uri: str, mount_point: str, options: Optional[MountOptions] = None):
    try:
        log.info('Running rslex URI volume mount')
        from azureml.dataprep.rslex import (PyVolumeMountOptions,
                                            RslexDirectURIMountContext)

        ensure_rslex_environment(None)

        max_size = None
        free_space_required = None
        allow_other = None
        cache_dir_path = None
        read_only = True
        create_destination = False

        if options:
            max_size = options.max_size
            free_space_required = options.free_space_required
            allow_other = options.allow_other
            cache_dir_path = options.data_dir
            permissions = options.default_permission
            read_only = options.read_only
            create_destination = options.create_destination

        options = PyVolumeMountOptions(
            max_size,
            cache_dir_path,
            free_space_required,
            allow_other,
            read_only,
            permissions,
            create_destination
        )

        try:
            os.makedirs(mount_point, exist_ok=True)
        except Exception as e:
            log.warning('Failed to ensure mount point "{}" due to exception of type {} with message {}'.format(
                mount_point, type(e).__name__, e))

        mount_context = RslexDirectURIMountContext(mount_point, uri, options)
        log.info("Rslex URI volume mount context created")
        return mount_context
    except Exception as e:
        log.warning('Failed to mount URI due to exception of type {} with message {}'.format(
            type(e).__name__, e))
        raise e


class VolumeMountNotEnabled(Exception):
    pass


class VolumeMountNotSupported(Exception):
    def __init__(self, message):
        super().__init__(message)


class VolumeMountFailed(Exception):
    def __init__(self, message):
        super().__init__(message)


def rslex_direct_volume_mount(dataflow: Optional[Dataflow],
                mount_point: str,
                options: MountOptions = None,
                destination: tuple = None,
                client_id: Optional[str] = None,
                identity_endpoint_type: Optional[str] = None,
                enable_rslex_mount: Optional[bool] = None,
                invocation_id: str = None,
                span_context: Optional[Context] = None):

    rslex_fuse_flight = os.getenv('RSLEX_DIRECT_VOLUME_MOUNT', default="true")
    rslex_writable_fuse_flight = os.getenv('RSLEX_DIRECT_VOLUME_WRITABLE_MOUNT', default="true")

    # == "1" is for backward compatibility for the people we already gave this flight
    # == "true" to be consistant with other arguments
    if (destination is None and (rslex_fuse_flight == "1" or rslex_fuse_flight.lower() == "true")) \
            or (destination is not None and (rslex_writable_fuse_flight == "1" or rslex_writable_fuse_flight.lower() == "true")) \
            or enable_rslex_mount:

        log.info('Running rslex direct volume mount: RSLEX_DIRECT_VOLUME_MOUNT={}, RSLEX_DIRECT_VOLUME_WRITABLE_MOUNT={}, enable_rslex_mount={}' \
            .format(rslex_fuse_flight, rslex_writable_fuse_flight, enable_rslex_mount))
        from azureml.dataprep.api._rslex_executor import \
            ensure_rslex_environment
        from azureml.dataprep.rslex import (PyVolumeMountDatastoreSource,
                                            PyVolumeMountOptions,
                                            RslexDirectMountContext)

        ensure_rslex_environment(None)
        datastore_source = None
        mount_options = None

        max_size = None
        free_space_required = None
        allow_other = None
        cache_dir_path = None
        datastore = None
        datastore_path = None
        read_only = True
        subscription_id = None
        resource_group = None
        workspace_name = None
        datastore_name = None
        permissions = None

        if options:
            max_size = options.max_size
            free_space_required = options.free_space_required
            allow_other = options.allow_other
            cache_dir_path = options.data_dir
            permissions = options.default_permission

        if dataflow is not None and len(dataflow._steps) == 1 and dataflow._steps[0].step_type == "Microsoft.DPrep.GetDatastoreFilesBlock":
            get_files_arguments = dataflow._steps[0].arguments
            datastores = get_files_arguments["datastores"]
            if datastores is None:
                raise VolumeMountNotSupported('No datastores found in GetDatastoreFilesBlock')
            if len(datastores) != 1:
                raise VolumeMountNotSupported('Volume mount only supports datasets with exactly one datastore path, actual: {}'.format(len(datastores)))
            if datastores is not None and len(datastores) == 1:
                datastore = datastores[0]
                datastore_path = datastore["path"]
                subscription_id = datastore["subscription"]
                resource_group = datastore["resourceGroup"]
                workspace_name = datastore["workspaceName"]
                datastore_name = datastore["datastoreName"]
        elif destination is not None:
            datastore = destination[0]
            datastore_path = destination[1]
            read_only = False
            subscription_id = datastore.workspace.subscription_id
            resource_group = datastore.workspace.resource_group
            workspace_name = datastore.workspace.name
            datastore_name = datastore.name

        if datastore is not None:
            mount_options = PyVolumeMountOptions(
                max_size,
                cache_dir_path,
                free_space_required,
                allow_other,
                read_only,
                permissions
            )
            datastore_source = PyVolumeMountDatastoreSource(
                subscription_id,
                resource_group,
                workspace_name,
                datastore_name,
                datastore_path,
                client_id,
                identity_endpoint_type
            )
        else:
            if enable_rslex_mount:
                log.warning(
                    'enable_rslex_mount is set to True but we couldn\'t extract datastore information')
            raise VolumeMountNotSupported('No datastore info was found, volume mount would not be attempted.')

        try:
            os.makedirs(mount_point, exist_ok=True)
        except Exception as e:
            message = 'Failed to ensure mount point "{}" due to exception of type {} with message {}, proceeding with mount attempt.'.format(
                mount_point, type(e).__name__, e)
            log.warning(message)
            print(message)

        try:
            mount_context = RslexDirectMountContext(
                mount_point, datastore_source, mount_options)
            log.info("Rslex direct volume mount context created")
        except BaseException as e:
            message = str(e)
            if 'Glob patterns inside the path are not supported' in message or 'DestinationError(NoHandler'in message:
                raise VolumeMountNotSupported(message)
            if 'DataAccess' in message or 'InvalidOptionValue ' in message or 'DestinationError' in message:
                raise VolumeMountFailed(message)
            raise e

        return mount_context
    else:
        raise VolumeMountNotEnabled()
