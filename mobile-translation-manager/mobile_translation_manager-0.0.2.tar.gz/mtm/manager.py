from datetime import datetime
import os
import shutil
import json
from .sheets import fetch_from_google_sheet, upload_to_google_sheet
from .android import AndroidStringFile
from munch import Munch

from .ios import iOSStringFile
from .map import StringsMap, StringsMapSchema
from .utilities import get_generic_language


DEFAULT_CONFIG_PATH = "config.json"


def get_config(config_path=DEFAULT_CONFIG_PATH):
    with open(config_path, 'r') as f:
        config_data = f.read()
    return Munch.fromDict(json.loads(config_data))


def _get_generic_languages(config, exclude_default=False):
    languages = []
    for application in config.applications:
        application_languages = application.languages
        if exclude_default:
            application_languages.remove(application.default_language)
        languages.extend(application_languages)
    languages = set(map(lambda l: get_generic_language(l), languages))
    return sorted(languages)


def _get_string_files(config):
    string_files = []
    for application in config.applications:
        platform = application.platform
        if platform == "ios":
            string_files.extend(iOSStringFile.get_string_files(application))
        elif platform == "android":
            string_files.extend(AndroidStringFile.get_string_files(application))
        else:
            raise Exception(f"{platform} is not a supported platform")
    return string_files


def populate_with_new_keys(config_path=DEFAULT_CONFIG_PATH):
    config = get_config(config_path)
    for application in config.applications:
        platform = application.platform
        if platform == "android":
            AndroidStringFile.populate_with_new_keys(application)
        elif platform == "ios":
            iOSStringFile.popuplate_with_new_keys(application)
        else:
            raise Exception(f"{platform} is not a supported platform")


def init(config_path=DEFAULT_CONFIG_PATH):
    config = get_config(config_path)
    if os.path.exists(config.string_index_filename):
        user_input = input(f"The string index file already exits: {config.string_index_filename}\nIf you continue, the file will be overwritten. Continue? [y/n]\t")
        if user_input == 'y':
            print(f"Overwritting {config.string_index_filename}")
        else:
            print("exiting")
            exit(2)

    string_files = _get_string_files(config)
    generic_languages = _get_generic_languages(config)
    map = StringsMap(string_files, generic_languages)
    map_dict = StringsMapSchema().dumps(map, indent=4, ensure_ascii=False, sort_keys=True)
    with open(config.string_index_filename, 'w') as f:
        f.write(map_dict)


def sync(config_path=DEFAULT_CONFIG_PATH):
    config = get_config(config_path)

    if not os.path.exists(config.string_index_filename):
        print("The string index file is not created yet. Please call the \"init\" function to initalize the string index.")
        exit(0)

    # create backup
    string_index_path = f"{os.getcwd()}/{config.string_index_filename}"
    shutil.copyfile(string_index_path, f"{string_index_path}.{datetime.now().strftime('%s')}.bak")

    # get current map
    with open(config.string_index_filename, 'r') as f:
        json_data = f.read()
    map = StringsMapSchema().loads(json_data)
    
    # get strings files
    string_files = _get_string_files(config)

    # update map with project values
    map.update_files(string_files)

    # update map with edited values from translator
    fetch_from_google_sheet(config.sheets_api.spreadsheet_id, map)

    # save to file
    map_dict = StringsMapSchema().dumps(map, indent=4, ensure_ascii=False, sort_keys=True)
    with open(config.string_index_filename, 'w') as f:
        f.write(map_dict)


def save(config_path=DEFAULT_CONFIG_PATH):
    config = get_config(config_path)
    # todo: figure out how to incorperate this with the save
    # need to make sure project files have the same keys as the default files
    #populate_with_new_keys(config)
    with open(config.string_index_filename, 'r') as f:
        json_data = f.read()
    map = StringsMapSchema().loads(json_data)
    string_files = _get_string_files(config)
    map.update_files(string_files)


def deploy(config_path=DEFAULT_CONFIG_PATH):
    sync(config_path)
    config = get_config(config_path)
    with open(config.string_index_filename, 'r') as f:
        json_data = f.read()
    generic_languages = _get_generic_languages(config, exclude_default=True)
    map = StringsMapSchema().loads(json_data)
    upload_to_google_sheet(config.sheets_api.spreadsheet_id, map, generic_languages)
