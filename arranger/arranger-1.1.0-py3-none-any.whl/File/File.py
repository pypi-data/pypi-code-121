from json import load
from os import rename as mv
from ..DIR.DIR import DIR


class File:
    def __init__(self, file_path, json_file_path):
        self.file_path = file_path
        self.__file_name = self.file_path.split('/')[-1]
        self.__file_extension = self.file_path.split('.')[-1]
        self.__json_file = json_file_path
        self.__destination = ''

    def main(self):
        self.__get_file_destination()

        if self.__destination != '':
            self.__move_file_to_destination()

    def __get_directory_to_extensions_dict(self):
        """Gets the directory --> extensions dictionary from the json file"""
        with open(self.__json_file, 'r') as extensions:
            dir_ext = load(extensions)

        return dir_ext

    def __get_file_destination(self):
        """Finds the directory to where the file would go."""
        dir_ext = self.__get_directory_to_extensions_dict()

        for directory, extensions in dir_ext.items():
            if self.__file_extension in extensions:
                self.__destination = directory
                break

    def __move_file_to_destination(self):
        """moves the given file to the destination."""
        try:
            mv(self.file_path, f'{self.__destination}/{self.__file_name}')
        except FileNotFoundError:
            directory = DIR(self.__destination)
            directory.create_directory()
            mv(self.file_path, f'{self.__destination}/{self.__file_name}')
