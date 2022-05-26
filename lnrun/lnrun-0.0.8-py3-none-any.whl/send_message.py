import argparse
import os
import subprocess
import urllib.parse

from lnrun.config import get_script_path, get_config


def parse_args(additional: bool = False) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    if additional:
        parser.add_argument('COMMAND', help='command to use')
    parser.add_argument('message', help='message to send')
    return parser.parse_args()


def send_message(message: str) -> None:
    script_path = get_script_path()
    if script_path is None:
        print('script path is not setted, run "lnrun set_config script_path https://your.path.here" to set your path')
        exit()

    urltext = urllib.parse.quote(message)

    verbose = get_config('verbose')
    if verbose:
        os.system(f'curl {script_path}?status={urltext}')
    else:
        subprocess.call(f'curl {script_path}?status={urltext}', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main(additional: bool = False) -> None:
    args = parse_args(additional)
    send_message(args.message)


if __name__ == '__main__':
    main()
