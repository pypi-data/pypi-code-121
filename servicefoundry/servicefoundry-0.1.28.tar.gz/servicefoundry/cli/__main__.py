import sys

from servicefoundry.cli import create_service_foundry_cli


def main():
    # Exit the interpreter by raising SystemExit(status).
    # If the status is omitted or None, it defaults to zero (i.e., success).
    # If the status is an integer, it will be used as the system exit status.
    # If it is another kind of object, it will be printed and the system exit status will be one (i.e., failure).
    sys.exit(create_service_foundry_cli()())


if __name__ == "__main__":
    main()
