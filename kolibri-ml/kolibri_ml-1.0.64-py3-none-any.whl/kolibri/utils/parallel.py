try:
    import dask
    import distributed
    has_dask=True
except:
    has_dask=False

import tempfile

def create_dask_client(cpu_count):
    dask_client=None
    if has_dask:
        dask_client = distributed.Client(  n_workers=cpu_count,
                threads_per_worker=1,
                local_directory=tempfile.gettempdir(),
                memory_limit='auto',
            # Heartbeat every 10s
            heartbeat_interval=10000,
        )

    return dask_client
def close_dask_client(dask_client):
    if dask_client is not None:
        dask_client.shutdown()
        dask_client.close()
        del dask_client
