import os

from servicefoundry.internal.io.output_callback import OutputCallBack
from servicefoundry.internal.parser.parser import parse

from ..const import BUILD_DIR, SERVICE_DEF_FILE_NAME
from ..exceptions import ConfigurationException
from ..packaged_component import PackagedComponent
from ..template.generated_definition import GeneratedDefinition
from .package_docker import PackageDocker
from .package_python import PackagePython


def _parse(service_def):
    if isinstance(service_def, GeneratedDefinition):
        return service_def

    if not os.path.isfile(service_def):
        raise ConfigurationException(
            f"Service definition {service_def} doesn't exist in directory {os.path.abspath(service_def)}."
        )

    service_def = parse(service_def)
    return service_def


class Package:
    def __init__(self, service_def, build_dir):
        self.build_dir = build_dir
        self.generated_service_def = _parse(service_def)

        build_pack = self.generated_service_def.get_build_pack()
        if build_pack.type == "python":
            self._package = PackagePython(self.build_dir, build_pack)
        elif build_pack.type == "docker":
            self._package = PackageDocker(self.build_dir, build_pack)
        else:
            raise ConfigurationException(f"{build_pack.type} not supported.")

    def clean(self, callback: OutputCallBack):
        callback.print_header("Clean")
        self._package.clean(callback=callback)

    def pre_package(self, callback: OutputCallBack):
        callback.print_header("Pre Packaging")
        self._package.pre_package(callback)
        self.generated_service_def.write(dir=self.build_dir)

    def package(self, callback: OutputCallBack):
        callback.print_header("Packaging")
        return self._package.package(callback)


def package(
    service_def_file_name=SERVICE_DEF_FILE_NAME,
    build_dir=BUILD_DIR,
    callback=OutputCallBack(),
):
    _package = Package(service_def_file_name, build_dir)
    _package.clean(callback=callback)
    _package.pre_package(callback=callback)
    _package.package(callback=callback)
    return PackagedComponent(
        build_dir=_package.build_dir, service_def=_package.generated_service_def
    )
