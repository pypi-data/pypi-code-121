"""
Dump TC2100 temperature readings to CSV
"""

import argparse
import sys
import os
from typing import TextIO

from twisted.internet import reactor
from twisted.internet.serialport import SerialPort

from tc2100.protocol import ThermometerToCSVProtocol
from tc2100.discover import discover
from tc2100.version import __version__ as version


_APPLICATION_NAME = 'tc2100dump'


def main():
    """ Run the program """
    parser = get_arg_parser()
    args = parser.parse_args()
    if args.version:
        print(version_string(), file=sys.stderr)
        sys.exit(0)

    port_name = args.port
    if not port_name:
        # Autodiscover
        ports = discover()
        if not ports:
            print("Cannot find a TC2100 compatible digital thermometer.\n\n"
                  "If you have one attached and powered on, check that its\n"
                  "USB product ID and vendor ID are listed in the discover\n"
                  "module. You can manually specify a serial port address\n"
                  "with the --port option.", file=sys.stderr)
            sys.exit(1)
        port_name = ports[0].device

    run_dump_to_csv(port_name, args.out)


def get_arg_parser() -> argparse.ArgumentParser:
    """ Obtain the argparse for the executable

    :return: Argument parser
    """
    parser = argparse.ArgumentParser(
        description="Dump values from a digital thermometer")
    parser.add_argument("--port", type=str, required=False,
                        help="Path to serial port, like /dev/ttyUSB0 or COM1")
    parser.add_argument("--out", type=str, required=False,
                        help="Output file. Use '-' for stdout.")
    parser.add_argument("--version", action='store_true',
                        help="Print version and exit")

    return parser


def run_dump_to_csv(port: str, file_name: str = None):
    """ Connect to a TC2100 and dump its output to a file

    :param port: Serial port
    :param file_name: Destination file
    :return: Zero on success, or non-zero for error
    """

    if not file_name or file_name == '-':
        _make_stdout_linebuffered()
        _run_dump(port, sys.stdout)
        return

    with open(
            file_name,
            mode='w',
            newline='',
            buffering=1,
            encoding='utf-8') as outfile:
        _run_dump(port, outfile)


def version_string() -> str:
    """ Obtain a version string for this executable

    :return Version string
    """
    return f"{_APPLICATION_NAME} version {version}"


def _make_stdout_linebuffered() -> None:
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except TypeError:
        sys.stdout = os.fdopen(0, 'w', 1)
    except AttributeError:
        sys.stdout = os.fdopen(0, 'w', 1)


def _run_dump(port: str, file_handle: TextIO) -> None:
    SerialPort(ThermometerToCSVProtocol(file_handle=file_handle),
               port, reactor, baudrate=9600)
    reactor.run()  # pylint: disable=no-member


if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
