import logging
from pathlib import Path

from ..exceptions import ConfigurationException
from ..output_callback import OutputCallBack
from ..util import create_file_from_content, manage_file_diff, read_lines_from_file
from .base_package import BasePackage

logger = logging.getLogger()


class PackageDocker(BasePackage):
    def package(self, callback: OutputCallBack):
        if (
            Path(self.build_pack.docker.file_name).exists() is False
            or self.build_pack.docker.overwrite
        ):
            if Path(self.build_pack.docker.file_name).is_dir():
                raise ConfigurationException(
                    f"Can't overwrite Dockerfile. "
                    f"Since {self.build_pack.docker.file_name} is a directory."
                )
            source_lines = []
            if Path(self.build_pack.docker.file_name).is_file():
                source_lines = read_lines_from_file(self.build_pack.docker.file_name)

            target_lines = self.build_pack.docker.docker_file_content.splitlines()
            manage_file_diff(
                source_lines, target_lines, self.build_pack.docker.file_name, callback
            )
            create_file_from_content(
                self.build_pack.docker.file_name,
                self.build_pack.docker.docker_file_content,
            )
        super().package(callback)
