import sys
import time
import argparse

from powerful_pipes import read_json_from_stdin, write_json_to_stdout, \
    NotConnectedToPipe, report, REPORT_LEVEL


def main():
    parser = argparse.ArgumentParser(
        description='Ticker input data'
    )
    parser.add_argument('-b', '--banner',
                        default=False,
                        action="store_true",
                        help="displays tool banner")
    parser.add_argument('-t', '--tag',
                        required=True,
                        help="tag name")
    parsed = parser.parse_args()


    if parsed.banner:
        print(f"[*] Starting Powerful-pipes Ticker", flush=True, file=sys.stderr)


    try:
        for error, input_json in read_json_from_stdin():

            if error:
                report(
                    {},
                    log_level=REPORT_LEVEL.ERROR,
                    message=f"[Ticker] Error processing input JSON: {input_json}"
                )

            else:

                input_json.setdefault("_meta", {}).setdefault("chain", []).append(
                    {parsed.tag: {"executionTime": time.time()}}
                )

                write_json_to_stdout(input_json, force_flush=True)

    except NotConnectedToPipe:
        write_json_to_stdout({
            "_meta": {"chain": [{parsed.tag: {"executionTime": time.time()}}]}
        }, force_flush=True)

    except KeyboardInterrupt:
        ...


if __name__ == '__main__':
    main()
