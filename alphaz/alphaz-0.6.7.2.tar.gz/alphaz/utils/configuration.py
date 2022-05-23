import argparse, os
os.environ["ALPHA_LOG_CMD_OUTPUT"] = "N"

from ..models.config import AlphaConfig

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load configuration file")

    parser.add_argument("--log", "-l", help="log file path")
    parser.add_argument("--file", "-f", help="Input configuration file", required=True)
    parser.add_argument("--configuration", "-c", help="Configuration", default=None)
    parser.add_argument("--user", "-u", help="User", default=None)
    parser.add_argument("--path", "-p", help="Input parameter path", required=True)

    args = parser.parse_args()

    config = AlphaConfig(filepath=args.file, configuration=args.configuration, user=args.user)

    if config is None:
        print("None")
    else:
        print(config.get(args.path))
