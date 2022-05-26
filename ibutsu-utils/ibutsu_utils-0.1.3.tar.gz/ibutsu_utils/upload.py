import asyncio
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

from ibutsu_client import ApiClient
from ibutsu_client import ApiException
from ibutsu_client import Configuration
from ibutsu_client.api.import_api import ImportApi

CA_BUNDLE_ENVS = ["REQUESTS_CA_BUNDLE", "IBUTSU_CA_BUNDLE"]


def parse_args():
    """Parse and return the command line arguments"""
    parser = ArgumentParser(description="A tool to upload a jUnit XML or Ibutsu archive to Ibutsu")
    parser.add_argument("input", nargs="+", help="The file(s) to upload")
    parser.add_argument(
        "-H",
        "--host",
        required=True,
        help="The Ibutsu instance for uploading, e.g. https://my.ibutsu.com/api",
    )
    parser.add_argument("-p", "--project", required=True, help="The project for the upload")
    parser.add_argument("-t", "--api-token", help="An API token for authentication")
    parser.add_argument("-s", "--source", help="The source used in the test results")
    parser.add_argument(
        "-m",
        "--metadata",
        action="append",
        help="Additional metadata to set when uploading, in the format of dotted.key.path=value",
    )
    parser.add_argument(
        "-w",
        "--wait",
        action="store_true",
        help="Wait for the upload to complete (by default this command does not wait)",
    )
    return parser.parse_args()


def parse_metadata(metadata_list):
    """Parse the metadata from a set of strings to a dictionary"""
    if not metadata_list:
        return {}
    metadata = {}
    # Loop through the list of metadata values
    for pair in metadata_list:
        # Split the key part from the value
        key_path, value = pair.split("=", 1)
        # Split the key up if it is a dotted path
        keys = key_path.split(".")
        current_data = metadata
        # Loop through all but the last key and create the dictionary structure
        for key in keys[:-1]:
            if key not in current_data:
                current_data[key] = {}
            current_data = current_data[key]
        # Finally, set the actual value
        key = keys[-1]
        # Properly process list types
        if "," in value:
            value = value.split(",")
        current_data[key] = value
    return metadata


def get_import_api(host, token=None):
    """Set up an API client that can connect to Ibutsu, and then set up and return the Import API"""
    config = Configuration(access_token=token)
    config.host = host

    # Only set the SSL CA cert if one of the environment variables is set
    for env_var in CA_BUNDLE_ENVS:
        if os.getenv(env_var, None):
            config.ssl_ca_cert = os.getenv(env_var)

    return ImportApi(ApiClient(config))


async def import_async(import_api, filename, project, source, metadata):
    """Import a file and wait for its completion"""
    try:
        # Start the upload
        import_file = Path(filename).resolve()
        if not import_file.exists():
            print("WARNING: {} does not exist".format(filename), file=sys.stderr)
            return True, "File does not exist"
        import_ = import_api.add_import(
            import_file.open("rb"), project=project, source=source, metadata=metadata
        )
        while import_.status in ["pending", "running"]:
            # Wait for a second
            await asyncio.sleep(1)
            import_ = import_api.get_import(import_.id)
        if import_.status != "done":
            return False, "Error importing {}".format(filename)
        else:
            return True, import_
    except ApiException as e:
        return False, "Error uploading {}: {}".format(filename, str(e))


async def import_and_wait(import_api, filenames, project, source, metadata):
    """Import a list of files and wait for their completion"""
    tasks = []
    errors = []
    for filename in filenames:
        tasks.append(
            asyncio.create_task(import_async(import_api, filename, project, source, metadata))
        )
    for task in tasks:
        is_success, message = await task
        if not is_success:
            errors.append(message)
    return errors


def import_without_waiting(import_api, filenames, project, source, metadata):
    """Import a list of files without waiting for their completion"""
    errors = []
    for filename in filenames:
        try:
            import_file = Path(filename).resolve()
            if not import_file.exists():
                print("WARNING: {} does not exist".format(filename), file=sys.stderr)
                break
            import_api.add_import(
                import_file.open("rb"), project=project, source=source, metadata=metadata
            )
        except ApiException as e:
            errors.append("Error uploading {}: {}".format(filename, str(e)))
    return errors


def main():
    """Run the script"""
    args = parse_args()
    metadata = parse_metadata(args.metadata)
    import_api = get_import_api(args.host, args.api_token)
    errors = []
    if not args.wait:
        errors = import_without_waiting(import_api, args.input, args.project, args.source, metadata)
    else:
        errors = asyncio.run(
            import_and_wait(import_api, args.input, args.project, args.source, metadata)
        )
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
