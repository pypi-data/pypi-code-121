# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import inspect
import sys
import types
import copy
import importlib
from pathlib import Path
from mldesigner._exceptions import (
    UserErrorException,
    ComponentDefiningError,
    NoComponentError,
    RequiredComponentNameError,
    TooManyComponentsError,
    ValidationException,
    ImportException,
)
from mldesigner._constants import NodeType
from mldesigner._utils import (
    is_mldesigner_component,
    _import_component_with_working_dir,
    _standalone_get_param_with_standard_annotation,
    is_primitive_type,
)


class ExecutorBase:
    """An executor base. Only to be inherited for sub executor classes."""

    INJECTED_FIELD = "_entity_args"  # The injected field is used to get the component spec args of the function.
    EXECUTION_PARAMETERS_KEY = "--params"
    SPECIAL_FUNC_CHECKERS = {
        "Coroutine": inspect.iscoroutinefunction,
        "Generator": inspect.isgeneratorfunction,
    }
    # This is only available on Py3.6+
    if sys.version_info.major == 3 and sys.version_info.minor > 5:
        SPECIAL_FUNC_CHECKERS["Async generator"] = inspect.isasyncgenfunction

    def __init__(self, func: types.FunctionType, entity_args=None, _entry_file=None):
        """Initialize a ComponentExecutor with a function to enable calling the function with command line args.

        :param func: A function decorated by mldesigner.command_component.
        :type func: types.FunctionType
        """
        if not isinstance(func, types.FunctionType):
            msg = "Only function type is allowed to initialize ComponentExecutor."
            raise ValidationException(message=msg)
        if entity_args is None:
            entity_args = getattr(func, self.INJECTED_FIELD, None)
            if entity_args is None:
                msg = "You must wrap the function with mldesigner component decorators before using it."
                raise ValidationException(message=msg)
        self._raw_entity_args = copy.deepcopy(entity_args)
        self._entity_args = copy.deepcopy(entity_args)
        self._name = entity_args["name"]
        self._type = entity_args.get("type", NodeType.COMMAND)
        self._entity_file_path = None
        self._assert_valid_func(func)
        if is_mldesigner_component(func):
            # If is mldesigner component func, set the func and entry file as original value
            self._func = func._executor._func
            self._entry_file = func._executor._entry_file
        else:
            # Else, set func directly, if _entry_file is None, resolve it from func.
            # Note: The entry file here might not equal with inspect.getfile(component._func),
            # as we can define raw func in file A and wrap it with mldesigner component in file B.
            # For the example below, we set entry file as B here (the mldesigner component defined in).
            self._func = func
            self._entry_file = _entry_file if _entry_file else Path(inspect.getfile(self._func)).absolute()

    def _assert_valid_func(self, func):
        """Check whether the function is valid, if it is not valid, raise."""
        for k, checker in self.SPECIAL_FUNC_CHECKERS.items():
            if checker(func):
                raise NotImplementedError("%s function is not supported for %s now." % (k, self._type))

    def __call__(self, *args, **kwargs):
        """Directly calling a component executor equals to calling the underlying function directly."""
        return self._func(*args, **kwargs)

    @classmethod
    def _collect_component_from_file(
        cls, py_file, working_dir=None, force_reload=False, component_name=None, from_executor=False
    ):
        """Collect single mldesigner component in a file and return the executors of the components."""
        py_file = Path(py_file).absolute()
        if py_file.suffix != ".py":
            msg = "{} is not a valid py file."
            raise ValidationException(message=msg.format(py_file))
        if working_dir is None:
            working_dir = py_file.parent
        working_dir = Path(working_dir).absolute()

        component_path = py_file.relative_to(working_dir).as_posix().split(".")[0].replace("/", ".")

        component = cls._collect_component_from_py_module(
            component_path,
            working_dir=working_dir,
            force_reload=force_reload,
            component_name=component_name,
            from_executor=from_executor,
        )
        if not component and from_executor:
            raise NoComponentError(py_file, component_name)
        return component

    @classmethod
    def _collect_component_from_py_module(
        cls, py_module, working_dir, force_reload=False, component_name=None, from_executor=False
    ):
        """Collect single mldesigner component in a py module and return the executors of the components."""
        components = [
            component for component in cls._collect_components_from_py_module(py_module, working_dir, force_reload)
        ]

        def defined_in_current_file(component):
            # The entry file here might not equal with inspect.getfile(component._func),
            # as we can define raw func in file A and wrap it with mldesigner component in file B.
            # For the example below, we got entry file as B here (the mldesigner component defined in).
            entry_file = component._entry_file
            component_path = py_module.replace(".", "/") + ".py"
            return Path(entry_file).resolve().absolute() == (Path(working_dir) / component_path).resolve().absolute()

        components = [
            component
            for component in components
            if defined_in_current_file(component) and (not component_name or component._name == component_name)
        ]
        if len(components) == 0:
            return None
        component = components[0]
        entry_file = Path(inspect.getfile(component._func))
        if len(components) > 1:
            if from_executor:
                if not component_name:
                    raise RequiredComponentNameError(entry_file)
                else:
                    raise TooManyComponentsError(len(components), entry_file, component_name)
            else:
                # Calls from pipeline project with no component name.
                raise TooManyComponentsError(len(components), entry_file)
        return component

    @classmethod
    def _collect_components_from_py_module(cls, py_module, working_dir=None, force_reload=False):
        """Collect all components in a python module and return the executors of the components."""
        if isinstance(py_module, str):
            try:
                py_module = _import_component_with_working_dir(py_module, working_dir, force_reload)
            except Exception as e:
                msg = """Error occurs when import component '{}': {}.\n
                Please make sure all requirements inside conda.yaml has been installed."""
                raise ImportException(message=msg.format(py_module, e)) from e
        for _, obj in inspect.getmembers(py_module):
            if cls._look_like_component(obj):
                component = cls(obj)
                component._check_py_module_valid(py_module)
                yield component

    @classmethod
    def _look_like_component(cls, f):
        """Return True if f looks like a component."""
        if not isinstance(f, types.FunctionType):
            return False
        if not hasattr(f, cls.INJECTED_FIELD):
            return False
        return True

    @classmethod
    def _get_executor_class(cls):
        try:
            from mldesigner._dependent_component_executor import DependentComponentExecutor

            return DependentComponentExecutor
        except Exception:
            return ComponentExecutor

    def _check_py_module_valid(self, py_module):
        """Check whether the entry py module is valid to make sure it could be run in AzureML."""

    def _update_func(self, func: types.FunctionType):
        # Set the injected field so the function could be used to initializing with `ComponentExecutor(func)`
        setattr(func, self.INJECTED_FIELD, self._raw_entity_args)

    def _reload_func(self):
        """Reload the function to make sure the latest code is used to generate yaml."""
        f = self._func
        module = importlib.import_module(f.__module__)
        # if f.__name__ == '__main__', reload will throw an exception
        if f.__module__ != "__main__":
            from mldesigner._utils import _force_reload_module

            _force_reload_module(module)
        func = getattr(module, f.__name__)
        self._func = func._func if is_mldesigner_component(func) else func
        self.__init__(self._func, entity_args=self._raw_entity_args, _entry_file=self._entry_file)

    def execute(self, argv):
        """Execute the component with command line arguments."""
        args = self._parse(argv)
        run = self._func(**args)
        return run


class ComponentExecutor(ExecutorBase):
    """An executor to analyze the entity args of a function and convert it to a runnable component in AzureML."""

    def __init__(self, func: types.FunctionType, entity_args=None, _entry_file=None):
        """Initialize a ComponentExecutor with a function to enable calling the function with command line args.

        :param func: A function wrapped by mldesigner.component.
        :type func: types.FunctionType
        """
        super().__init__(func=func, entity_args=entity_args, _entry_file=_entry_file)
        self._arg_mapping = self._standalone_analyze_annotations(func)

    @classmethod
    def _standalone_parse_with_mapping(cls, argv, arg_mapping):
        """Use the parameters info in arg_mapping to parse commandline params for standalone mode.

        :param argv: Command line arguments like ['--param-name', 'param-value']
        :param arg_mapping: A dict contains the mapping from param key 'param_name' to _ComponentBaseParam
        :return: params: The parsed params used for calling the user function.
        """
        parameters = dict()
        # For cases that use executor directly, params may not start with --xx
        while len(argv) > 0 and not argv[0].startswith("--"):
            argv.pop(0)
        last_key = argv[0][2:].replace("-", "_")
        for item in argv:
            if item.startswith("--"):
                cleaned_key = item[2:].replace("-", "_")
                parameters[cleaned_key] = None
                last_key = cleaned_key
            else:
                parameters[last_key] = item
        for key, data_type in arg_mapping.items():
            if key in parameters:
                try:
                    val = parameters[key]
                    if is_primitive_type(data_type):
                        val = data_type(parameters[key])
                    parameters[key] = val
                except Exception:
                    raise UserErrorException(
                        f"Parameter transition failed: {parameters[key]!r} can not be casted to type {data_type!r}"
                    )
        return parameters

    def _parse(self, argv):
        return self._standalone_parse_with_mapping(argv, self._arg_mapping)

    @classmethod
    def _standalone_analyze_annotations(cls, func):
        mapping = _standalone_get_param_with_standard_annotation(func)
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

        # Indicate the component is generated by mldesigner
        tags["codegenBy"] = "mldesigner"
        entity_args["tags"] = tags

        if "type" in entity_args and entity_args["type"] == "SweepComponent":
            return entity_args

        entity_args["environment"] = entity_args.get("environment", None)
        entity_args["distribution"] = entity_args.get("distribution", None)
        return entity_args

    @classmethod
    def _refine_environment(cls, environment, mldesigner_component_source_dir):
        return environment
