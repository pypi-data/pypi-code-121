# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import types
import copy
import argparse
from pathlib import Path
from typing import Union

from mldesigner._component_executor import ExecutorBase
from mldesigner._exceptions import (
    UserErrorException,
    ComponentDefiningError,
    RequiredParamParsingError,
    ValidationException,
)
from mldesigner._constants import BASE_PATH_CONTEXT_KEY, DefaultEnv, ComponentSource
from mldesigner._utils import mldesigner_component_execution

try:
    from azure.ai.ml.entities._job.distribution import MpiDistribution, TensorFlowDistribution, PyTorchDistribution
    from azure.ai.ml.entities import CommandComponent, Environment
    from azure.ai.ml.entities._load_functions import load_environment
    from azure.ai.ml.entities._inputs_outputs import (
        Input,
        Output,
        _get_param_with_standard_annotation,
    )
    from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration
except ImportError:
    raise UserErrorException(
        "Dependent component executor can not be used in standalone mode. Please install auzre.ai.ml package."
    )


class DependentComponentExecutor(ExecutorBase):
    """An executor to analyze the entity args of a function and convert it to a runnable component in AzureML."""

    def __init__(self, func: types.FunctionType, entity_args=None, _entry_file=None):
        """Initialize a ComponentExecutor with a function to enable calling the function with command line args.

        :param func: A function wrapped by mldesigner.command_component.
        :type func: types.FunctionType
        """
        super().__init__(func=func, entity_args=entity_args, _entry_file=_entry_file)
        self._arg_mapping = self._analyze_annotations(func)

    @property
    def component(self):
        """
        Return the module entity instance of the component.

        Initialized by the function annotations and the meta data.
        """
        io_properties = self._generate_entity_io_properties(self._arg_mapping)
        command, args = self._entity_args["command"], io_properties.pop("args")
        # for normal command component
        entity_args = copy.copy(self._entity_args)
        entity_args["command"] = self._get_command_str_by_command_args(command, args)
        component = CommandComponent._load_from_dict(
            {**entity_args, **io_properties},
            context={BASE_PATH_CONTEXT_KEY: "./"},
            _source=ComponentSource.MLDESIGNER,
        )
        return component

    @classmethod
    def _get_command_str_by_command_args(cls, command, args):
        return " ".join(command + args)

    @property
    def _component_dict(self):
        """Return the component entity data as a python dict."""
        return self.component._to_dict()

    @classmethod
    def _parse_with_mapping(cls, argv, arg_mapping):
        """Use the parameters info in arg_mapping to parse commandline params.

        :param argv: Command line arguments like ['--param-name', 'param-value']
        :param arg_mapping: A dict contains the mapping from param key 'param_name' to _ComponentBaseParam
        :return: params: The parsed params used for calling the user function.
        """
        parser = argparse.ArgumentParser()
        for param in arg_mapping.values():
            DSLCommandLineGenerator(param).add_to_arg_parser(parser)
        args, _ = parser.parse_known_args(argv)

        # Convert the string values to real params of the function.
        params = {}
        for name, param in arg_mapping.items():
            val = getattr(args, param.name)
            generator = DSLCommandLineGenerator(param)
            if val is None:
                # Note: here param value only contains user input except default value on function
                if isinstance(param, Output) or (not param.optional and param.default is None):
                    raise RequiredParamParsingError(name=param.name, arg_string=generator.arg_string)
                continue
            # If it is a parameter, we help the user to parse the parameter,
            # if it is an input port, we use load to get the param value of the port,
            # otherwise we just pass the raw value as the param value.
            param_value = val
            if param._is_parameter_type:
                param_value = param._parse_and_validate(val)
            elif isinstance(param, Input):
                param_value = val
            params[name] = param_value
            # For OutputPath, we will create a folder for it.
            if isinstance(param, Output) and not Path(val).exists():
                Path(val).mkdir(parents=True, exist_ok=True)
        return params

    def _parse(self, argv):
        return self._parse_with_mapping(argv, self._arg_mapping)

    @classmethod
    def _generate_entity_outputs(cls, arg_mapping) -> dict:
        """Generate output ports of a component, from the return annotation and the arg annotations.

        The outputs including the return values and the special PathOutputPort in args.
        """
        return {val.name: val for val in arg_mapping.values() if isinstance(val, Output)}

    @classmethod
    def _generate_entity_inputs(cls, arg_mapping) -> dict:
        """Generate input ports of the component according to the analyzed argument mapping."""
        return {val.name: val for val in arg_mapping.values() if isinstance(val, Input)}

    @classmethod
    def _generate_entity_io_properties(cls, arg_mapping):
        """Generate the required properties for a component entity according to the annotation of a function."""
        inputs = cls._generate_entity_inputs(arg_mapping)
        outputs = cls._generate_entity_outputs(arg_mapping)
        args = []
        for val in list(inputs.values()) + list(outputs.values()):
            args.append(DSLCommandLineGenerator(val).arg_group_str())

        return {
            "inputs": {k: v._to_component_input() for k, v in inputs.items()},
            "outputs": {k: v._to_component_output() for k, v in outputs.items()},
            "args": args,
        }

    @classmethod
    def _analyze_annotations(cls, func):
        """Analyze the annotation of the function to get the parameter mapping dict and the output port list.
        :param func:
        :return: (param_mapping, output_list)
            param_mapping: The mapping from function param names to input ports/component parameters;
            output_list: The output port list analyzed from return annotations.
        """
        mapping = _get_param_with_standard_annotation(func, is_func=True)
        return mapping

    @classmethod
    def _refine_entity_args(cls, entity_args: dict) -> dict:
        # Deep copy because inner dict may be changed (environment or distribution).
        entity_args = copy.deepcopy(entity_args)
        tags = entity_args.get("tags", {})

        # Convert the type to support old style list tags.
        if isinstance(tags, list):
            tags = {tag: None for tag in tags}

        if not isinstance(tags, dict):
            raise ComponentDefiningError("Keyword 'tags' must be a dict.")

        tags["codegenBy"] = "mldesigner"
        entity_args["tags"] = tags

        if "type" in entity_args and entity_args["type"] == "SweepComponent":
            return entity_args

        core_env = entity_args.get("environment", Environment(image=DefaultEnv.IMAGE, conda_file=DefaultEnv.CONDA_FILE))
        if isinstance(core_env, Environment):
            core_env = core_env._to_dict()
        entity_args["environment"] = core_env

        distribution = entity_args.get("distribution", None)
        if distribution:
            if isinstance(distribution, (PyTorchDistribution, MpiDistribution, TensorFlowDistribution)):
                distribution_dict = distribution.as_dict()
                # Currently there is no entity class for PyTorch/Mpi/Tensorflow, need to change key name to type
                distribution_dict["type"] = distribution_dict.pop("distribution_type")
                entity_args["distribution"] = distribution_dict

        resources = entity_args.get("resources", None)
        if resources:
            if isinstance(resources, ResourceConfiguration):
                entity_args["resources"] = resources._to_rest_object().as_dict()

        return entity_args

    @classmethod
    def _refine_environment(cls, environment, mldesigner_component_source_dir):
        if cls._is_arm_versioned_str(environment):
            return environment
        environment = (
            Environment(image=DefaultEnv.IMAGE, conda_file=DefaultEnv.CONDA_FILE)
            if mldesigner_component_execution()
            else cls._refine_environment_to_obj(environment, mldesigner_component_source_dir)
        )
        return environment

    @classmethod
    def _refine_environment_to_obj(cls, environment, mldesigner_component_source_dir) -> Environment:
        if isinstance(environment, dict):
            environment = Environment(**environment)
        if isinstance(environment, (str, Path)):
            environment = Path(mldesigner_component_source_dir) / environment
            environment = load_environment(environment)
        if environment and not isinstance(environment, Environment):
            raise UserErrorException(
                f"Unexpected environment type {type(environment).__name__!r}, "
                f"expected str, path, dict or azure.ai.ml.core.Environment object."
            )
        return environment

    @classmethod
    def _is_arm_versioned_str(cls, env):
        return isinstance(env, str) and env.lower().startswith("azureml:")


class CommandLineGenerator:
    """This class is used to generate command line arguments for an input/output in a component."""

    def __init__(self, param: Union["Input", "Output"], arg_name=None, arg_string=None):
        self._param = param
        self._arg_name = arg_name
        self._arg_string = arg_string

    @property
    def param(self) -> Union["Input", "Output"]:
        """Return the bind input/output/parameter"""
        return self._param

    @property
    def arg_string(self):
        """Return the argument string of the parameter."""
        return self._arg_string

    @property
    def arg_name(self):
        """Return the argument name of the parameter."""
        return self._arg_name

    @arg_name.setter
    def arg_name(self, value):
        self._arg_name = value

    def to_cli_option_str(self, style=None):
        """Return the cli option str with style, by default return underscore style --a_b."""
        return self.arg_string.replace("_", "-") if style == "hyphen" else self.arg_string

    def arg_group_str(self):
        """Return the argument group string of the input/output/parameter."""
        s = "%s %s" % (self.arg_string, self._arg_placeholder())
        return "[%s]" % s if isinstance(self.param, Input) and self.param.optional else s

    def _arg_group(self):
        """Return the argument group item. This is used for legacy module yaml."""
        return [self.arg_string, self._arg_dict()]

    def _arg_placeholder(self) -> str:
        raise NotImplementedError()

    def _arg_dict(self) -> dict:
        raise NotImplementedError()


class DSLCommandLineGenerator(CommandLineGenerator):
    """This class is used to generate command line arguments for an input/output in a mldesigner.command_component."""

    @property
    def arg_string(self):
        """Compute the cli option str according to its name, used in argparser."""
        return "--" + self.param.name

    def add_to_arg_parser(self, parser: argparse.ArgumentParser, default=None):
        """Add this parameter to ArgumentParser, both command line styles are added."""
        cli_str_underscore = self.to_cli_option_str(style="underscore")
        cli_str_hyphen = self.to_cli_option_str(style="hyphen")
        if default is not None:
            return parser.add_argument(cli_str_underscore, cli_str_hyphen, default=default)
        else:
            return parser.add_argument(
                cli_str_underscore,
                cli_str_hyphen,
            )

    def _update_name(self, name: str):
        """Update the name of the port/param.

        Initially the names of inputs should be None, then we use variable names of python function to update it.
        """
        if self.param.name is not None:
            msg = "Cannot set name to {} since it is not None, the value is {}."
            raise ValidationException(message=msg.format(name, self.name))
        if not name.isidentifier():
            raise ComponentDefiningError("The name must be a valid variable name, got '%s'." % name)
        self.param.name = name

    def _arg_placeholder(self) -> str:
        io_tag = "outputs" if isinstance(self.param, Output) else "inputs"
        return "${{%s.%s}}" % (io_tag, self.param.name)
