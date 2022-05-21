import os
import re
import shutil
from pathlib import Path
from typing import Dict, Union

from pkm.api.dependencies.dependency import Dependency
from pkm.api.environments.environment import Environment
from pkm.api.environments.environment_introspection import EnvironmentIntrospection
from pkm.api.pkm import pkm
from pkm.config.configuration import FileConfiguration
import sys

from pkm.utils.commons import NoSuchElementException

_INTERPRETER_INTROSPECTIONS: Dict[str, EnvironmentIntrospection] = {}
_PYVENV_SEP_RX = re.compile("\\s*=\\s*")


class EnvironmentBuilder:

    @staticmethod
    def create_matching(env_path: Path, interpreter: Dependency) -> Environment:
        result = Environment(env_path)

        python_versions = pkm.repositories.installed_pythons.match(interpreter, result)
        if not python_versions:
            raise NoSuchElementException("could not find installed python interpreter "
                                         f"that match the given dependency: {interpreter}")
        python_versions[0].install_to(result)
        return result

    @staticmethod
    def create(env_path: Path, interpreter_path: Path = Path(sys.executable)) -> Environment:
        interpreter_path = interpreter_path.absolute()

        if env_path.exists():
            raise FileExistsError(f"{env_path} already exists")

        ispc = _introspection_for(interpreter_path)
        sys_platform = ispc['sys.platform']
        is_windows = ispc.is_windows_env()
        sys_vinfo = ispc['sys.version_info']

        env_path.mkdir(parents=True, exist_ok=True)

        # prepare pyvenv.cfg
        pyvenvcfg = PyVEnvConfiguration.load(env_path / 'pyvenv.cfg')
        pyvenvcfg['home'] = str(interpreter_path.parent)
        pyvenvcfg['version'] = '.'.join(str(it) for it in sys_vinfo[:3])
        pyvenvcfg['include-system-site-packages'] = 'false'
        pyvenvcfg.save()

        # build relevant directories
        if is_windows:
            bin_path = env_path / 'Scripts'
            include_path = env_path / 'Include'
            site_packages_path = env_path / 'Lib' / 'site-packages'
        else:
            bin_path = env_path / 'bin'
            include_path = env_path / 'include'
            site_packages_path = env_path / 'lib' / f'python{sys_vinfo[0]}.{sys_vinfo[1]}' / 'site-packages'

        for path in (bin_path, include_path, site_packages_path):
            path.mkdir(exist_ok=True, parents=True)

        if not ispc.is_32bit_interpreter and ispc['os.name'] == 'posix' and sys_platform != 'darwin':
            (env_path / 'lib64').symlink_to(env_path / 'lib')

        # copy needed files
        if is_windows:
            file_names_to_copy = ['python.exe', 'python_d.exe', 'pythonw.exe', 'pythonw_d.exe']
            python_dir = interpreter_path.parent
            for file_name in file_names_to_copy:
                if (python_file := python_dir / file_name).exists():
                    shutil.copy(python_file, bin_path / file_name)

            if ispc['sysconfig.is_python_build']:
                # copy init.tcl
                if init_tcl := next(python_dir.rglob("**/init.tcl"), None):
                    target_init_tcl = env_path / str(init_tcl.relative_to(python_dir))
                    target_init_tcl.parent.mkdir(exist_ok=True, parents=True)
                    shutil.copy(init_tcl, target_init_tcl)
        else:
            for i in range(3):
                executable_name = f"python{'.'.join(str(it) for it in sys_vinfo[:i])}"
                executable_path = bin_path / executable_name
                if not executable_path.exists():
                    executable_path.symlink_to(interpreter_path)

        return Environment(env_path)


def _introspection_for(interpreter_path: Path) -> EnvironmentIntrospection:
    interpreter_key = str(interpreter_path.absolute())
    if (intro := _INTERPRETER_INTROSPECTIONS.get(interpreter_key)) is None:
        _INTERPRETER_INTROSPECTIONS[interpreter_key] = intro = EnvironmentIntrospection.compute(interpreter_path)

    return intro


class PyVEnvConfiguration(FileConfiguration):

    def generate_content(self) -> str:
        return os.linesep.join(f"{k} = {v}" for k, v in self._data.items())

    @classmethod
    def load(cls, path: Union[Path, str]):
        path = Path(path)

        if not path.exists():
            return PyVEnvConfiguration(path=path, data={})

        data = {(kv := _PYVENV_SEP_RX.split(line))[0]: kv[1]
                for line in path.read_text().splitlines(keepends=False)}
        return PyVEnvConfiguration(path=path, data=data)
