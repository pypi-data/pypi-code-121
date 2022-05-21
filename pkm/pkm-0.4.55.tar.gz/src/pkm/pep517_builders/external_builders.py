import json
import threading
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Optional, Dict, Set, Literal, Any, List, TYPE_CHECKING

from pkm.api.dependencies.dependency import Dependency
from pkm.api.distributions.build_monitors import BuildPackageMonitoredOp, BuildPackageHookExecutionEvent
from pkm.api.packages.package import PackageDescriptor
from pkm.api.projects.pyproject_configuration import BuildSystemConfig
from pkm.utils.files import temp_dir

if TYPE_CHECKING:
    from pkm.api.environments.environment import Environment
    from pkm.api.projects.project import Project


class BuildError(IOError):

    def __init__(self, msg: str, missing_hook: bool = False) -> None:
        super().__init__(msg)
        self.missing_hook = missing_hook


_ongoing_builds: Dict[int, Set[PackageDescriptor]] = defaultdict(set)


@contextmanager
def _cycle_detection(project: "Project"):
    ongoing_builds = _ongoing_builds[threading.current_thread().ident]
    if project.descriptor in ongoing_builds:
        raise BuildError(f"cycle detected involving: {ongoing_builds}")

    ongoing_builds.add(project.descriptor)
    try:
        yield
    finally:
        ongoing_builds.remove(project.descriptor)
        if not ongoing_builds:
            del _ongoing_builds[threading.current_thread().ident]


def build_sdist(project: "Project", target_dir: Optional[Path] = None,
                target_env: Optional["Environment"] = None) -> Path:
    """
    build a source distribution from this project
    :param project: the project to build
    :param target_dir: the directory to put the created archive in
    :param target_env: the environment to build this distribution for
    :return: the path to the created archive
    """

    from pkm.api.environments.environment_builder import EnvironmentBuilder
    target_dir = target_dir or (project.directories.dist / str(project.version))
    target_env = target_env or project.attached_environment

    target_dir.mkdir(exist_ok=True, parents=True)

    dist = 'sdist'
    with BuildPackageMonitoredOp(project.descriptor, dist) as mop, temp_dir() as tdir, _cycle_detection(project):

        pyproject = project.config
        buildsys: BuildSystemConfig = pyproject.build_system
        build_packages_repo = project.attached_repository

        build_env = EnvironmentBuilder.create(tdir / 'venv', target_env.interpreter_path)

        if buildsys.requirements:
            build_env.install(buildsys.requirements, build_packages_repo)
        if buildsys.backend_path:
            build_env.install_link('build_backend', [project.path / pth for pth in buildsys.backend_path])

        # start build life-cycle:
        # 1. check for sdist extra requirements
        command = 'get_requires_for_build_sdist'
        mop.notify(BuildPackageHookExecutionEvent(project.descriptor, command))

        extra_requirements = _exec_build_cycle_script(project, build_env, buildsys, command, [None])

        if extra_requirements.status == 'success':
            if requirements := [Dependency.parse(d) for d in extra_requirements.result]:
                build_env.install(requirements, build_packages_repo)

        # 2. build the sdist
        command = 'build_sdist'
        mop.notify(BuildPackageHookExecutionEvent(project.descriptor, command))
        sdist_output = _exec_build_cycle_script(
            project, build_env, buildsys, command, [str(target_dir), None])

        if sdist_output.status == 'success':
            return target_dir / sdist_output.result
        raise BuildError("build backend did not produced expected sdist", True)


def build_wheel(project: "Project", target_dir: Optional[Path] = None, only_meta: bool = False,
                editable: bool = False, target_env: Optional["Environment"] = None) -> Path:
    """
    build a wheel distribution from this project
    :param project: the project to build
    :param target_dir: directory to put the resulted wheel in
    :param only_meta: if True, only builds the dist-info directory otherwise the whole wheel
    :param editable: if True, a wheel for editable install will be created
    :param target_env: the environment that this build should be compatible with
    :return: path to the built artifact (directory if only_meta, wheel archive otherwise)
    """

    from pkm.api.environments.environment_builder import EnvironmentBuilder
    target_dir = target_dir or (project.directories.dist / str(project.version))
    interpreter_path = target_env.interpreter_path if target_env else project.attached_environment.interpreter_path

    target_dir.mkdir(exist_ok=True, parents=True)

    dist = 'editable_wheel' if editable else 'metadata' if only_meta else 'wheel'
    with BuildPackageMonitoredOp(project.descriptor, dist) as mop, temp_dir() as tdir, _cycle_detection(project):

        pyproject = project.config
        buildsys: BuildSystemConfig = pyproject.build_system
        build_packages_repo = project.attached_repository

        build_env = EnvironmentBuilder.create(tdir / 'venv', interpreter_path)

        if buildsys.requirements:
            build_env.install(buildsys.requirements, build_packages_repo)
        if buildsys.backend_path:
            build_env.install_link('build_backend', [project.path / pth for pth in buildsys.backend_path])

        # start build life-cycle:
        # 1. check for wheel extra requirements
        command = 'get_requires_for_build_editable' \
            if editable else 'get_requires_for_build_wheel'
        mop.notify(BuildPackageHookExecutionEvent(project.descriptor, command))

        extra_requirements = _exec_build_cycle_script(project, build_env, buildsys, command, [None])

        if extra_requirements.status == 'success':
            build_env.install(
                [Dependency.parse(d) for d in extra_requirements.result],
                build_packages_repo)

        if only_meta:
            # 2. try to build metadata only
            command = 'prepare_metadata_for_build_wheel'
            mop.notify(BuildPackageHookExecutionEvent(project.descriptor, command))
            dist_info_output = _exec_build_cycle_script(
                project, build_env, buildsys, command,
                [str(target_dir), None])
            if dist_info_output.status == 'success':
                return target_dir / dist_info_output.result
            raise BuildError("build backend did not produced wheel metadata", True)

        # 3. build the wheel
        command = 'build_editable' if editable else 'build_wheel'
        mop.notify(BuildPackageHookExecutionEvent(project.descriptor, command))
        wheel_output = _exec_build_cycle_script(
            project, build_env, buildsys, command, [str(target_dir), None, None])

        if wheel_output.status == 'success':
            return target_dir / wheel_output.result
        raise BuildError("build backend did not produced expected wheel")


@dataclass
class _BuildCycleResult:
    status: Literal['success', 'undefined_hook']
    result: Any


def _exec_build_cycle_script(
        project: "Project", env: "Environment", buildsys: BuildSystemConfig, hook: str,
        arguments: List[Any]) -> _BuildCycleResult:
    with temp_dir() as tdir_path:
        build_backend_parts = buildsys.build_backend.split(":")
        build_backend_import = build_backend_parts[0]
        build_backend = 'build_backend' + (f".{build_backend_parts[1]}" if len(build_backend_parts) > 1 else "")
        output_path = tdir_path / 'output'
        output_path_str = str(output_path.absolute()).replace('\\', '\\\\')

        script = f"""
            import json

            def ret(status, result):
                out = open('{output_path_str}', 'w+')
                out.write(json.dumps({{'status': status, 'result': result}}))
                out.close()
                exit(0)

            try:
                import {build_backend_import} as build_backend
                if not hasattr({build_backend}, '{hook}'):
                    ret('undefined_hook', None)
                else:
                    result = {build_backend}.{hook}({', '.join(repr(arg) for arg in arguments)})
                    ret('success', result)
            except Exception:
                import traceback
                traceback.print_exc()
                ret('fail', traceback.format_exc())
        """

        script_path = tdir_path / 'execution.py'
        script_path.write_text(dedent(script))
        process_results = env.run_proc([str(env.interpreter_path), str(script_path)], cwd=project.path)
        if process_results.returncode != 0:
            raise BuildError(
                f"PEP517 build cycle execution failed.\n"
                f"Project: {project.name} {project.version}\n"
                f"Build backend: {build_backend}\n"
                f"Hook: {hook}\n"
                f"Resulted in exit code: {process_results.returncode}", False)

        result = _BuildCycleResult(**json.loads((tdir_path / 'output').read_text()))
        if result.status == 'fail':
            raise BuildError(
                f"PEP517 build cycle execution failed.\n"
                f"Project: {project.name} {project.version}\n"
                f"Build backend: {build_backend}\n"
                f"Hook: {hook}\n"
                f"Resulted in exception:\n{result.result}", False)
        return result
