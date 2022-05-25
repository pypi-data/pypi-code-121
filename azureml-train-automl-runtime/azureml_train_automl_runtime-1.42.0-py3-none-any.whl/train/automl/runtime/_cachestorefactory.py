# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Factory class that automatically selects the appropriate cache store."""
import logging
from typing import Optional

from azureml.automl.runtime.shared import lazy_file_cache_store as lfcs
from azureml.automl.runtime.shared.run_backed_cache_store import RunBackedCacheStore
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.runtime.shared.file_dataset_cache import FileDatasetCache
from azureml.automl.runtime.shared.memory_cache_store import MemoryCacheStore
from azureml.core import Run
from azureml.data.azure_storage_datastore import AzureBlobDatastore

from azureml.automl.core.shared._diagnostics.contract import Contract

logger = logging.getLogger(__name__)


class CacheStoreFactory:

    @staticmethod
    def get_cache_store(temp_location: str,
                        run_target: str,
                        data_store: Optional[AzureBlobDatastore] = None,
                        run: Optional[Run] = None,
                        task_timeout: int = lfcs._CacheConstants.DEFAULT_TASK_TIMEOUT_SECONDS,
                        use_fd_cache: bool = False,
                        ) -> CacheStore:
        """Get the cache store based on run type."""
        try:
            if run is None:
                return MemoryCacheStore()
            elif run is not None and run_target != "local":
                # Only used FileDataset cache if the env var is set.
                if use_fd_cache:
                    Contract.assert_type(data_store, name='data_store', expected_types=AzureBlobDatastore)
                    return FileDatasetCache(
                        data_store=data_store, blob_path=run.id, task_timeout=task_timeout
                    )
                else:
                    return RunBackedCacheStore(run=run, temp_dir_path=temp_location)

            return lfcs.LazyFileCacheStore(path=temp_location)
        except Exception as e:
            run_id = run.id if run else "Not Available"
            logger.warning("Cannot proceed with the Run ({}) without a valid storage for intermediate files. "
                           "Encountered an exception of type: {}".format(run_id, type(e)))
            raise
