import re
import shutil
from os.path import join
from pathlib import Path

import yaml
from jsonschema.exceptions import ValidationError
from mako.template import Template

from ..const import SERVICE_DEF_FILE_NAME, TEMPLATE_DEF_FILE_NAME
from ..exceptions import ConfigurationException
from ..output_callback import OutputCallBack
from ..util import (
    create_file_from_content,
    get_file_diff,
    manage_file_diff,
    read_lines_from_file,
    read_text_from_file,
)
from .generated_definition import GeneratedDefinition
from .input_hook import InputHook
from .sf_definition import SFDefinition
from .template_parameters import get_template_parameter
from .util import (
    check_common,
    get_or_create_template_folder,
    list_dir_and_files,
    load_yaml_from_file,
    validate_schema,
)

SPEC = "spec"
OVERWRITES = "overwrites"


class Parameters(dict):
    def __init__(self, *args, **kwargs):
        super(Parameters, self).__init__(*args, **kwargs)
        self.__dict__ = self


def render(value, parameters):
    try:
        template = Template(value)
        return template.render(parameters=parameters)
    except AttributeError as e:
        raise ConfigurationException(f"Failed to parse {value}. Caused by: {e}")


class SfTemplate:
    def __init__(self, template_id, template_folder, template):
        self.template_id = template_id
        self.template_folder = template_folder
        try:
            validate_schema(template, "schema/template_schema.json")
        except ValidationError as err:
            raise ConfigurationException(f"Template validation failed. {err.message}")

        spec = template[SPEC]
        self.base_build = spec["baseBuild"]
        self.base_component = spec["baseComponent"]
        self.post_init_instruction = spec["postInitInstruction"]
        self.overwrite = spec[OVERWRITES]
        self.parameters = [
            get_template_parameter(parameter) for parameter in spec["parameters"]
        ]
        self.comments: str = spec["comments"]
        self.file_interceptor = {}

    def add_file_interceptor(self, file_name, interceptor):
        self.file_interceptor[file_name] = interceptor

    def generate_service_def(self, sf_definition: SFDefinition):
        parameters = Parameters(sf_definition.parameters)
        base_build_id = self.base_build
        base_component_id = self.base_component
        resolved_overrides = self._resolve_variables(self.overwrite, parameters)
        if sf_definition.overwrites:
            resolved_overrides.extend(
                self._resolve_variables(sf_definition.overwrites, parameters)
            )

        definition = GeneratedDefinition(
            base_build_id, base_component_id, resolved_overrides
        )
        return definition

    def list_dir_and_files(self):
        dirs, files = list_dir_and_files(self.template_folder)
        files.remove(TEMPLATE_DEF_FILE_NAME)
        files.append(SERVICE_DEF_FILE_NAME)
        return dirs, files

    def get_servicefoundry_yaml(self, parameters):
        # Write parameters into servicefoundry.yaml
        content = yaml.dump(
            {
                "template": f"truefoundry.com/v1/{self.template_id}",
                "parameters": parameters,
            },
            sort_keys=False,
        )
        content += "overwrites:\n"
        for line in self.comments.splitlines():
            content += f"#  {line}\n"
        return content

    def _get_file_content(self, file, parameters):
        if file == SERVICE_DEF_FILE_NAME:
            return self.get_servicefoundry_yaml(parameters)
        elif file in self.file_interceptor:
            old_content = read_text_from_file(join(self.template_folder, file))
            return self.file_interceptor[file](old_content)
        else:
            return read_text_from_file(join(self.template_folder, file))

    def _check_overwrite(
        self, files, parameters, out_folder, input_hook, overwrite, callback
    ):
        common_files = check_common(out_folder, files)
        overwrite_files = []
        for common_file in common_files:
            target_lines = self._get_file_content(common_file, parameters)
            source_lines = read_text_from_file(join(out_folder, common_file))
            diffs = get_file_diff(source_lines.splitlines(), target_lines.splitlines())
            if len(diffs) != 0:
                overwrite_files.append(common_file)
                callback.print_code_lines(diffs, f"{common_file} Diff", lang="diff")

        overwrite_files_str = ", ".join(overwrite_files)
        if not overwrite and len(overwrite_files) > 0:
            if not (
                input_hook
                and input_hook.ask_boolean(
                    f"We have conflicts in following files: [{overwrite_files_str}]. Do you want to overwrite them?"
                )
            ):
                raise ConfigurationException(
                    f"Can't write project. "
                    f"Conflict in files: [{overwrite_files_str}]. "
                    f"Pass `overwrite=True` to overwrite existing files."
                )
        elif len(overwrite_files) > 0:
            print(f"Going to overwrite files [{overwrite_files_str}]")

    def write(
        self,
        parameters,
        out_folder,
        input_hook: InputHook,
        overwrite=False,
        verbose=False,
        callback=OutputCallBack(),
    ):
        Path(out_folder).mkdir(parents=True, exist_ok=True)
        dirs, files = self.list_dir_and_files()
        self._check_overwrite(
            files, parameters, out_folder, input_hook, overwrite, callback
        )

        for _dir in dirs:
            Path(join(out_folder, _dir)).mkdir(parents=True, exist_ok=True)

        for file in files:
            create_file_from_content(
                join(out_folder, file), self._get_file_content(file, parameters)
            )
            if verbose:
                print(f"File created: {file}")

    def _resolve_variables(self, overwrite_dict, parameters):
        resolved_values = []
        for overwrite_key, overwrite_value in overwrite_dict.items():
            resolved_values.append(
                (
                    overwrite_key,
                    self._resolve_variable(overwrite_key, overwrite_value, parameters),
                )
            )
        return resolved_values

    def _resolve_variable(self, key, value, parameters):
        if isinstance(value, dict):
            ret_value = {}
            for k, v in value.items():
                ret_value[k] = self._resolve_variable(key, v, parameters)
            return ret_value
        if isinstance(value, list):
            ret_value = []
            for item in value:
                ret_value.append(self._resolve_variable(key, item, parameters))
            return ret_value
        if isinstance(value, (int, float)):
            return value
        # Check if it's a simple substitution
        match = re.match("^\$\{parameters\.([A-Za-z0-9]+)\}$", value)
        if match:
            variable = match.group(1)
            if variable in parameters:
                return parameters[variable]
            else:
                raise ConfigurationException(
                    f"Failed to parse {key}. Parameters doesn't have {variable}"
                )
        return render(value, parameters)

    @classmethod
    def get_template(cls, template_name):
        split = template_name.split("/")
        if len(split) != 3:
            raise ConfigurationException(f"Incorrect template {template_name}")
        template_id = split[2]
        template_folder = get_or_create_template_folder(template_id)
        template_yaml = load_yaml_from_file(f"{template_folder}/template.yaml")
        return cls(template_id, template_folder, template_yaml)
