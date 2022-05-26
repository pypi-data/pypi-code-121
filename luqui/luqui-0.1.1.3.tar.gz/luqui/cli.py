import argparse
import sys
import toml
from pathlib import Path


def main():
    """Console script for luqui."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_file",
        # type=argparse.FileType(mode="rb"),
        help="File containing all the necessary parameters to run the protocol",
    )
    args = parser.parse_args()

    config = toml.load(Path(args.config_file))
    print(config["path"]["folder"])

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
