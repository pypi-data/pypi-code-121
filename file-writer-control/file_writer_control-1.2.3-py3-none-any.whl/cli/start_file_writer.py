import argparse
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from time import time as current_time
from typing import Tuple

from file_writer_control import JobHandler, JobState, WorkerJobPool, WriteJob

JOB_HANDLER: JobHandler
ACK_TIMEOUT: float


def cli_parser() -> argparse.Namespace:
    """
    Parser for the command line interface.
    """

    fw_parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@", description="FileWriter Starter"
    )

    fw_parser.add_argument(
        "-f",
        "--filename",
        metavar="filename",
        type=str,
        required=True,
        help="Name of the output file, e.g., `<filename>.nxs`.",
    )
    fw_parser.add_argument(
        "-j",
        "--job-id",
        metavar="job_id",
        type=str,
        help="The job identifier of the currently running file-writer job. "
        "The job identifier should be a valid UUID.",
    )
    fw_parser.add_argument(
        "-c",
        "--config",
        metavar="json_config",
        type=str,
        required=True,
        help="Path to JSON config file.",
    )
    fw_parser.add_argument(
        "-b",
        "--broker",
        metavar="kafka_broker",
        type=str,
        default="localhost:9092",
        help="Kafka broker port.",
    )
    fw_parser.add_argument(
        "-t",
        "--command-status-topic",
        metavar="consume_topic",
        type=str,
        required=True,
        help="Name of the Kafka topic to listen to" " commands and send status to.",
    )
    fw_parser.add_argument(
        "-p",
        "--job-pool-topic",
        metavar="job_pool_topic",
        type=str,
        required=True,
        help="The Kafka topic that the available file-writers"
        " are listening to for write jobs.",
    )
    fw_parser.add_argument(
        "--timeout",
        metavar="ack_timeout",
        type=float,
        default=5,
        help="How long to wait for timeout on acknowledgement.",
    )
    fw_parser.add_argument(
        "--stop",
        metavar="stop_writing",
        type=float,
        help="How long the file will be written.",
    )

    args = fw_parser.parse_args()

    return args


def file_writer(args: argparse.Namespace) -> None:
    write_job = prepare_write_job(args)
    start_time, timeout = start_write_job(write_job)

    if args.stop:
        stop_write_job(args.stop, start_time, timeout)

    inform_status()


def start_write_job(write_job: WriteJob) -> Tuple[datetime, float]:

    start_handler = JOB_HANDLER.start_job(write_job)
    timeout = int(current_time()) + ACK_TIMEOUT
    start_time = datetime.now()
    while not start_handler.is_done():
        if int(current_time()) > timeout:
            raise ValueError("Timeout.")
    return start_time, timeout


def stop_write_job(stop: float, start_time: datetime, timeout: float) -> None:

    stop_time = start_time + timedelta(seconds=stop)
    stop_handler = JOB_HANDLER.set_stop_time(stop_time)
    while not stop_handler.is_done() and not JOB_HANDLER.is_done():
        if int(current_time()) > timeout:
            raise ValueError("Timeout.")


def stop_write_job_now() -> None:
    if JOB_HANDLER.get_state() == JobState.WRITING:
        JOB_HANDLER.set_stop_time(datetime.now())
        while not JOB_HANDLER.is_done():
            time.sleep(1)
        print("FileWriter successfully stopped.")
    sys.exit()


def prepare_write_job(args: argparse.Namespace) -> WriteJob:
    global JOB_HANDLER
    global ACK_TIMEOUT

    file_name = args.filename
    job_id = args.job_id
    host = args.broker
    command_topic = args.command_status_topic
    pool_topic = args.job_pool_topic
    config = args.config
    ACK_TIMEOUT = args.timeout
    command_channel = WorkerJobPool(f"{host}/{pool_topic}", f"{host}/{command_topic}")
    JOB_HANDLER = JobHandler(worker_finder=command_channel)
    with open(config, "r") as f:
        nexus_structure = f.read()
    if job_id:
        write_job = WriteJob(
            nexus_structure, file_name, host, datetime.now(), job_id=job_id
        )
    else:
        write_job = WriteJob(
            nexus_structure,
            file_name,
            host,
            datetime.now(),
        )
    return write_job


def inform_status() -> None:
    if JOB_HANDLER.get_state() == JobState.WRITING:
        print("Use CTRL-C to enter interactive menu.")
        print("Writing.", end="", flush=True)
    while JOB_HANDLER.get_state() == JobState.WRITING:
        print(".", end="", flush=True)
        time.sleep(1)
        if JOB_HANDLER.get_state() == JobState.DONE:
            print("[DONE]")


def validate_namespace(args: argparse.Namespace) -> None:
    argument_list = [
        args.filename,
        args.config,
        args.broker,
        args.command_status_topic,
        args.job_pool_topic,
    ]
    for arg in argument_list:
        is_empty(arg)

    # Validate extensions for filename and config
    check_file_extension(args.filename, "nxs")
    check_file_extension(args.config, "json")

    # Validate JSON config path
    config_file = args.config
    if not os.path.isfile(config_file):
        raise ValueError(
            "The configuration file " f"`{config_file}` " "does not exist."
        )


def check_file_extension(arg: str, extension: str) -> None:
    if len(arg.split(".")) < 2 or arg.split(".")[1] != extension:
        raise ValueError(
            f"The argument, {arg}, has incorrect extension. "
            "Please use `.nxs` for output file and `.json` for "
            "the configuration."
        )
    is_empty(arg.split(".")[0])


def is_empty(arg: str) -> None:
    if not arg or arg.isspace():
        raise ValueError("A positional argument cannot be an empty string.")


def ask_user_action(signum, frame) -> None:
    user_action = """

    What would you like to do (type 1, 2 or 3 and press Enter)?

    1- Stop FileWriter immediately
    2- Stop FileWriter after a given time (seconds)
    3- Exit CLI without terminating FileWriter

    Or any other key to Continue.

    """

    choice = input(user_action)

    if choice == "1":
        stop_write_job_now()
    elif choice == "2":
        set_time_and_stop()
    elif choice == "3":
        sys.exit()
    else:
        return


def set_time_and_stop() -> None:
    stop_time = input("Stop time in seconds = ")
    try:
        stop_time = float(stop_time)
        timeout = int(current_time()) + ACK_TIMEOUT
        stop_write_job(stop_time, datetime.now(), timeout)
    except ValueError:
        # The CLI will simply continue.
        print("Input should be a float.")


def start_writer():
    # Catch ctrl-c
    signal.signal(signal.SIGINT, ask_user_action)
    # Main
    cli_args = cli_parser()
    validate_namespace(cli_args)
    file_writer(cli_args)


if __name__ == "__main__":
    start_writer()
