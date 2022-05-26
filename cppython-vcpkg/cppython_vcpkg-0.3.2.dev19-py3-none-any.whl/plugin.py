"""
TODO
"""
import json
import subprocess
from os import name as system_name
from pathlib import Path, PosixPath, WindowsPath
from typing import Optional, Type

from cppython_core.schema import (
    PEP621,
    CPPythonData,
    Generator,
    GeneratorConfiguration,
    GeneratorData,
)
from cppython_core.utility import subprocess_call
from pydantic import BaseModel, Field, HttpUrl


class VcpkgData(GeneratorData):
    """
    TODO
    """

    # TODO: Make relative to CPPython:build_path
    install_path: Path = Field(
        default="build", description="The referenced dependencies defined by the local vcpkg.json manifest file"
    )

    manifest_path: Path = Field(default="", description="The directory to store the manifest file, vcpkg.json")


class VcpkgDependency(BaseModel):
    """
    Vcpkg dependency type
    """

    name: str


class Manifest(BaseModel):
    """
    The manifest schema
    """

    name: str

    # TODO: Support other version types
    version: str
    homepage: Optional[HttpUrl]
    dependencies: list[VcpkgDependency] = []


class VcpkgGenerator(Generator):
    """
    _summary_

    Arguments:
        Generator {_type_} -- _description_
    """

    def __init__(self, configuration: GeneratorConfiguration, project: PEP621, cppython: CPPythonData) -> None:
        """
        TODO
        """
        super().__init__(configuration, project, cppython)

    def _update_generator(self, path: Path):

        # TODO: Identify why Shell is needed and refactor
        try:
            if system_name == "nt":
                subprocess_call([str(WindowsPath("bootstrap-vcpkg.bat"))], cwd=path, shell=True)
            elif system_name == "posix":
                subprocess_call(["sh", str(PosixPath("bootstrap-vcpkg.sh"))], cwd=path, shell=True)
        except subprocess.CalledProcessError:
            self.logger.error("Unable to bootstrap the vcpkg repository", exc_info=True)
            raise

    def _extract_manifest(self) -> Manifest:
        """
        TODO
        """
        base_dependencies = self.cppython.dependencies

        vcpkg_dependencies = []
        for dependency in base_dependencies:
            vcpkg_dependency = VcpkgDependency(name=dependency.name)
            vcpkg_dependencies.append(vcpkg_dependency)

        # Create the manifest
        return Manifest(name=self.project.name, version=self.project.version, dependencies=vcpkg_dependencies)

    @staticmethod
    def name() -> str:
        return "vcpkg"

    @staticmethod
    def data_type() -> Type[GeneratorData]:
        return VcpkgData

    def generator_downloaded(self, path: Path) -> bool:

        try:
            # Hide output, given an error output is a logic conditional
            subprocess_call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                suppress=True,
                cwd=path,
            )

        except subprocess.CalledProcessError:
            return False

        return True

    def download_generator(self, path: Path) -> None:

        try:
            # The entire history is need for vcpkg 'baseline' information
            subprocess_call(
                ["git", "clone", "https://github.com/microsoft/vcpkg", "."],
                cwd=path,
            )

        except subprocess.CalledProcessError:
            self.logger.error("Unable to clone the vcpkg repository", exc_info=True)
            raise

        self._update_generator(path)

    def update_generator(self, path: Path) -> None:
        try:
            # The entire history is need for vcpkg 'baseline' information
            subprocess_call(["git", "fetch", "origin"], cwd=path)
            subprocess_call(["git", "pull"], cwd=path)
        except subprocess.CalledProcessError:
            self.logger.error("Unable to update the vcpkg repository", exc_info=True)
            raise

        self._update_generator(path)

    def install(self) -> Path:
        """
        TODO
        """
        manifest_path = self.cppython.vcpkg.manifest_path
        manifest = self._extract_manifest()

        # Write out the manifest
        serialized = json.loads(manifest.json())
        with open(manifest_path / "vcpkg.json", "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=4)

        vcpkg_path = self.cppython.install_path / self.name()

        executable = vcpkg_path / "vcpkg"

        try:
            subprocess_call(
                [
                    executable,
                    "install",
                    f"--x-install-root={self.cppython.vcpkg.install_path}",
                    f"--x-manifest-root={self.cppython.vcpkg.manifest_path}",
                ],
                cwd=self.cppython.build_path,
            )
        except subprocess.CalledProcessError:
            self.logger.error("Unable to install project dependencies", exc_info=True)
            raise

        return vcpkg_path / "scripts/buildsystems/vcpkg.cmake"

    def update(self) -> Path:
        """
        TODO
        """
        manifest_path = self.cppython.vcpkg.manifest_path
        manifest = self._extract_manifest()

        # Write out the manifest
        serialized = json.loads(manifest.json())
        with open(manifest_path / "vcpkg.json", "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=4)

        vcpkg_path = self.cppython.install_path / self.name()

        executable = vcpkg_path / "vcpkg"

        try:
            subprocess_call(
                [
                    executable,
                    "install",
                    f"--x-install-root={self.cppython.vcpkg.install_path}",
                    f"--x-manifest-root={self.cppython.vcpkg.manifest_path}",
                ],
                cwd=self.cppython.build_path,
            )
        except subprocess.CalledProcessError:
            self.logger.error("Unable to install project dependencies", exc_info=True)
            raise

        return vcpkg_path / "scripts/buildsystems/vcpkg.cmake"
