# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import inspect
import functools
import types
from typing import Union
from pathlib import Path
from typing import TypeVar, Callable, Any
from os import PathLike

from mldesigner._component_executor import ExecutorBase, ComponentExecutor
from mldesigner._exceptions import (
    UserErrorException,
    ComponentDefiningError,
)
from mldesigner._utils import (
    is_valid_name,
    _resolve_source_directory,
    _resolve_source_file,
    _relative_to,
)


# hint vscode intellisense
_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])
SPEC_EXT = ".spec.yaml"


def command_component(
    *,
    name=None,
    version="1",
    display_name=None,
    description=None,
    is_deterministic=None,
    tags=None,
    environment: Union[str, dict, PathLike, "Environment"] = None,
    distribution: Union[dict, "PyTorchDistribution", "MpiDistribution", "TensorFlowDistribution"] = None,
    resources: Union[dict, "ResourceConfiguration"] = None,
    code: Union[str, PathLike] = None,
):
    """Return a decorator which is used to declare a component with @command_component.

    A component is a reusable unit in an Azure Machine Learning workspace.
    With the decorator @command_component, a function could be registered as a component in the workspace.
    Then the component could be used to construct an Azure Machine Learning pipeline.

    .. remarks::

        The following example shows how to use @command_component to declare a simple component.

        .. code-block:: python

            @command_component()
            def your_component_function(output:Output(), input: Input(), param='str_param'):
                pass

        The following example shows how to declare a component with detailed meta data.

        .. code-block:: python

            @command_component(name=name, version=version, description=description)
            def your_component_function(output: Output(), input: Input(), param='str_param'):
                pass

        The following example shows how to consume the declared component function with dsl.pipeline.

        .. code-block:: python

            from azure.ai.ml import MLClient
            from azure.ai.ml.dsl import pipeline

            # define pipeline with mldesigner.command_component function
            @pipeline()
            def your_pipeline_func(input, param):
                your_component_function(input=input, param=param)

            # create the pipeline
            pipeline = your_pipeline_func(your_input, 'your_str')

            # Submit pipeline through MLClient

            ml_client = MLClient(cred, "my-sub", "my-rg", "my-ws")
            ml_client.create_or_update(pipeline)


    :param name: The name of the component. If None is set, function name is used.
    :type name: str
    :param version: Version of the component.
    :type version: str
    :param display_name: Display name of the component.
    :type display_name: str
    :param description: The description of the component. If None is set, the doc string is used.
    :type description: str
    :param is_deterministic: Specify whether the component will always generate the same result. The default value is
                             None, the component will be reused by default behavior, the same for True value. If
                             False, this component will never be reused.
    :type is_deterministic: bool
    :param tags: Tags of the component.
    :type tags: dict
    :param environment: Environment config of component, could be a yaml file path, a dict or an Environment object.
                        If None, a default conda with 'azure-ai-ml' will be used.
    :type environment: Union[str, os.PathLike, dict, azure.ai.ml.entities.Environment]
    :param distribution: The distribution config of component, e.g. distribution={'type': 'mpi'}.
    :type distribution: Union[dict, PyTorchDistribution, MpiDistribution, TensorFlowDistribution]
    :param resources: Compute Resource configuration for the component.
    :type resources: Union[dict, ResourceConfiguration]
    :param code: The source directory of component, with default value '.'.
                 i.e. The directory of mldesigner component file.
    :type code: Union[str, PathLike]
    :return: The decorated function which could be used to create component directly.
    """
    if name and not is_valid_name(name):
        msg = "Name is not valid, it could only contains a-z, A-Z, 0-9 and '.-_', got '%s'." % name
        raise ComponentDefiningError(msg)

    # Get the directory of decorator to resolve absolute code path in environment
    # Note: The decorator defined source directory may be different from mldesigner component source directory.
    decorator_defined_source_dir = _resolve_source_directory()
    # If is in mldesigner component execution process, skip resolve file path.
    EXECUTOR_CLASS = ExecutorBase._get_executor_class()
    environment = EXECUTOR_CLASS._refine_environment(environment, decorator_defined_source_dir)
    if code:
        # Resolve code source immediately if defined with code.
        code = Path(decorator_defined_source_dir / code).resolve().absolute().as_posix()

    entity_args = {
        k: v for k, v in locals().items() if v is not None and k in inspect.signature(command_component).parameters
    }

    def component_func_decorator(func: _TFunc) -> _TFunc:
        if not isinstance(func, Callable):
            raise UserErrorException(f"Dsl component decorator accept only function type, got {type(func)}.")

        nonlocal entity_args
        entity_args = EXECUTOR_CLASS._refine_entity_args(entity_args)

        entity_args["name"] = entity_args.get("name", func.__name__)
        entity_args["display_name"] = entity_args.get("display_name", entity_args["name"])
        entity_args["description"] = entity_args.get("description", func.__doc__)
        # pop description if not set, otherwise it's None value and will raise error when load schema
        if entity_args["description"] is None:
            entity_args.pop("description")
        func_entry_path = _resolve_source_file()
        if not func_entry_path:
            func_entry_path = Path(inspect.getfile(func)).resolve().absolute()
        # Fall back to func entry directory if not specified.
        entity_args["code"] = entity_args.pop("code") if code else Path(func_entry_path).parent.absolute().as_posix()

        # Set entry name as relative path to code
        entry_relative_path = _relative_to(func_entry_path, entity_args["code"])
        if not entry_relative_path:
            raise UserErrorException(
                f"Dsl component {entity_args['name']!r} source directory {func_entry_path!r} "
                f"not under code directory {entity_args['code']!r}"
            )
        entry_relative_path = entry_relative_path.as_posix()
        entity_args["command"] = [
            "python",
            "-m",
            "mldesigner.executor",
            "--file",
            str(entry_relative_path),
            "--name",
            entity_args["name"],
            "--params",
        ]
        # Initialize a ComponentExecutor to make sure it works and use it to update the component function.
        # Save the raw func as we will wrap it
        raw_func = _copy_func(func)

        executor = EXECUTOR_CLASS(func=raw_func, entity_args=entity_args, _entry_file=func_entry_path)
        executor._update_func(raw_func)

        def standalone_warning(*args, **kwargs):
            raise UserErrorException(
                "Function that is decorated by command component can not be called in standalone mode. Please install auzre.ai.ml to call this function to generate a pipeline node."
            )

        _component_func = None
        # if EXECUTOR_CLASS is DependentComponentExecutor
        if EXECUTOR_CLASS != ComponentExecutor:
            from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function

        @functools.wraps(raw_func)
        def wrapper(*args, **kwargs):
            nonlocal _component_func
            if not _component_func:
                _component_func = (
                    standalone_warning
                    if EXECUTOR_CLASS == ComponentExecutor
                    else _generate_component_function(executor.component)
                )
            return _component_func(*args, **kwargs)

        wrapper._is_mldesigner_component = True
        wrapper._executor = executor
        if EXECUTOR_CLASS != ComponentExecutor:
            wrapper.component = executor.component
        return wrapper

    return component_func_decorator


def _copy_func(f):
    """Copy func without deep copy as some method may contains fields can not be copied."""
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__, argdefs=f.__defaults__, closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g
