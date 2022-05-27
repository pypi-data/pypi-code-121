from importlib.metadata import metadata, version, PackageNotFoundError

from metainfo.environment.EnvironmentMetaInfo import EnvironmentMetaInfo
from metainfo.exception.PackageFileNotFoundError import PackageFileNotFoundError


class DeployedEnvironmentMetaInfo(EnvironmentMetaInfo):

    def __init__(self, package_name):
        self.package_name = package_name
        if not self.package_meta_info_exists():
            raise PackageFileNotFoundError(f'package meta info not found')

    def package_meta_info_exists(self):
        try:
            version(self.package_name)
            return True
        except PackageNotFoundError:
            return False

    def get_version(self):
        return version(self.package_name)

    def get_description(self):
        meta_info = metadata(self.package_name)
        return meta_info['Summary']
