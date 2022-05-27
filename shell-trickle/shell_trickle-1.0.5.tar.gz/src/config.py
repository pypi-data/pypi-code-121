from pathlib import Path
from configparser import ConfigParser


config_path = Path.joinpath(Path.home(), ".shell_trickle.ini")
if not Path.exists(config_path):
    open(config_path, "a").close()


def set_config(endpoint: str, app_member_token: str):
    lines = [
        "[DEFAULT]\n",
        f"endpoint = {endpoint}\n",
        f"token = {app_member_token}\n"
    ]
    with open(config_path, "w") as f:
        f.writelines(lines)


config_parser = ConfigParser()
def get_config():
    if not Path.exists(config_path):
        print("please set config first...")
        return None

    config_parser.read(config_path)
    return config_parser.defaults()
