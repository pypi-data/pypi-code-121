import argparse
import tempfile
import time
from datetime import date, datetime
from typing import Tuple

import pandas as pd
import pytz
from loguru import logger

from skit_calls import __version__, calls
from skit_calls import constants as const
from skit_calls import utils


def to_datetime(date_string: str | None) -> datetime:
    """
    Check if date_string is in YYYY-MM-DD format.

    :param date_string: A string representing a date in YYYY-MM-DD format.
    :type date_string: [type]
    """
    if not date_string:
        return date_string
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: expected YYYY-MM-DD for {date_string} instead, {e}"
        )


def validate_date_ranges(start_date: datetime, end_date: datetime) -> None:
    """
    Check if start_date is before end_date.

    :param start_date: A datetime object representing a former date.
    :type start_date: datetime
    :param end_date: A datetime object representing a latter date.
    :type end_date: datetime
    """
    if start_date > end_date:
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        raise ValueError(f"{start_date=} shouldn't be later than {end_date=}.")


def process_date_filters(
    start_date: datetime | None,
    end_date: datetime | None,
    timezone: str = const.DEFAULT_TIMEZONE,
) -> Tuple[str, str]:
    """
    Process the date filters.

    Make timestamps timezone aware and provide their ISO-8601 representation.

    :param start_date: A datetime object representing a former date.
    :type start_date: datetime
    :param end_date: A datetime object representing a latter date.
    :type end_date: datetime
    :param timezone: The timezone to use for the start and end dates.
    :type timezone: str
    """
    today = date.today()

    if not start_date:
        start_date = datetime.combine(today, datetime.min.time())
    if not end_date:
        end_date = datetime.combine(today, datetime.max.time())

    start_date = start_date.replace(tzinfo=pytz.timezone(timezone)).isoformat()
    end_date = end_date.replace(tzinfo=pytz.timezone(timezone)).isoformat()
    return start_date, end_date


def get_version():
    return __version__


def build_sample_command(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--lang",
        type=str,
        help="Search calls made in the given language.",
        required=True,
    )
    parser.add_argument(
        "--org-id",
        type=str,
        help="The org for which you need the data.",
    )
    parser.add_argument(
        "--start-date",
        type=to_datetime,
        default=None,
        help="Search calls made after the given date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end-date",
        type=to_datetime,
        help="Search calls made before the given date.",
        default=None,
    )
    parser.add_argument(
        "--timezone",
        type=str,
        help="The timezone to use for the start and end dates.",
        default=const.DEFAULT_TIMEZONE,
    )
    parser.add_argument(
        "--call-quantity",
        type=int,
        help="The number of calls to filter.",
        default=const.DEFAULT_CALL_QUANTITY,
    )
    parser.add_argument(
        "--call-type",
        type=str,
        help="The type of call to filter.",
        default=const.INBOUND,
        choices=[const.INBOUND, const.OUTBOUND, const.CALL_TEST],
    )
    parser.add_argument(
        "--ignore-callers",
        type=str,
        nargs="*",
        help="A comma separated list of callers to ignore.",
        default=const.DEFAULT_IGNORE_CALLERS_LIST,
    )
    parser.add_argument(
        "--reported", action="store_true", help="Search only reported calls."
    )
    parser.add_argument("--use-case", help="Filter calls by use-case.")
    parser.add_argument("--flow-name", help="Filter calls by flow-name.")
    parser.add_argument(
        "--min-audio-duration",
        type=float,
        help="Filter calls longer than given duration.",
    )
    parser.add_argument(
        "--asr-provider", help="Filter calls served via a specific ASR provider."
    )

    parser.add_argument(
        "--states",
        type=str,
        nargs="*",
        help="A comma separated list of states to keep turns from, and remove all else.",
        default=[],
    )


def build_select_command(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--call-ids", type=str, nargs="+", help="The call-ids to select."
    )
    group.add_argument("--csv", help="CSV file that contains the call-ids to select.")
    parser.add_argument(
        "--org-id",
        help="The org for which you need the data. Required if --csv is set.",
    )
    parser.add_argument(
        "--uuid-column",
        help="The column name of the UUID column in the CSV file. Required if --csv is set.",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Collect call history for each turn",
        default=False,
    )


def build_cli():
    version = get_version()
    parser = argparse.ArgumentParser(
        description=const.DESCRIPTION.format(version={version})
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=4, help="Increase verbosity"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Supported means to obtain calls datasets aggregated with their turns.",
    )
    build_sample_command(
        subparsers.add_parser(
            "sample", help="Random sample calls with a variety of call/turn filters."
        )
    )
    build_select_command(
        subparsers.add_parser("select", help="Select calls from known call-ids.")
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=const.Q_DELAY,
        help="Some queries may timeout and need some delay"
        " before a new connection is established."
        " The value should be a between (0-0.5).",
    )

    parser.add_argument(
        "--batch-turns",
        type=int,
        default=const.TURNS_LIMIT,
        help="Maximum number of turns to be collected in a single batch.",
    )

    parser.add_argument(
        "--on-disk",
        action="store_true",
        help="Each record is written directly to disk. Highly recommended for large queries.",
        default=True,
    )
    return parser


def random_sample_calls(args: argparse.Namespace) -> str | pd.DataFrame:
    args.start_date, args.end_date = process_date_filters(
        args.start_date, args.end_date
    )
    validate_date_ranges(args.start_date, args.end_date)
    start = time.time()
    maybe_df = calls.sample(
        args.org_id,
        args.start_date,
        args.end_date,
        args.lang,
        call_quantity=args.call_quantity,
        call_type=args.call_type,
        ignore_callers=args.ignore_callers,
        reported=args.reported,
        use_case=args.use_case,
        flow_name=args.flow_name,
        min_duration=args.min_audio_duration,
        asr_provider=args.asr_provider,
        states=args.states,
        on_disk=args.on_disk,
        batch_turns=args.batch_turns,
        delay=args.delay,
    )
    logger.info(f"Finished in {time.time() - start:.2f} seconds")
    return maybe_df


def cmd_to_str(args: argparse.Namespace) -> str:
    utils.configure_logger(args.verbose)

    maybe_df = None
    if args.command == "sample":
        maybe_df = random_sample_calls(args)
    elif args.command == "select":
        maybe_df = calls.select(
            args.call_ids,
            args.org_id,
            args.csv,
            args.uuid_column,
            args.history,
            on_disk=args.on_disk,
            delay=args.delay,
        )
    else:
        raise argparse.ArgumentError(f"Unknown command {args.command}")

    if args.on_disk:
        print(maybe_df)
    else:
        _, file_path = tempfile.mkstemp(suffix=const.CSV_FILE)
        maybe_df.to_csv(file_path, index=False)
        print(file_path)


def main() -> None:
    """
    Main entry point for the CLI.

    - We try to read token from the pipes if not passed as an arguments.
    - Process the request for sampling calls.
    - Collect the results:
        - In a single file if save is set to IN_MEMORY.
            - Print the file path to stdout.
        - In multiple files if save is set to FILES.
            - Print the directory path to stdout.
    """
    cmd_to_str(build_cli().parse_args())
