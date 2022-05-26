from collections import defaultdict
from json import load, dump
from ..DIR.DIR import DIR


class Extensions:
    def __init__(self, json_file_path, directory_for_extensions=None, extensions=None):
        """
        Loads the dir_ext_map file.
        If "directory_for_extensions" and "dir_ext_map" were specified, we save them to the json file.
        """

        self._extensions_file_path = json_file_path
        self.dir_ext_map = {}
        self.__get_existing_extensions()

        if directory_for_extensions and extensions:
            extensions = set(extensions)
            directory_for_extensions = DIR(directory_for_extensions)

            self.add_extensions(directory_for_extensions, extensions)
            self.write_json_file()

    def __get_existing_extensions(self):
        """Load dir_ext_map from json file to the extensions_file dictionary"""
        try:
            with open(self._extensions_file_path, 'r') as extensions:
                x = load(extensions)
                self.dir_ext_map = {directory: set(extension) for directory, extension in x.items()}
        except FileNotFoundError:
            pass

    def add_extensions(self, directory: DIR, extensions: set):
        """Adds the dir_ext_map to the json object without writing to the file"""
        self.dir_ext_map = defaultdict(set, self.dir_ext_map)

        for dir_key in self.dir_ext_map:
            if extensions <= self.dir_ext_map[dir_key]:
                self.dir_ext_map[dir_key] -= extensions

        self.dir_ext_map[directory.dir_path] |= extensions
        self.dir_ext_map = dict(self.dir_ext_map)

    def remove_extensions(self, extensions: set):
        extensions = set(extensions)
        dir_ = ''
        for directory, ext_set in self.dir_ext_map.items():
            if extensions < ext_set:
                self.dir_ext_map[directory] -= extensions
                dir_ = directory
                break

        if len(self.dir_ext_map[dir_]) == 0:
            print('reached here!!')
            del self.dir_ext_map[dir_]
            print(self.dir_ext_map)

    def remove_directory(self, directory: DIR):
        if self.dir_ext_map.get(directory.dir_path):
            del self.dir_ext_map[directory.dir_path]

    def write_json_file(self):
        """Writes the json object to the json __file_path"""

        # turns all the extension sets into lists since json doesn't work with sets
        extensions_list = {directory: list(extensions) for directory, extensions in self.dir_ext_map.items()}

        with open(self._extensions_file_path, 'w') as extensions:
            dump(extensions_list, extensions)
