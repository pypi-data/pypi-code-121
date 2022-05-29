import sys
from argparse import ArgumentParser, Namespace
from urllib.error import HTTPError
from urllib.request import urlopen


def eprint(*values: object):
    print(*values, file=sys.stderr)


def parse_args():
    parser = ArgumentParser(description="Health check website")
    parser.add_argument(
        "url", type=str,
        help="url to query for status"
    )
    parser.add_argument(
        "--timeout", dest="timeout",
        type=float, default=0.3,
        help="timeout before connection fail"
    )
    return parser.parse_args()


def main(args: Namespace):
    try:
        with urlopen(
            args.url,
            timeout=args.timeout,
        ) as response:
            if response.read().decode() != "🆗":
                eprint(f"⛔ missing '🆗' in response")
            else:
                print("🆗")
                return
    except HTTPError as err:
        eprint(f"⛔ http status '{err.code}'")

    exit(1)


if __name__ == "__main__":
    args = parse_args()
    main(args)
