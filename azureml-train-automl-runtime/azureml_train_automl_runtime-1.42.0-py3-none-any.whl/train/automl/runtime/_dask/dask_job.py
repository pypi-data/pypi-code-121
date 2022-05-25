# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Callable, Dict, List, Optional
import logging
import threading

from azureml.train.automl.runtime._dask.mpi_dask_cluster import MpiDaskClsuter

logger = logging.getLogger(__name__)


class DaskJob:

    @staticmethod
    def run(
            driver_func: Callable[..., Any],
            driver_func_args: List[Optional[str]] = [],
            driver_func_kwargs: Dict[str, Any] = {}) -> Any:
        """Initialize a Dask cluster and run the driver function on it."""
        cluster = MpiDaskClsuter()
        rank = cluster.start()
        try:
            # Only run the driver function on rank 0
            if rank == 0:
                return driver_func(*driver_func_args, **driver_func_kwargs)
        except Exception as e:
            logger.error(f"Failure during dask job: {type(e)}")
            raise
        finally:
            if rank == 0:
                logger.info("Shutting down dask cluster.")
                shutdown_thread = threading.Thread(target=lambda c: c.shutdown(), args=(cluster,))
                shutdown_thread.start()
                shutdown_thread.join(timeout=10)
                if shutdown_thread.isAlive():
                    logger.info("Failed to shut down dask cluster.")
                else:
                    logger.info("Successfully shut down dask cluster.")
