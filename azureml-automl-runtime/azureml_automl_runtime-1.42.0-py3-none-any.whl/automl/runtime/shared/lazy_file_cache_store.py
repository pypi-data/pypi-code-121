# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing the implementation for a file based cache to be used for saving automl data between runs."""
import uuid
from typing import Any, Callable, Dict, Iterable, Optional, Tuple
import json
import logging
import os
import pathlib
import shutil

import numpy as np
import pandas as pd
from azureml.automl.runtime.shared._cache_constants import Keys
from scipy import sparse

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    CacheOperation,
)
from azureml.automl.core.shared.pickler import DefaultPickler
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import CacheException

from azureml.automl.runtime.shared._parqueter import Parqueter
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.core.shared import utilities
from azureml.automl.runtime.stats_computation import RawFeatureStats

logger = logging.getLogger(__name__)


class CachedValueMetadata:
    TYPE_DIR = "dir"
    TYPE_FILE = "file"

    SUPPORTED_TYPES = (TYPE_FILE, TYPE_DIR)

    def __init__(self, local_path: str, remote_path: str, cv_type: str) -> None:
        """
        CacheValue constructor.

        :param local_path: path of the cached item on local system.
        :param remote_path: path of the cached item in remote cache store.
        :cv_type: supported type for cached value
        """
        if cv_type not in CachedValueMetadata.SUPPORTED_TYPES:
            msg = "Unsupported type value {}.".format(cv_type)
            raise CacheException(exception_message=msg)

        self.cv_type = cv_type
        self.local_path = local_path
        self.remote_path = remote_path

    def update_local_path(self, key: str, parent_local_path: str) -> None:
        """
        Update local path of cached item post load().

        :param key: Key of item in cached_items
        :param parent_local_path: local path of parent item.
        """
        pass

    def update_remote_path(self, key: str, parent_remote_path: str) -> None:
        """
        Set upload path based on parameters provided.

        :param key: key of item in cache store.
        :param parent_remote_path: remote path of parent directory.
        """
        pass


class FileCachedValueMetadata(CachedValueMetadata):
    """Class to hold metadata of files saved in cache store."""

    def __init__(self, local_path: str, remote_path: str = "", **kwargs: Any) -> None:
        """
        FileCachedValueMetadata constructor.

        :param local_path: path of the cached item on local system.
        :param remote_path: path of the cached item in remote cache store.
            NOTE This should be updated when cached file is uploaded to cached storage.
        :param kwargs: kwargs.
        """
        super().__init__(local_path, remote_path, CachedValueMetadata.TYPE_FILE)
        if kwargs.get("ext"):
            self.ext = kwargs["ext"]
        else:
            self.ext = self._get_file_ext(local_path)

    def update_local_path(self, key: str, parent_local_path: str) -> None:
        """
        Update local path of file item post load().

        :param key: Key of item in cached_items
        :param parent_local_path: local path of parent item.
        """
        self.local_path = ".".join([
            os.path.join(parent_local_path, *self._get_fqn(key).split("/")),
            self.ext])

    def update_remote_path(self, key: str, parent_remote_path: str) -> None:
        """
        Set upload path based on parameters provided.

        :param key: key of item in cache store.
        :param parent_remote_path: remote path of parent directory.
        """
        self.remote_path = (pathlib.Path(parent_remote_path).joinpath(
            self._get_fqn(key))).as_posix()
        if self.ext != "":
            self.remote_path = ".".join([self.remote_path, self.ext])

    def _get_file_ext(self, path: str) -> str:
        split = path.rfind(".")
        if split != -1:
            return path[split + 1:]
        return ""

    def _get_fqn(self, key: str) -> str:
        return Keys.DEFAULT_NAMESPACE + key if not os.path.dirname(key) else key


class DirCachedValueMetadata(CachedValueMetadata):
    """Class to hold metadata of directory saved in cache store."""

    def __init__(self, key: str, local_path: str, remote_path: str = "", **kwargs: Any) -> None:
        """
        DirCachedValueMetadata constructor.

        :param key: Key of item in cached_items.
        :param local_path: path of the cached item on local system.
        :param remote_path: path of the cached item in remote cache store.
            NOTE This should be updated when cached file is uploaded to cached storage.
        :param kwargs: Used during de-serialization.
        """
        super().__init__(local_path, remote_path, CachedValueMetadata.TYPE_DIR)
        self.key = key
        self.dir_items: Dict[str, FileCachedValueMetadata]
        self.dir_items = kwargs.get("dir_items", None)
        if self.dir_items is None:
            self.dir_items = self._get_dir_items(key)

    def _get_dir_items(self, key: str) -> Dict[str, FileCachedValueMetadata]:
        items: Dict[str, FileCachedValueMetadata] = {}
        path = self.local_path
        self._get_dir_items_helper(key, path, items)
        return items

    def _get_dir_items_helper(
        self,
        parent_key: str,
        path: str,
        items: Dict[str, FileCachedValueMetadata]
    ) -> None:
        try:
            for entry in os.scandir(path):
                key = parent_key + "/" + entry.name
                if entry.is_file():
                    split = key.rfind(".")
                    if split != -1:
                        key = key[:split]
                    items[key] = FileCachedValueMetadata(local_path=entry.path)
                elif entry.is_dir():
                    self._get_dir_items_helper(key, entry.path, items)
        except Exception as e:
            msg = "Exception while scanning dir {}".format(path)
            raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def update_local_path(self, key: str, parent_local_path: str) -> None:
        """
        Update local path of dir items post load().

        :param key: Key of item in cached_items
        :param parent_local_path: local path of parent item.
        """
        self.local_path = os.path.join(parent_local_path, *key.split("/"))
        for k, v in self.dir_items.items():
            v.update_local_path(k, parent_local_path)

    def update_remote_path(self, key: str, parent_remote_path: str) -> None:
        """
        Set upload path based on parameters provided.

        :param key: key of item in cache store.
        :param parent_remote_path: remote path of parent directory.
        """
        self.remote_path = (pathlib.Path(parent_remote_path).joinpath(key)).as_posix()
        for k, v in self.dir_items.items():
            v.update_remote_path(k, parent_remote_path)


class _JSONUtils(json.JSONEncoder):
    """Class to handle JSON serialization and de-serilization of index file."""

    def default(self, obj):
        """Called during JSON  serialization"""
        if isinstance(obj, FileCachedValueMetadata) \
                or isinstance(obj, DirCachedValueMetadata):
            return obj.__dict__
        else:
            return obj

    @staticmethod
    def decode(jdict):
        """Provided as object hook for JSON deserialization"""
        if jdict.get("cv_type") == CachedValueMetadata.TYPE_DIR:
            return DirCachedValueMetadata(**jdict)
        elif jdict.get("cv_type") == CachedValueMetadata.TYPE_FILE:
            return FileCachedValueMetadata(**jdict)
        else:
            return jdict


class _CacheConstants:
    # default task timeout
    DEFAULT_TASK_TIMEOUT_SECONDS = 900

    class FileExtensions:
        # Extension name for files that are saved by Numpy.save()
        NUMPY_FILE_EXTENSION = "npy"

        # Extension name for files that are saved by SciPy.save()
        SCIPY_SPARSE_FILE_EXTENSION = "npz"

        # Extension name for files saved with Pickle.dumps()
        PICKLE_FILE_EXTENSION = "pkl"

        # Extension for numpy arrays stored in parquet format.
        NUMPY_PARQUET_FILE_EXTENSION = "npy.parquet"

        # Extension for numpy arrays that are single dimensional.
        NUMPY_SINGLE_DIM_FILE_EXTENSION = "npys.parquet"

        # Extension for pandas dataframes stored in parquet format.
        DF_PARQUET_FILE_EXTENSION = "df.parquet"

        # Extension for pandas dataframes stored with pandas.DataFrame.to_pickle.
        DF_PICKLE_FILE_EXTENSION = "df.pkl"

        # Extension for spmatrix stored in parquet format.
        SCIPY_SPARSE_PARQUET_FILE_EXTENSION = "coo.parquet"

        ALL = [
            DF_PARQUET_FILE_EXTENSION,
            DF_PICKLE_FILE_EXTENSION,
            NUMPY_FILE_EXTENSION,
            NUMPY_PARQUET_FILE_EXTENSION,
            NUMPY_SINGLE_DIM_FILE_EXTENSION,
            PICKLE_FILE_EXTENSION,
            SCIPY_SPARSE_FILE_EXTENSION,
            SCIPY_SPARSE_PARQUET_FILE_EXTENSION,
        ]


class LazyFileCacheStore(CacheStore):
    """
    Cache store backed by the local file system.

    We consider this a "lazy" store as it doesn't pre-fetch the saved_as information.
    Instead we simply load the metadata and leverage the file extension to deserialize objects.

    This cache store supports keys with namespaces (as posix paths) to help distinguish b/w duplicate keys, i.e.,
    adding keys 'foo/bar/a' and 'a' is possible, since the former is located under a different namespace (foo/bar) than
    the latter (which is under a default namespace). If multiple keys with the same name and namespace are added,
    the values are overwritten (i.e. the last write wins).
    The underlying storage mechanism creates sub-directories as represented by the namespace to store the serialized
    objects that the key represents. For instance, a fully qualified key such as 'foo/bar/a' will create the required
    sub-directories under the root cache folder - '$CACHE_ROOT/foo/bar', and store the serialized file under it.

    To use keys with namespaces with this cache store, pass in a posix formatted key when calling add() or set()
    methods. e.g. `cache_store.set('a/new/directory/my_key', 'this is the value for my_key')`

    When retrieving keys from the cache store (via. cache_store.get(...)), the client can chose to include or omit
    the default namespace. E.g. `cache_store.get([DEFAULT_NAMESPACE_foo])` and `cache_store.get(["_foo"])` will both
    result in cache hits, if "_foo" was added to the cache store (via. cache_store.add(["_foo], ...))
    """

    _pickler = DefaultPickler()

    _extension_to_deserializer = {
        _CacheConstants.FileExtensions.DF_PARQUET_FILE_EXTENSION: Parqueter.load_pandas_dataframe,
        _CacheConstants.FileExtensions.DF_PICKLE_FILE_EXTENSION: pd.read_pickle,
        _CacheConstants.FileExtensions.NUMPY_FILE_EXTENSION: np.load,
        _CacheConstants.FileExtensions.NUMPY_PARQUET_FILE_EXTENSION: Parqueter.load_numpy_array,
        _CacheConstants.FileExtensions.NUMPY_SINGLE_DIM_FILE_EXTENSION: Parqueter.load_single_dim_numpy_array,
        _CacheConstants.FileExtensions.PICKLE_FILE_EXTENSION: _pickler.load,
        _CacheConstants.FileExtensions.SCIPY_SPARSE_FILE_EXTENSION: sparse.load_npz,
        _CacheConstants.FileExtensions.SCIPY_SPARSE_PARQUET_FILE_EXTENSION: Parqueter.load_sparse_matrix,
    }

    def __init__(
        self,
        path: str,
    ):
        """
        File based cache store - constructor.

        :param path: store path
        """
        super(LazyFileCacheStore, self).__init__()

        self._root = path
        self._indices_dir_path = self._to_fully_qualified_path(os.path.join(
            Keys.DEFAULT_NAMESPACE, Keys.INDICES_DIR))
        self._init_cache_folder()

    def __getstate__(self):
        """
        Get this cache store's state, removing unserializable objects in the process.

        :return: a dict containing serializable state.
        """
        return super().__getstate__(), {
            "_root": self._root,
            "_index_file_name": self._index_file_name,
            "_index_file_path": self._index_file_path,
            "_indices_dir_path": self._indices_dir_path
        }

    def __setstate__(self, state):
        """
        Deserialize this cache store's state, using the default logger.

        :param state: dictionary containing object state
        :type state: dict
        """
        super_state, my_state = state
        self._root = my_state["_root"]
        self._index_file_name = my_state["_index_file_name"]
        self._index_file_path = my_state["_index_file_path"]
        self._indices_dir_path = my_state["_indices_dir_path"]
        super().__setstate__(super_state)

    def __repr__(self):
        return '{}(path="{}")'.format(self.__class__.__name__, self._root[: self._root.rfind("cache") - 1])

    def _init_cache_folder(self) -> None:
        """
        Create temp dir.

        :return: temp location
        """
        try:
            os.makedirs(self._indices_dir_path, exist_ok=True)
            self._index_file_name = ".".join([str(uuid.uuid4().hex), "json"])
            self._index_file_path = os.path.join(
                self._indices_dir_path, self._index_file_name)
        except OSError as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            logger.error("Failed to initialize the cache store. Error code: {}".format(e.errno))
            raise CacheException._with_error(
                AzureMLError.create(
                    CacheOperation,
                    target="cache-init",
                    operation_name="initialization",
                    path=self._root,
                    os_error_details=e.errno,
                ),
                inner_exception=e,
            ) from e

    def add(self, keys: Iterable[str], values: Iterable[Any]) -> None:
        """
        Serialize the values and add them to cache and local file system.

        :param keys: store keys
        :param values: store values
        """
        with self.log_activity():
            for k, v in zip(keys, values):
                if not self._is_valid_key(k):
                    # _is_valid_key will return False if key exists
                    # Logging but allowing value to be updated.
                    # There are keys such as cv-splits which are updated more than once.
                    # Preventing that will break functionality.
                    logger.warning("Updating an existing key {}.".format(k))
                try:
                    logger.info("Uploading key: " + k)
                    # add the default namespace if no other namespace specified
                    k_fqn = Keys.DEFAULT_NAMESPACE + k if not os.path.dirname(k) else k
                    cached_value = self._write(k_fqn, v)
                    if not self.cache_items.get(k):
                        self.cache_items[k] = cached_value
                except OSError as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    logger.error(
                        "Failed to persist the keys [{}] to the local disk. Error code: {}".format(
                            ",".join(keys), e.errno
                        )
                    )
                    raise CacheException._with_error(
                        AzureMLError.create(
                            CacheOperation,
                            target="cache-add",
                            operation_name="add",
                            path=self._root,
                            os_error_details=e.errno,
                        ),
                        inner_exception=e,
                    ) from e
                except Exception as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    msg = "Failed to add key {} to cache. Exception type: {}".format(k, e.__class__.__name__)
                    raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

            # update index file at the end of add
            self._update_index_file()

    def get(self, keys: Iterable[str], default: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get deserialized object from store.

        :param keys: store keys
        :param default: returns default value if not present
        :return: deserialized objects
        """
        res = dict()

        with self.log_activity():
            for key in keys:
                try:
                    logger.info("Getting data for key: " + key)
                    # A key may or may not include the default namespace when added to the cache store. Create a list
                    # of possible keys that include and exclude the namespace, and try to match that with the items
                    # that are present in the cache store. The first hit we get is returned.
                    derived_keys = [
                        key,  # the original key
                        f"{Keys.DEFAULT_NAMESPACE}{key}",  # key with the default namespace
                        key.replace(Keys.DEFAULT_NAMESPACE, ""),  # key w/o default namespace
                    ]
                    obj = default  # type: Any
                    for k in derived_keys:
                        item = self.cache_items.get(k, None)
                        if item is not None and item.cv_type == CachedValueMetadata.TYPE_FILE:
                            func = self._extension_to_deserializer.get(item.ext, self._pickler.load)
                            obj = func(item.local_path)
                            break

                    res[key] = obj
                except OSError as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    logger.error(
                        "Failed to get the keys [{}] from the local cache on disk. Error code: {}".format(
                            ",".join(keys), e.errno
                        )
                    )
                    raise CacheException._with_error(
                        AzureMLError.create(
                            CacheOperation,
                            target="cache-get",
                            operation_name="get",
                            path=self._root,
                            os_error_details=str(e),
                        ),
                        inner_exception=e,
                    ) from e
                except Exception as e:
                    logging_utilities.log_traceback(e, logger, is_critical=False)
                    msg = f"Failed to retrieve key {key} from cache. Exception type: {e.__class__.__name__}"
                    raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

        return res

    def add_dir(self, key: str, path: str) -> None:
        """
        Adds a valid local directory to cache store.

        Once a dir key is added, a new key with any of the dir keys as prefix wont be allowed.
        This is to keep contents inside dir key consistent and to prevent any file conflict.
        For instance if a dir key "/foo/bar" is added followed by "/foo/bar/a" it would throw exception.

        :param key: store key
        :type key: str
        :param path: a valid path to a local directory
        :type path: str
        """
        # check if passed val is a valid dir
        if not os.path.isdir(path):
            logger.error("not a directory")
            raise CacheException(exception_message="Not a directory")

        if not self._is_valid_key(key):
            logger.warning(
                "Key {} exists. Cache store doesnot support adding existing dir key".format(key)
            )
            return

        self.cache_items[key] = DirCachedValueMetadata(key=key, local_path=path)
        # update index file
        self._update_index_file()

    def get_dir(self, key: str) -> Optional[str]:
        """
        Get the local path of the directory.

        :param key: key pointing to a directory
        :return: local path if dir key exists or None
        """
        item = self.cache_items.get(key)
        if isinstance(item, DirCachedValueMetadata):
            return item.local_path
        return None

    def _update_index_file(self) -> None:
        try:
            if not os.path.exists(self._indices_dir_path):
                logger.info("Cache folder does not exist. Creating one.")
                self._init_cache_folder()
            with open(self._index_file_path, "w") as f:
                json.dump(self.cache_items, f, cls=_JSONUtils)
        except Exception as e:
            msg = "Failed to save index file. Exception type: {}".format(e.__class__.__name__)
            raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)

    def _sanitize_cache_items(self) -> None:
        """Update cache items post load()."""
        for k, v in self.cache_items.items():
            v.update_local_path(k, self._root)
        # persist new values
        self._update_index_file()

    def _is_valid_key(self, key: str) -> bool:
        if self.cache_items.get(key) is not None:
            return False

        # Split keys on '/' and go through subsequent suffixes to verify a dir key doesnot exist.
        # This is done to make sure, if a dir key `/foo/bar` exists, then keys such as `/foo/bar/a` cannot
        # be inserted to keep the consistency of the dir key `/foo/bar` and to prevent any file conflict.
        key_to_check = ""
        for str in key.split("/"):
            key_to_check += str
            item = self.cache_items.get(key_to_check)
            if item is None:
                # check with trailing slashes
                item = self.cache_items.get(key_to_check + "/")
            if item is not None and item.cv_type == CachedValueMetadata.TYPE_DIR:
                msg = "A directory key " + key_to_check \
                    + " exists. Cannot add a new key in subsequent directories"
                raise CacheException(exception_message=msg)
            key_to_check += "/"

        return True

    def set(self, key: str, value: Any) -> None:
        """
        Set to store.

        :param key: store key
        :param value: store value
        """
        self.add([key], [value])

    def remove(self, key: str) -> None:
        """
        Remove key from store.

        :param key: store key
        """
        to_remove = self.cache_items[key]
        if to_remove.cv_type == CachedValueMetadata.TYPE_DIR:
            shutil.rmtree(to_remove.local_path)
        else:
            os.remove(os.path.join(self._root, to_remove.local_path))
        del self.cache_items[key]

    def remove_all(self) -> None:
        """Remove all the cache from store."""
        self.cache_items = {}
        shutil.rmtree(self._root)

    def get_available_keys(self, path: str) -> Dict[str, str]:
        """
        Get the files available in the cache store, and create a mapping of the keys (with file extensions) pointing
        to their paths on the underlying storage
        This method recursively discovers the keys via. the files available under the `path` specified.

        :return: Dictionary of keys and their corresponding paths on the storage
        """
        extended_key_mapping = {}
        for name in os.listdir(path):
            if os.path.isfile(os.path.join(path, name)):
                file_abs_path = os.path.join(path, name)
                key = pathlib.Path(file_abs_path).relative_to(self._root).as_posix()
                extended_key_mapping[key] = file_abs_path
            else:
                extended_key_mapping.update(self.get_available_keys(os.path.join(path, name)))
        return extended_key_mapping

    def load(self) -> None:
        """Load from store."""
        logger.info("Loading from file cache")
        with self.log_activity():
            if not os.path.exists(self._indices_dir_path):
                msg = "Indices directory does not exist cache store."
                logger.error(msg)
                raise CacheException(exception_message=msg)
            for entry in os.scandir(self._indices_dir_path):
                with open(entry.path, "r") as f:
                    try:
                        cache_items = json.load(f, object_hook=_JSONUtils.decode)
                        for k, v in cache_items.items():
                            if self.cache_items.get(k):
                                logger.info("load() => key {} exists in cache_items".format(k))
                                continue
                            self.cache_items[k] = v
                    except Exception as e:
                        msg = "Failed to load cache items from index file. Exception type: {}".format(
                            e.__class__.__name__
                        )
                        raise CacheException.from_exception(e, msg=msg).with_generic_msg(msg)
            self._update_index_file()

    def unload(self) -> None:
        """Unload from store."""
        self.remove_all()
        self._init_cache_folder()

    def _serialize_pandas_dataframe_as_parquet(self, file_fqn: str, obj: pd.DataFrame) -> str:
        """Serialize a pandas dataframe into a parquet file."""
        Contract.assert_type(value=obj, name="obj", expected_types=pd.DataFrame, log_safe=True)
        return Parqueter.dump_pandas_dataframe(obj, file_fqn)

    def _serialize_numpy_ndarray_as_parquet(self, file_fqn: str, obj: np.ndarray) -> str:
        """Serialize numpy array into a parquet file."""
        Contract.assert_type(value=obj, name="obj", expected_types=np.ndarray, log_safe=True)
        return Parqueter.dump_numpy_array(obj, file_fqn)

    def _serialize_numpy_ndarray(self, file_fqn: str, obj: np.ndarray) -> str:
        Contract.assert_type(value=obj, name="obj", expected_types=np.ndarray)
        np.save(file_fqn, obj, allow_pickle=False)
        return file_fqn

    def _serialize_scipy_sparse_matrix_as_npz(self, file_fqn: str, obj: Any) -> str:
        Contract.assert_true(sparse.issparse(obj), message="`obj` must be a sparse matrix.")
        sparse.save_npz(file_fqn, obj)
        return file_fqn

    def _serialize_sparse_matrix_as_parquet(self, file_fqn: str, obj: sparse.spmatrix) -> str:
        """Serialize a sparse matrix into a parquet file."""
        Contract.assert_true(sparse.issparse(obj), message="`obj` must be a sparse matrix.")
        return Parqueter.dump_sparse_matrix(obj, file_fqn)

    def _serialize_object_as_pickle(self, file_fqn: str, obj: Any) -> str:
        self._pickler.dump(obj, path=file_fqn)
        return file_fqn

    def _serialize_dataframe_as_pickle(self, file_fqn: str, obj: pd.DataFrame) -> str:
        try:
            obj.to_pickle(file_fqn)
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            logger.info("Dataframe to pkl: Failed. Fallback: Failed")
        return file_fqn

    def _get_deserializer_based_on_extension(self, extension: str) -> Callable[[str], Any]:
        """
        Get appropriate deserializer based on extension of the file. Default deserializer is the
        default pickler's load() method.

        :param extension: Extension of the file trying to be deserialized.
        :return: Callable deserializer method.
        """
        deserializer = self._extension_to_deserializer.get(extension, None)
        if deserializer is None:
            logger.info(
                "Did not find deserializer for extension: {}. Falling back to pickler"
                "to load the object".format(extension)
            )

        return deserializer or self._pickler.load

    def _serialize(self, file_name: str, obj: Any) -> FileCachedValueMetadata:
        if isinstance(obj, np.ndarray) and obj.dtype != np.object:
            return self._serialize_numpy_array(file_name=file_name, arr=obj)

        if sparse.issparse(obj):
            return self._serialize_sparse_matrix(file_name=file_name, sp_matrix=obj)

        if isinstance(obj, pd.DataFrame):
            return self._serialize_pandas_dataframe(file_name=file_name, df=obj)

        return self._serialize_object(file_name=file_name, obj=obj)

    def _serialize_object(self, file_name: str, obj: Any) -> FileCachedValueMetadata:
        if isinstance(obj, pd.DataFrame):
            ext = _CacheConstants.FileExtensions.DF_PICKLE_FILE_EXTENSION
            file_name = file_name.partition('.')[0]
            serializer_func = self._serialize_dataframe_as_pickle
        else:
            ext = _CacheConstants.FileExtensions.PICKLE_FILE_EXTENSION
            serializer_func = self._serialize_object_as_pickle
        file_name = ".".join([file_name, ext])

        file_fqn = self._to_fully_qualified_path(file_name)

        os.makedirs(os.path.dirname(file_fqn), exist_ok=True)
        serializer_func(file_fqn, obj)
        return FileCachedValueMetadata(local_path=file_fqn, ext=ext)

    def _serialize_sparse_matrix(
            self,
            file_name: str,
            sp_matrix: sparse.spmatrix
    ) -> FileCachedValueMetadata:
        if isinstance(sp_matrix, sparse.coo_matrix):
            sp_matrix = sp_matrix.tocsr()

        inmemory_size_kb = (sp_matrix.data.nbytes + sp_matrix.indptr.nbytes + sp_matrix.indices.nbytes) / 1000.0
        ext = _CacheConstants.FileExtensions.SCIPY_SPARSE_PARQUET_FILE_EXTENSION
        serializer_func = self._serialize_sparse_matrix_as_parquet
        file_name = ".".join([file_name, ext])
        file_fqn = self._to_fully_qualified_path(file_name)
        try:
            os.makedirs(os.path.dirname(file_fqn), exist_ok=True)
            serializer_func(file_fqn, sp_matrix)
            logger.info("spmatrix to parquet: Success.")
            logger.info(
                f"spmatrix to parquet. Memory: {inmemory_size_kb} kb," f"Disk: {os.path.getsize(file_fqn) / 1000.0} kb"
            )
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            logger.info("spmatrix to parquet: Failed. Fallback: npz")
            ext = _CacheConstants.FileExtensions.SCIPY_SPARSE_FILE_EXTENSION
            serializer_func = self._serialize_scipy_sparse_matrix_as_npz
            file_name = ".".join([file_name, ext])
            file_fqn = self._to_fully_qualified_path(file_name)
            serializer_func(file_fqn, sp_matrix)
            logger.info(
                f"spmatrix to npz. Memory: {inmemory_size_kb} kb," f"Disk: {os.path.getsize(file_fqn) / 1000.0} kb"
            )
        return FileCachedValueMetadata(local_path=file_fqn, ext=ext)

    def _serialize_numpy_array(
        self,
        file_name: str,
        arr: np.ndarray
    ) -> FileCachedValueMetadata:
        inmemory_size_kb = arr.nbytes / 1000.0
        if arr.ndim == 1:
            ext = _CacheConstants.FileExtensions.NUMPY_SINGLE_DIM_FILE_EXTENSION
        else:
            ext = _CacheConstants.FileExtensions.NUMPY_PARQUET_FILE_EXTENSION

        serializer_func = self._serialize_numpy_ndarray_as_parquet
        file_name = ".".join([file_name, ext])
        file_fqn = self._to_fully_qualified_path(file_name)
        try:
            os.makedirs(os.path.dirname(file_fqn), exist_ok=True)
            serializer_func(file_fqn, arr)
            logger.info(
                f"ndarray to parquet. Memory: {inmemory_size_kb} kb, " f"Disk: {os.path.getsize(file_fqn) / 1000.0} kb"
            )
            logger.info("ndarray to parquet: Success.")
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            logger.info("ndarray to parquet: Failed. Fallback: npy")
            ext = _CacheConstants.FileExtensions.NUMPY_FILE_EXTENSION
            serializer_func = self._serialize_numpy_ndarray
            file_name = ".".join([file_name, ext])
            file_fqn = self._to_fully_qualified_path(file_name)
            serializer_func(file_fqn, arr)
            logger.info(
                f"ndarray to npy. Memory: {inmemory_size_kb} kb, " f"Disk: {os.path.getsize(file_fqn) / 1000.0} kb"
            )

        return FileCachedValueMetadata(local_path=file_fqn, ext=ext)

    def _serialize_pandas_dataframe(
        self,
        file_name: str,
        df: pd.DataFrame
    ) -> FileCachedValueMetadata:
        inmemory_size_kb = sum(df.memory_usage(deep=True)) / 1000.0
        ext = _CacheConstants.FileExtensions.DF_PARQUET_FILE_EXTENSION
        serializer_func = self._serialize_pandas_dataframe_as_parquet
        file_name = ".".join([file_name, ext])
        file_fqn = self._to_fully_qualified_path(file_name)
        try:
            os.makedirs(os.path.dirname(file_fqn), exist_ok=True)
            serializer_func(file_fqn, df)
            logger.info("Dataframe to parquet: Success.")
            logger.info(
                f"df to parquet. Memory: {inmemory_size_kb} kb," f"Disk: {os.path.getsize(file_fqn) / 1000.0} kb"
            )
            return FileCachedValueMetadata(local_path=file_fqn, ext=ext)
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            logger.info("Dataframe to parquet: Failed. Fallback: Pickle")
            item = self._serialize_object(file_name=file_name, obj=df)
            logger.info(
                f"df to pickle. Memory: {inmemory_size_kb} kb,"
                # f"Disk: {os.path.getsize(item.get('local_path')) / 1000.0} kb"
                f"Disk: {os.path.getsize(item.local_path) / 1000.0} kb"
            )
            # log stats of the error throwing dataframe
            self.__log_serialize_error_stats(df)
            return item

    def __log_serialize_error_stats(self, df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        for column in df.columns:
            featurized_stats = RawFeatureStats(df[column])
            utilities._log_raw_data_stat(
                featurized_stats,
                prefix_message="[Serialize Error DataFrame ColNum:{}]".format(df.columns.get_loc(column))
            )

    def _write(self, key: str, obj: Any) -> CachedValueMetadata:
        try:
            item = self._serialize(key, obj)
            logger.info("Object type: {}, Uploaded file: ")
            return item
        except Exception:
            logger.error("Uploading {} failed.".format(key))
            raise

    def _split_file_ext(self, path: str) -> Tuple[str, str]:
        """
        Given an arbitrary path with a file name and extension split path+file from extension. We first
        check with the FileExtensions that we use from `CacheConstants.FileExtensions`. If none of those match,
        we will continue with rfind towards the end. Keys might contain '.' so we can use rfind to get the separator
        then split file from extension.

        :param path: File path.
        :return: A tuple containing file name and extension.
        """
        for ext in _CacheConstants.FileExtensions.ALL:
            if path.endswith(ext):
                file_name = path[: len(path) - len(ext) - 1]
                return file_name, ext

        split = path.rfind(".")
        file_name = path[:split]
        ext = path[split + 1:]
        return file_name, ext

    def _to_fully_qualified_path(self, key: str) -> str:
        """
        Returns the fully qualified path of the key (i.e. the path on the local FS), splitting on '/'
        if the key uses namespaces
        """
        return os.path.join(self._root, *key.split("/"))
