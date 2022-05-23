import pytest
import datetime
import threading
from ewokscore import events
from .utils import has_redis_server


@pytest.mark.skipif(not has_redis_server(), reason="redis-server not installed")
def test_redis(redis_ewoks_events):
    handlers, reader = redis_ewoks_events
    assert_event_reader(handlers, reader)


def test_sqlite3(sqlite3_ewoks_events):
    handlers, reader = sqlite3_ewoks_events
    assert_event_reader(handlers, reader)


@pytest.mark.skipif(not has_redis_server(), reason="redis-server not installed")
def test_redis_stop_wait_events(redis_ewoks_events):
    _, reader = redis_ewoks_events

    stop_event = threading.Event()

    thread = threading.Thread(
        target=reader.wait_events, kwargs={"stop_event": stop_event}, daemon=True
    )
    thread.start()

    stop_event.set()
    thread.join(timeout=3)
    assert not thread.is_alive()


def test_sqlite3_stop_wait_events(sqlite3_ewoks_events):
    _, reader = sqlite3_ewoks_events

    stop_event = threading.Event()

    thread = threading.Thread(
        target=reader.wait_events, kwargs={"stop_event": stop_event}, daemon=True
    )
    thread.start()

    stop_event.set()
    thread.join(timeout=3)
    assert not thread.is_alive()


def assert_event_reader(handlers, reader):
    execinfo = {
        "job_id": 123,
        "workflow_id": 456,
        "host_name": None,
        "user_name": None,
        "process_id": None,
        "handlers": handlers,
    }
    events.send_workflow_event(execinfo=execinfo, event="start")
    events.send_workflow_event(execinfo=execinfo, event="end")

    evts = list(reader.wait_events(timeout=1))
    assert len(evts) == 2

    evts = list(reader.get_events(type="end"))
    assert len(evts) == 1
    evts = list(reader.get_full_job_events(type="end"))
    assert len(evts) == 1
    assert len(evts[0]) == 2
    evts = list(reader.get_events(type="progress"))
    assert len(evts) == 0
    evts = list(reader.get_full_job_events(type="progress"))
    assert len(evts) == 0

    evts = list(reader.get_events(job_id=123))
    assert len(evts) == 2
    evts = list(reader.get_full_job_events(job_id=123))
    assert len(evts) == 1
    assert len(evts[0]) == 2

    now = datetime.datetime.now().astimezone()
    starttime = now - datetime.timedelta(minutes=1)
    endtime = now + datetime.timedelta(minutes=1)
    evts = list(reader.get_events(starttime=starttime, endtime=endtime))
    assert len(evts) == 2
    evts = list(
        reader.get_full_job_events(type="end", starttime=starttime, endtime=endtime)
    )
    assert len(evts) == 1
    assert len(evts[0]) == 2

    evts = list(reader.get_events(endtime=starttime))
    assert len(evts) == 0
    evts = list(reader.get_full_job_events(endtime=starttime))
    assert len(evts) == 0
