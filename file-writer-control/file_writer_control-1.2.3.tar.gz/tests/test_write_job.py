from copy import copy
from datetime import datetime, timedelta

from streaming_data_types import deserialise_pl72

from file_writer_control.WriteJob import WriteJob


def test_write_generate_job_id():
    under_test = WriteJob("", "", "", datetime.now())
    old_job_id = copy(under_test.job_id)
    under_test.generate_new_job_id()
    assert old_job_id != under_test.job_id


def test_get_start_message():
    under_test = WriteJob("", "", "", datetime.now())
    assert type(under_test.get_start_message()) is bytes


def test_get_start_message_contents():
    structure = "some structure"
    file_name = "some file name"
    start_time = datetime.now()
    stop_time = start_time + timedelta(seconds=10)
    service_id = "some service id"
    broker = "some broker"
    instrument_name = "some instrument name"
    metadata = "some meta data"
    run_name = "some run name"
    under_test = WriteJob(
        nexus_structure=structure,
        file_name=file_name,
        broker=broker,
        start_time=start_time,
        stop_time=stop_time,
        instrument_name=instrument_name,
        run_name=run_name,
        metadata=metadata,
    )
    under_test.service_id = service_id
    message = deserialise_pl72(under_test.get_start_message())
    assert message.nexus_structure == structure
    assert message.filename == file_name
    assert message.service_id == service_id
    assert message.broker == broker
    assert message.instrument_name == instrument_name
    assert message.run_name == run_name
    assert message.start_time == int(start_time.timestamp() * 1000)
    assert message.stop_time == int(stop_time.timestamp() * 1000)
    assert message.job_id == under_test.job_id
    assert message.instrument_name == instrument_name
    assert message.metadata == metadata
