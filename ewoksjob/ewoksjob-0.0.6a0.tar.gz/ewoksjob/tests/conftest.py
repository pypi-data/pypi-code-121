import gc
import os
import pytest
from ewokscore import events
from ewoksjob.events.readers import instantiate_reader
from ewokscore.events import cleanup
from .utils import has_redis_server
from ..client import process

if has_redis_server():

    @pytest.fixture(scope="session")
    def celery_config(redis_proc):
        url = f"redis://{redis_proc.host}:{redis_proc.port}"
        # celery -A ewoksjob.apps.ewoks --broker={url}/0 --result-backend={url}/1 inspect stats -t 5
        return {
            "broker_url": f"{url}/0",
            "result_backend": f"{url}/1",
            "result_serializer": "pickle",
            "accept_content": ["application/json", "application/x-python-serialize"],
        }

else:

    @pytest.fixture(scope="session")
    def celery_config(tmpdir_factory):
        tmpdir = tmpdir_factory.mktemp("celery")
        return {
            "broker_url": "memory://",
            # "broker_url": f"sqla+sqlite:///{tmpdir / 'celery.db'}",
            "result_backend": f"db+sqlite:///{tmpdir / 'celery_results.db'}",
            "result_serializer": "pickle",
            "accept_content": ["application/json", "application/x-python-serialize"],
        }


@pytest.fixture(scope="session")
def celery_includes():
    return ("ewoksjob.apps.ewoks",)


@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {"loglevel": "debug"}


@pytest.fixture(scope="session")
def celery_worker_pool():
    if os.name == "nt":
        # "prefork" doesn't work on windows
        return "solo"
    else:
        # some tests may require more than one worker
        return "prefork"


@pytest.fixture()
def ewoks_worker(celery_session_worker, celery_worker_pool):
    yield celery_session_worker
    if celery_worker_pool == "solo":
        events.cleanup()


@pytest.fixture(scope="session")
def local_ewoks_worker():
    with process.pool_context(max_worker=8) as pool:
        yield
        while gc.collect():
            pass
        assert len(pool._jobs) == 0


@pytest.fixture()
def sqlite3_ewoks_events(tmpdir):
    uri = f"file:{tmpdir / 'ewoks_events.db'}"
    handlers = [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": uri}],
        }
    ]
    reader = instantiate_reader(uri)
    yield handlers, reader
    reader.close()
    cleanup()


@pytest.fixture()
def redis_ewoks_events(redisdb):
    url = f"unix://{redisdb.connection_pool.connection_kwargs['path']}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [{"name": "url", "value": url}],
        }
    ]
    reader = instantiate_reader(url)
    yield handlers, reader
    reader.close()
    cleanup()
