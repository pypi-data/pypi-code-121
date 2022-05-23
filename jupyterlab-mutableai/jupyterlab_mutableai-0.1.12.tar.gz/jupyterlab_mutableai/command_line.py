import os
from pathlib import Path
import argparse

DEFAULT_SETTINGS = """{
    // MutableAI Settings
    // jupyterlab_mutableai:settings-mutableai
    // MutableAI Settings
    // ***************************************

    // API key
    // This is the api key to call the endpoints.
    "apiKey": "insertKeyHere",

    // Autocomplete Domain
    // Used to construct url to call autocomplete endpoint
    "autocompleteDomain": "api.mutableai.com",

    // Autocomplete Flag
    // This controls whether or not autocomplete is activated.
    "flag": true,

    // Transfer Domain
    // Used to construct url to call transform endpoint
    "transformDomain": "api.mutableai.com"
}"""


def main():
    """
    This method is a CLI that gets args to
    replace the user settings file of Jupyterlab Mutable AI
    """

    home = Path.home()
    user_setting = os.path.join(
        str(home),
        ".jupyter",
        "lab",
        "user-settings",
        "jupyterlab_mutableai",
        "IMutableAI.jupyterlab-settings",
    )
    setting_file_exists = os.path.exists(user_setting)
    if not setting_file_exists:
        try:
            with open(user_setting, "w") as f:
                f.write(DEFAULT_SETTINGS)
        except:
            print("Error: could not create settings file")
            return

    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", help="Update Jupyterlab MutableAI License Key.")
    parser.add_argument(
        "--auto_complete_domain",
        help="Update Jupyterlab MutableAI Autocomplete Domain.",
    )
    parser.add_argument(
        "--transform_domain", help="Update Jupyterlab MutableAI Transform Domain."
    )
    args = parser.parse_args()

    # If the file is found the args values replaces the settings.
    file = open(user_setting, "r")
    new_file = ""
    for line in file:
        if args.api_key and '"apiKey"' in line:
            keys = line.split('"')
            new_line = line.replace(keys[3], args.api_key)
            new_file += new_line
        elif args.auto_complete_domain and '"autocompleteDomain"' in line:
            keys = line.split('"')
            new_line = line.replace(keys[3], args.auto_complete_domain)
            new_file += new_line
        elif args.transform_domain and '"transformDomain"' in line:
            keys = line.split('"')
            new_line = line.replace(keys[3], args.transform_domain)
            new_file += new_line
        else:
            new_file += line
    f = open(user_setting, "w")
    f.write(new_file)
    f.close()
