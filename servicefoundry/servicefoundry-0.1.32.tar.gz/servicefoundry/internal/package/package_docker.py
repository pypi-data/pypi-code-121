import logging
from os.path import join
from pathlib import Path

from servicefoundry.internal.io.output_callback import OutputCallBack

from ..exceptions import ConfigurationException
from ..util import create_file_from_content, manage_file_diff, read_lines_from_file
from .base_package import BasePackage

logger = logging.getLogger()


class PackageDocker(BasePackage):
    def package(self, callback: OutputCallBack):
        super().package(callback)
        docker_file_location = join(self.build_dir, self.build_pack.docker.file_name)
        if (
            Path(docker_file_location).exists() is False
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
                docker_file_location,
                self.build_pack.docker.docker_file_content,
            )
