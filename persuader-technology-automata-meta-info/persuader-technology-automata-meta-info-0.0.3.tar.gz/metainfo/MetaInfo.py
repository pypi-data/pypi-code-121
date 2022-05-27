from metainfo.environment.DeployedEnvironmentMetaInfo import DeployedEnvironmentMetaInfo
from metainfo.environment.DevEnvironmentMetaInfo import DevEnvironmentMetaInfo
from metainfo.environment.EnvironmentMetaInfo import EnvironmentMetaInfo
from metainfo.exception.PackageFileNotFoundError import PackageFileNotFoundError


class MetaInfo:

    def __init__(self, package_name, default_setup_path='..'):
        self.package_name = package_name
        self.default_setup_path = default_setup_path
        self.meta_info = self.init_environment_meta_info()

    def init_environment_meta_info(self) -> EnvironmentMetaInfo:
        try:
            return DeployedEnvironmentMetaInfo(self.package_name)
        except PackageFileNotFoundError:
            return DevEnvironmentMetaInfo(default_path=self.default_setup_path)

    def get_version(self):
        return self.meta_info.get_version()

    def get_description(self):
        return self.meta_info.get_description()
