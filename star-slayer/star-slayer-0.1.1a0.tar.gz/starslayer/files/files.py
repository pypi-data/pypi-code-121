"""
Files Module. It reads (and writes) in files to define persistent
variables in the behaviour of the game.
"""


from json import dump, load
from os import listdir
from os.path import isfile
from os.path import join as path_join
from os.path import splitext
from typing import List, Optional

from ..consts import DEFAULT_THEME

StrDict = dict[str, str]
ProfilesDict = dict[str, StrDict]

GameDict = StrDict | ProfilesDict


def load_json(file_name: str) -> GameDict:
    """
    Loads a JSON file into a python dictionary.
    """

    dict_to_return = {}

    with open(file_name, mode='r', encoding="utf-8") as file:

        dict_to_return = load(file)

    return dict_to_return


def dump_json(dump_dict: GameDict, file_name: str) -> None:
    """
    Dumps a python dictionary into a JSON file.
    """

    with open(file_name, mode='w', encoding="utf-8") as file:

        dump(dump_dict, file, indent=4)


def list_actions(keys_dict: StrDict) -> List[str]:
    """
    Returns a list of all the actions in the keys file, without repetitions.
    """

    actions_list = []

    for action in keys_dict.values():

        if not action in actions_list:

            actions_list.append(action)

    return actions_list


def list_repeated_keys(value: str, keys_dict: StrDict) -> List[str]:
    """
    Given a value to search for and a dictionary (by default the one that 'map_keys' returns),
    it returns a list of all the keys that have such value.
    """

    return [key for (key, val) in keys_dict.items() if val == value]


def list_profiles(profiles_dict: ProfilesDict) -> List[str]:
    """
    Returns a list of all the available color profiles titles.
    """

    return [profile for profile in profiles_dict if not profile == DEFAULT_THEME]


def list_attributes(profile_dict: StrDict) -> List[str]:
    """
    Returns a list of all of the attributes of a given color profile.
    """

    return list(profile_dict)


def check_ext(path: str, ext: str) -> bool:
    """
    Checks if a file or path file end with a certain extension.
    """

    return splitext(path)[1][1:].lower() == ext.lower()


def count_files(dir_path: str, preferred_ext: Optional[str]=None) -> List[str]:
    """
    Counts all the files that are in a directory path.

    Also, if `preferred_ext` is set, it checks if they have such extension.
    """

    files = []

    for elem in listdir(dir_path):
        fpath = path_join(dir_path, elem)
        if isfile(fpath) and (check_ext(fpath, preferred_ext) if preferred_ext else True):
            files.append(elem)

    return files
