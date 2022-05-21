import zipfile
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from pkm.api.distributions.wheel_distribution import WheelDistribution
from pkm.api.environments.environment import Environment
from pkm.api.environments.environment_builder import EnvironmentBuilder
from pkm.api.projects.project import Project
from pkm.utils.commons import UnsupportedOperationException
from pkm.utils.files import temp_dir

CONTAINERIZED_APP_SITE_PATH = "__packages__"
CONTAINERIZED_APP_BIN_PATH = "__bin__"
CONTAINERIZED_APP_DATA_PATH = "__data__"


def build_wheel(project: "Project", target_dir: Optional[Path] = None,
                editable: bool = False,
                target_env: Optional[Environment] = None) -> Path:
    """
    build a wheel distribution from this project
    :param project: the project to build
    :param target_dir: directory to put the resulted wheel in
    :param editable: if True, a wheel for editable install will be created
    :param target_env: the environment that this build should be compatible with, defaults to the project's attached env
    :return: path to the built artifact (directory if only_meta, wheel archive otherwise)
    """

    target_dir = target_dir or (project.directories.dist / str(project.version))
    interpreter_path = target_env.interpreter_path if target_env else project.attached_environment.interpreter_path

    if not (app_config := project.config.pkm_application) or not app_config.containerized:
        raise UnsupportedOperationException("not application or non containerized")

    with temp_dir() as tdir:
        tenv = EnvironmentBuilder.create(tdir / "env", interpreter_path)
        target = tenv.installation_target

        target.app_containers.install(project, editable=editable)

        # build the actual wheel
        wheel_path = target_dir / WheelDistribution.expected_wheel_file_name(project)
        target_dir.mkdir(parents=True, exist_ok=True)
        with ZipFile(wheel_path, 'w', compression=zipfile.ZIP_DEFLATED) as wheel:
            build_dir = Path(target.purelib)
            for file in build_dir.rglob('*'):
                wheel.write(file, file.relative_to(build_dir))

        return wheel_path
