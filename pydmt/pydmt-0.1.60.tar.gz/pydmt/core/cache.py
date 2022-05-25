import os
import pickle
import glob
from typing import Tuple, Iterable

from pydmt.utils.filesystem import copy_mkdir, makedirs_for_file
from pydmt.utils.logging import get_logger

NAME_OBJECTS = "objects"
NAME_LISTS = "lists"
FOLDER_NAME = ".pydmt"


class Cache:
    def __init__(self):
        self.name_cache = set(glob.glob(os.path.join(FOLDER_NAME,"*","*","*")))
        # self.name_cache = set(files_under_folder(FOLDER_NAME))
        logger = get_logger()
        logger.debug(self.name_cache)

    def get_list_filename(self, signature: str):
        logger = get_logger()
        logger.debug(f"get_list_filename [{signature}]")
        full_path = os.path.join(FOLDER_NAME, NAME_LISTS, signature[:2], signature[2:])
        if full_path in self.name_cache:
            logger.debug(f"return [{full_path}]")
            return full_path
        logger.debug("return None")
        return None

    def get_object_filename(self, signature: str):
        logger = get_logger()
        logger.debug(f"get_object_filename [{signature}]")
        full_path = os.path.join(FOLDER_NAME, NAME_OBJECTS, signature[:2], signature[2:])
        if full_path in self.name_cache:
            logger.debug(f"return [{full_path}]")
            return full_path
        logger.debug("return None")
        return None

    def list_sig_ok(self, signature: str):
        """
        return if a signature is indeed a list and all objects are intact
        :param signature:
        :return:
        """
        logger = get_logger()
        logger.debug(f"list_sig_ok [{signature}]")
        list_filename = self.get_list_filename(signature)
        if list_filename is None:
            logger.debug("return False")
            return False
        for _filename, sig in Cache.iterate_objects(list_filename):
            if self.get_object_filename(sig) is None:
                logger.debug(f"return False for {sig}")
                return False
        logger.debug("return True")
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
