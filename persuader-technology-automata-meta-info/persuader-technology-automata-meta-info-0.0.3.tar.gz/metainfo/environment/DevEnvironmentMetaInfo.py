import os

from metainfo.environment.EnvironmentMetaInfo import EnvironmentMetaInfo
from metainfo.exception.PackageFileNotFoundError import PackageFileNotFoundError


class DevEnvironmentMetaInfo(EnvironmentMetaInfo):

    def __init__(self, default_path='..', setup_file='setup.cfg'):
        self.setup_file_path = os.path.join(os.getcwd(), default_path, setup_file)
        if not self.setup_file_exists():
            raise PackageFileNotFoundError(f'{setup_file} is not found')

    def setup_file_exists(self):
        return os.path.exists(self.setup_file_path)

    def get_version(self):
        return self.obtain_value_from_setup('version')

    def get_description(self):
        return self.obtain_value_from_setup('description')

    def obtain_value_from_setup(self, key):
        file_contents = self.read_from_setup_file()
        value_of_key = [line for line in file_contents if line.find(key) >= 0]
        normalized_value = value_of_key[0].replace('\n', '').replace(f'{key} = ', '')
        return normalized_value

    def read_from_setup_file(self):
        with open(self.setup_file_path, 'r') as data_file:
            return data_file.readlines()
