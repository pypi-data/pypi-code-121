#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" File Input/Output Utility Methods """


import os
import io
import json
import codecs

import yaml
from yaml import Loader


class FileIO(object):
    """ File Input/Output Utility Methods """

    def temp(data: object) -> None:
        path = "c:/Users/Craig/Desktop/temp.json"

        _type = type(data)
        if _type in [dict, list]:
            FileIO.write_json(data, path)
        elif _type in [str]:
            FileIO.write_string(data, path)
        else:
            raise NotImplementedError(_type)
        raise ValueError

    @staticmethod
    def exists(file_path: str) -> bool:
        """Check if File or Directory exists

        Args:
            file_path (str): a file path

        Returns:
            bool: True if file or directory exists
        """
        return os.path.exists(file_path)

    @staticmethod
    def exists_or_error(file_path: str) -> None:
        """Raise Exception if File Path does not exist

        Args:
            file_path (str): an input path

        Raises:
            FileNotFoundError: an input path
        """
        if not FileIO.exists(file_path):
            raise FileNotFoundError(file_path)

    @staticmethod
    def exists_or_create(file_path: str) -> None:
        """Create File Path if File Path does not exist

        Args:
            file_path (str): an input path
        """
        if not FileIO.exists(file_path):
            FileIO.create_dir(file_path)

    @staticmethod
    def create_dir(dir_name: str) -> None:
        """Create Directory (recursive)

        Args:
            dir_name (str): an input path
        """
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)

    @staticmethod
    def get_file_name(file_path: str) -> str:
        """Get the File Name From the File Path

        Args:
            file_path (str): the path to the file
                example: /root/temp-file.ext

        Returns:
            str: the filename only
                example: temp-file
        """
        file_name = os.path.basename(file_path)
        return os.path.splitext(file_name)[0]

    @staticmethod
    def debug(data: object) -> None:
        """Debug Mechanism for Examining 'Stack Trace'

        Args:
            data (object): the JSON object

        Raises:
            ValueError: Stops Program Execution
        """
        file_path = os.path.join(os.environ['DESKTOP'], 'temp.json')
        FileIO.write_json(data, file_path=file_path)
        raise ValueError(f"Wrote Temp File: {file_path}")

    @staticmethod
    def write_json(data: object,
                   file_path: str) -> None:
        """Write JSON to File

        Args:
            data (object): the JSON object
            file_path (str): the absolute and qualified output file path
        """
        with io.open(file_path, "w") as json_file:
            json_dump = json.dumps(data,
                                   indent=4,
                                   sort_keys=False,
                                   ensure_ascii=True)
            json_file.write(json_dump)

    @staticmethod
    def read_json(file_path: str) -> object:
        """Read JSON from File

        Args:
            file_path (str): the absolute and qualified output file path
            file_encoding (str, optional): The output file encoding. Defaults to "utf-8".

        Returns:
            [type]: the JSON object
        """
        with open(file_path) as json_file:
            return json.load(json_file)

    @staticmethod
    def read_string(file_path: str,
                    encoding: str = "utf-8",
                    replace_newlines: bool = False) -> str:
        """Read String from File

        Args:
            file_path (str): the absolute and qualified input file path
            encoding (str, optional): the file encoding. Defaults to "utf-8".

        Returns:
            str: the file contents as a single string
        """
        with open(file_path, 'r', encoding=encoding) as myfile:
            if replace_newlines:
                return myfile.read().replace('\n', ' ')
            return myfile.read()

    @staticmethod
    def write_string(input_text: str,
                     file_path: str,
                     file_encoding: str = "utf-8") -> None:
        """Write String to File

        Args:
            input_text (str): the string contents to write to file
            file_path (str): the absolute and qualified input file path
            file_encoding (str, optional): the file encoding. Defaults to "utf-8".

        Raises:
            ValueError: Invalid Input
        """
        if not input_text or type(input_text) != str:
            raise ValueError

        target = codecs.open(file_path,
                             mode="w",
                             encoding=file_encoding)

        target.write(input_text)
        target.close()

    @staticmethod
    def write_lines(lines: list,
                    file_path: str,
                    file_encoding: str = "utf-8") -> None:
        """Write Lines to File

        Args:
            lines (list): the list to write to file
            file_path (str): the absolute and qualified input file path
            file_encoding (str, optional): the file encoding. Defaults to "utf-8".

        Raises:
            ValueError: Invalid Input
        """

        input_text = '\n'.join(lines)
        FileIO.write_string(input_text=input_text,
                            file_path=file_path,
                            file_encoding=file_encoding)

    @staticmethod
    def write_yaml(d: dict,
                   file_path: str) -> None:
        """Write YAML to File

        Args:
            d (dict): the py YAML dictionary
            file_path (str): the absolute and qualified output file path
        """
        with open(file_path, 'w') as file:
            documents = yaml.dump(d, file)

    @staticmethod
    def read_yaml(file_path: str) -> dict:
        """Read YAML from File

        Args:
            file_path (str): the absolute and qualified input file path

        Raises:
            ValueError: the file is not valid YAML

        Returns:
            dict: a py YAML dictionary
        """
        FileIO.exists_or_error(file_path)

        with open(file_path, 'r') as stream:
            try:
                return yaml.load(stream, Loader)
            except yaml.YAMLError:
                raise ValueError(f"Invalid YAML File: {file_path}")

    @staticmethod
    def read_lines(file_path: str,
                   file_encoding: str = "utf-8") -> list:
        """Read Lines of a File into a List

        Args:
            file_path (str): the absolute and qualified input file path
            file_encoding (str, optional): the file encoding. Defaults to "utf-8".

        Returns:
            list: each line in the file as a list
        """
        target = codecs.open(file_path,
                             mode="r",
                             encoding=file_encoding)
        lines = [x.replace("\n", "").strip() for x in target.readlines() if x]
        target.close()

        return lines

    @staticmethod
    def has_files(directory: str,
                  extension: str) -> bool:
        """Check if files exist in a directory by extension

        Args:
            file_path (str): the absolute and qualified directory path
            extension (str): the extendion to check for

        Returns:
            bool: True if files exist
        """
        return len(FileIO.load_files(directory, extension))

    @staticmethod
    def load_files(directory: str,
                   extension: str,
                   limit: int = None,
                   blacklist: list = None,
                   recursive: bool = False) -> list:
        """Load Files from a directory

        Args:
            directory (str): the absolute and qualified directory path
            extension (str): the file extension to load
            recursive (bool, optional): loads files recursively if set to True. Defaults to False.
            limit (int, optional): The number of files to load. Defaults to None.
            blacklist (list, optional): an list of File Names to exclude. Defaults to None.

        Returns:
            list: list of files
        """
        def non_recursive_loader() -> list:
            input_files = []

            files = os.listdir(directory)

            files = [f for f in files if f.endswith(extension)]
            if limit and len(files) >= limit:
                files = files[:limit]

            files = [os.path.normpath(os.path.join(directory, f))
                     for f in files]

            return files

        def recursive_loader() -> list:
            results = []

            for dirpath, dirnames, files in os.walk(directory):
                files = [x for x in files if x.lower().endswith(extension)]

                for name in files:

                    path = os.path.join(dirpath, name)
                    if not is_valid(path):
                        continue

                    results.append(path)
                    if limit and len(results) >= limit:
                        return results

            return results

        def load_files() -> list:
            if recursive:
                return recursive_loader()
            return non_recursive_loader()

        def is_valid(a_file: str) -> bool:
            if blacklist and len(blacklist):
                for entry in blacklist:
                    if entry in a_file:
                        return False
            return True

        return [x for x in load_files() if is_valid(x)]
