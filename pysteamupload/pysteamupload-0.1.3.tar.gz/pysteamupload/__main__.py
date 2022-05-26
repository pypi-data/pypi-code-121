import os
import argparse
import platform
from dotenv import load_dotenv
from pysteamupload.linux_pysteam import LinuxPySteam
from pysteamupload.windows_pysteam import WindowsPySteam


def parse_argv() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-ai", "--app_id", help="specify which application is being targeted", type=int, required=True)
    parser.add_argument("-di", "--depot_id", help="specify which depot is being targeted", type=int, required=True)
    parser.add_argument("-bd", "--build_description", help="specify build description", type=str, required=True)
    parser.add_argument("-cp", "--content_path", help="specify which local directory should be uploaded", type=str, required=True)
    return parser.parse_args()


def check_required_variables() -> None:
    required_env_vars = (
        "STEAM_USERNAME",
        "STEAM_PASSWORD",
        "STEAM_CONFIG_VDF_FILE_CONTENT",
        "STEAM_SSFN_FILENAME",
        "STEAM_SSFN_FILE_CONTENT",
    )
    missing_keys = []
    for key in required_env_vars:
        if key not in os.environ:
            missing_keys.append(key)
    if missing_keys:
        raise KeyError(f"Missing environment variables {missing_keys}")


def main() -> None:
    load_dotenv()
    check_required_variables()

    operating_system: str = platform.system().lower()
    if operating_system == "windows":
        ps = WindowsPySteam()
    elif operating_system == "linux":
        ps = LinuxPySteam
    else:
        raise RuntimeError(f"Unsupported operating system [{operating_system}]")

    args = parse_argv()
    ps.upload(
        app_id=args.app_id,
        depot_id=args.depot_id,
        build_description=args.build_description,
        content_path=args.content_path,
    )


if __name__ == '__main__':
    main()
