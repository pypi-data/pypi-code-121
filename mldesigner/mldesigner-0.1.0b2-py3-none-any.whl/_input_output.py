# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This file includes the type classes which could be used in mldesigner.command_component

.. remarks::

    The following pseudo-code shows how to create a command component with such classes.

    .. code-block:: python

        @command_component(name=f"mldesigner_component_train", display_name="my-train-job")
        def train_func(
            input_param0: Input,
            input_param1: Input(type="uri_folder", path="xxx", mode="ro_mount"),
            int_param0: Input(type="integer", default=0, min=-3, max=10),
            int_param1 = 2
            str_param = 'abc',
            output_param: Output(type="uri_folder", path="xxx", mode="rw_mount"),
        ):
            pass

"""
from abc import abstractmethod, ABC
from typing import overload, Union


# TODO: merge with azure.ai.ml.entities.Input/Output
class _IOBase(ABC):
    """Define the base class of Input/Output/Parameter class."""

    def __init__(self, name=None, type=None, description=None, **kwargs):
        """Define the basic properties of io definition."""
        self.name = name
        self.type = type
        self.description = description
        # record extra kwargs and pass to azure.ai.ml.entities.Input/Output for forward compatibility
        self._kwargs = kwargs or {}
        super(_IOBase, self).__init__(**kwargs)

    @abstractmethod
    def _to_io_entity_args_dict(self):
        """Convert the Input/Output object to a kwargs dict for azure.ai.ml.entity.Input/Output."""
        pass


class Input(_IOBase):
    """Define an input of a component."""

    @overload
    def __init__(self, type: str = "uri_folder", path: str = None, mode: str = "ro_mount", description: str = None):
        """Initialize an input of a component.

        :param path: The path to which the input is pointing. Could be pointing to local data, cloud data, a registered name, etc.
        :type path: str
        :param type: The type of the data input. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param mode: The mode of the data input. Possible values are:
                            'ro_mount': Read-only mount the data,
                            'download': Download the data to the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the input
        :type description: str
        """
        pass

    @overload
    def __init__(
        self, type: str = "number", default: float = None, min: float = None, max: float = None, description: str = None
    ):
        """Initialize a number input

        :param type: The type of the data input. Can only be set to "number".
        :type type: str
        :param default: The default value of this input. When a `default` is set, input will be optional
        :type default: float
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: float
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: float
        :param description: Description of the input
        :type description: str
        """
        pass

    @overload
    def __init__(
        self, type: str = "integer", default: int = None, min: int = None, max: int = None, description: str = None
    ):
        """Initialize an integer input

        :param type: The type of the data input. Can only be set to "integer".
        :type type: str
        :param default: The default value of this input. When a `default` is set, the input will be optional
        :type default: integer
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: integer
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: integer
        :param description: Description of the input
        :type description: str
        """
        pass

    @overload
    def __init__(self, type: str = "string", default: str = None, description: str = None):
        """Initialize a string input.

        :param type: The type of the data input. Can only be set to "string".
        :type type: str
        :param default: The default value of this input. When a `default` is set, the input will be optional
        :type default: str
        :param description: Description of the input
        :type description: str
        """
        pass

    @overload
    def __init__(self, type: str = "boolean", default: bool = None, description: str = None):
        """Initialize a bool input.

        :param type: The type of the data input. Can only be set to "boolean".
        :type type: str
        :param default: The default value of this input. When a `default` is set, input will be optional
        :type default: bool
        :param description: Description of the input
        :type description: str
        """
        pass

    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: str = None,
        mode: str = "ro_mount",
        min: Union[int, float] = None,
        max: Union[int, float] = None,
        enum=None,
        description: str = None,
        **kwargs,
    ):
        """
        The actual initialization of a component input, default to be a uri_folder Input.
        The parameter combinations are defined in above @overload-decorated __init__ functions, other combinations will raise error.

        :param path: The path to which the input is pointing. Could be pointing to local data, cloud data, a registered name, etc.
        :type path: str
        :param type: The type of the data input. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', 'integer', 'number', 'string', 'boolean'
        :type type: str
        :param mode: The mode of the data input. Possible values are:
                            'ro_mount': Read-only mount the data,
                            'download': Download the data to the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: Union[integer, float]
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: Union[integer, float]
        :param description: Description of the input
        :type description: str
        """
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self.path = path
        self.mode = mode
        self.min = min
        self.max = max
        self.enum = enum
        super().__init__(name=None, type=type, description=description, **kwargs)

    def _to_io_entity_args_dict(self):
        """Convert the Input object to a kwargs dict for azure.ai.ml.entity.Input."""
        keys = ["name", "path", "type", "mode", "description", "min", "max", "enum"]
        result = {key: getattr(self, key, None) for key in keys}
        result.update(self._kwargs)
        return _remove_empty_values(result)


class Output(_IOBase):
    """Define an output of a component."""

    @overload
    def __init__(self, type="uri_folder", path=None, mode="rw_mount", description=None):
        """Define an output of a component.

        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        """
        pass

    @overload
    def __init__(self, type="uri_file", path=None, mode="rw_mount", description=None):
        """Define an output of a component.

        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        """
        pass

    def __init__(self, *, type=None, path=None, mode=None, description=None, **kwargs):
        """The actual initialization of a component output,

        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        """
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self.path = path
        self.mode = mode
        super().__init__(name=None, type=type, description=description, **kwargs)

    def _to_io_entity_args_dict(self):
        """Convert the Output object to a kwargs dict for azure.ai.ml.entity.Output."""
        keys = ["name", "path", "type", "mode", "description"]
        result = {key: getattr(self, key) for key in keys}
        result.update(self._kwargs)
        return _remove_empty_values(result)


def _remove_empty_values(data, ignore_keys=None):
    if not isinstance(data, dict):
        return data
    ignore_keys = ignore_keys or {}
    return {
        k: v if k in ignore_keys else _remove_empty_values(v)
        for k, v in data.items()
        if v is not None or k in ignore_keys
    }
