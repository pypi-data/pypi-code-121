import os
import pickle
from typing import Tuple, Iterable

from pydmt.utils.filesystem import copy_mkdir, makedirs_for_file, files_under_folder

NAME_OBJECTS = "objects"
NAME_LISTS = "lists"
FOLDER_NAME = ".pydmt"


class Cache:
    def __init__(self):
        self.name_cache = set(files_under_folder(FOLDER_NAME))

    def get_list_filename(self, signature: str):
        full_path = os.path.join(FOLDER_NAME, NAME_LISTS, signature[:2], signature[2:])
        if full_path in self.name_cache:
            return full_path
        return None

    def get_object_filename(self, signature: str):
        full_path = os.path.join(FOLDER_NAME, NAME_OBJECTS, signature[:2], signature[2:])
        if full_path in self.name_cache:
            return full_path
        return None

    def list_sig_ok(self, signature: str):
        """
        return if a signature is indeed a list and all objects are intact
        :param signature:
        :return:
        """
        list_filename = self.get_list_filename(signature)
        if list_filename not in self.name_cache:
            return False
        for _filename, sig in Cache.iterate_objects(list_filename):
            if self.get_object_filename(sig) is None:
                return False
        return True

    def save_list_by_signature(self, signature: str, d: dict):
        full_path = os.path.join(FOLDER_NAME, NAME_LISTS, signature[:2], signature[2:])
        makedirs_for_file(full_path)
        with open(full_path, "wb") as file_handle:
            pickle.dump(d, file_handle)
        self.name_cache.add(full_path)

    def save_object_by_signature(self, signature: str, file_name: str):
        full_path = os.path.join(FOLDER_NAME, NAME_OBJECTS, signature[:2], signature[2:])
        copy_mkdir(file_name, full_path)
        self.name_cache.add(full_path)

    @staticmethod
    def iterate_objects(file_name: str) -> Iterable[Tuple[str, str]]:
        with open(file_name, "rb") as file_handle:
            yield from pickle.load(file_handle).items()
