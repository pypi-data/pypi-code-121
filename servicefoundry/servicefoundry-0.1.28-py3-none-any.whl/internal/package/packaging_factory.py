from ..exceptions import ConfigurationException
from ..model.build_pack import BuildPack
from ..output_callback import OutputCallBack
from .package_docker import PackageDocker
from .package_python import PackagePython


def package(build_dir, build_pack: BuildPack, callback: OutputCallBack):
    if build_pack.type == "python":
        package = PackagePython(build_dir, build_pack)
    elif build_pack.type == "docker":
        package = PackageDocker(build_dir, build_pack)
    else:
        raise ConfigurationException(f"{build_pack.type} not supported.")
    package.clean()
    package.pre_package(callback)
    package.package(callback)
    return package.build_path
