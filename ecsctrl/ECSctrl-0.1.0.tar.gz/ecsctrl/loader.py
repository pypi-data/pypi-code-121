import os
import logging
import json
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader, make_logging_undefined, Undefined
from jinja2.exceptions import TemplateNotFound
from jinja2.utils import open_if_exists


logger = logging.getLogger(__name__)


class EnvFileLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> Dict[str, str]:
        with open(self.file_path) as f:
            file_contents = f.read()

        lines = file_contents.splitlines()
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if not line.startswith("#")]
        lines = [line for line in lines if "=" in line]
        key_values = [line.split("=", maxsplit=2) for line in lines]
        return {k.strip(): v.strip() for k, v in key_values}


class EnvVarsParser:
    def __init__(self, env_vars) -> None:
        self.env_vars = env_vars

    def parse(self) -> Dict[str, str]:
        vars = [v.split("=", maxsplit=2) for v in self.env_vars]
        return {v[0]: v[1] for v in vars}


class JsonFileLoader:
    def __init__(self, file_path) -> None:
        self.file_path = file_path

    def load(self) -> Dict[str, str]:
        with open(self.file_path) as f:
            return json.load(f)


class SpecFileLoader:
    class JinjaLoader(FileSystemLoader):
        def split_template_path(self, template):
            # based on https://github.com/pallets/jinja/blob/ca8b0b0287e320fe1f4a74f36910ef7ae3303d99/src/jinja2/loaders.py#L19
            pieces = []
            for piece in template.split("/"):
                if piece and piece != ".":
                    pieces.append(piece)
            return pieces

        def get_source(self, environment, template):
            # based on https://github.com/pallets/jinja/blob/ca8b0b0287e320fe1f4a74f36910ef7ae3303d99/src/jinja2/loaders.py#L174
            pieces = self.split_template_path(template)
            for searchpath in self.searchpath:
                filename = os.path.join(searchpath, *pieces)
                f = open_if_exists(filename)
                if f is None:
                    continue
                try:
                    contents = f.read().decode(self.encoding)
                finally:
                    f.close()

                mtime = os.path.getmtime(filename)

                def uptodate():
                    try:
                        return os.path.getmtime(filename) == mtime
                    except OSError:
                        return False

                return contents, filename, uptodate
            raise TemplateNotFound(template)

    LoggingUndefined = make_logging_undefined(logger=logger, base=Undefined)

    def __init__(self, file_path: str, vars: Dict[str, str]):
        self.file_path = file_path
        self.vars = vars

        self.base_dir = os.path.dirname(os.path.realpath(file_path))

    def load(self) -> str:
        with open(self.file_path) as f:
            file_data = f.read()

        return self._render(file_data, self.vars)

    def _render(self, file_data: str, env: Dict[str, str]) -> str:
        jinja_env = Environment(
            loader=self.JinjaLoader(self.base_dir), undefined=self.LoggingUndefined
        )
        jinja_template = jinja_env.from_string(str(file_data))
        return jinja_template.render(env)


class VarsLoader:
    def __init__(
        self,
        env_files: List[str],
        vars: List[str],
        json_files: List[str],
        use_sys_env: bool,
    ) -> None:
        self.env_files = env_files
        self.vars = vars
        self.json_files = json_files
        self.use_sys_env = use_sys_env

    def load(self) -> Dict[str, str]:
        combined_env = {}
        for env_file in self.env_files:
            env_loader = EnvFileLoader(env_file)
            combined_env.update(env_loader.load())

        for json_file in self.json_files:
            json_loader = JsonFileLoader(json_file)
            combined_env.update(json_loader.load())

        if self.use_sys_env:
            sys_env_vars = {k: v for k, v in os.environ.items()}
            combined_env.update(sys_env_vars)

        vars_parser = EnvVarsParser(self.vars)
        parsed_vars = vars_parser.parse()
        combined_env.update(parsed_vars)

        return combined_env
