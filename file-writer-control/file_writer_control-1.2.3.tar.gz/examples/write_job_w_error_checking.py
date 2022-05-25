import time
from datetime import datetime, timedelta

from file_writer_control import CommandState
from file_writer_control import JobHandler
from file_writer_control import JobState
from file_writer_control import WorkerJobPool
from file_writer_control import WriteJob

if __name__ == "__main__":
    kafka_host = "dmsc-kafka01:9092"
    worker_job_pool = WorkerJobPool(
        "{}/job_topic".format(kafka_host), "{}/command_topic".format(kafka_host)
    )
    job_handler = JobHandler(worker_finder=worker_job_pool)
    start_time = datetime.now()
    with open("file_writer_config.json", "r") as f:
        nexus_structure = f.read()
    write_job = WriteJob(
        nexus_structure,
        "{0:%Y}-{0:%m}-{0:%d}_{0:%H}{0:%M}.nxs".format(start_time),
        kafka_host,
        start_time,
    )

    print("Starting write job")
    start_handler = job_handler.start_job(write_job)
    while not start_handler.is_done():
        print("Waiting: {}".format(start_handler.get_state()))
        if start_handler.get_state() == CommandState.ERROR:
            print(
                "Got error when starting job. The error was: {}".format(
                    start_handler.get_message()
                )
            )
            exit(-1)
        elif start_handler.get_state() == CommandState.TIMEOUT_RESPONSE:
            print("Failed to start write job due to start command timeout.")
            exit(-1)
        time.sleep(1)
    print("Write job started")
    stop_time = start_time + timedelta(seconds=60)
    print("Setting stop time")
    stop_handler = job_handler.set_stop_time(stop_time)

    while not stop_handler.is_done():
        time.sleep(1)
        if stop_handler.get_state() == CommandState.ERROR:
            print(
                f"Got error when starting job. The error was: {start_handler.get_message()}"
            )
            exit(-1)
        elif stop_handler.get_state() == CommandState.TIMEOUT_RESPONSE:
            print("Failed to set stop time for write job due to timeout.")
            exit(-1)
    print("Stop time has been set")
    print("Waiting for write job to finish")
    while not job_handler.is_done():
        if job_handler.get_state() == JobState.ERROR:
            print(f"Got job error. The error was: {job_handler.get_message()}")
            exit(-1)
        time.sleep(1)
    print("Write job finished")
