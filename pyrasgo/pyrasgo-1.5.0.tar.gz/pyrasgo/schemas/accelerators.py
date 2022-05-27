from enum import Enum
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, Field


class AcceleratorOperationType(str, Enum):
    """
    The type of operation to create.

    OPERATION: Creates a canvas node with the given inputs
    INSIGHT: Creates an insight chart with the given inputs
    """

    OPERATION = 'OPERATION'
    INSIGHT = 'INSIGHT'


class AcceleratorOperationCreate(BaseModel):
    """
    An operation to create for an accelerator

    Attributes:
        name:
            The name of the operation. Must be a variable-safe name. Can be used
            to reference this operation in subsequent steps
        description:
            Optional description of this operation step
        transform_id:
            id of the transform to apply in creating this operation
        transform_arguments:
            Arguments to apply to the transform.
            Arguments *must* be
                - A Jinja template, parsable with Jinja syntax
                - Valid JSON. After Jinja parsing, will be loaded as python objects
                    using `json.loads()` and passed as transform arguments
            Special Argument:
                json_string_arguments:
                    The string passed in this argument will be Jinja and JSON parsed
                    like the others, then added to the transform_arguments. This allows
                    for building complex objects using Jinja (e.g. passing multiple
                    transform arguments based on one user argument)
        operation_type:
            Enum AcceleratorOperationType
            Operations of type OPERATION will be created as dataset operations
            Operations of type INSIGHT will  be created as Insight charts on the dataset
    """

    name: str
    description: Optional[str]
    transform_id: int = Field(alias='transformId')
    transform_arguments: Dict[str, Any] = Field(alias='transformArguments')
    operation_type: AcceleratorOperationType = AcceleratorOperationType.OPERATION

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class AcceleratorArgumentCreate(BaseModel):
    """
    An argument to require from users that will be passed to Accelerator operations

    Attributes:
        name:
            The name of the argument. Must be variable-safe and will be passed to operations
        description:
            Description of the argument and how to use it
        argument_type:
            The argument type, consistent with Transforms. Used by Rasgo to determine
            what input type to provide for UI forms and other special cases
            Special Type:
                dataset:
                    Arguments of type `dataset` will expect a dataset ID and will be
                    translated to FTQNs during parsing. These wll also be marked as
                    dependencies for the dataset
        optional:
            Is the argument required
        context:
            Generic data for use in displaying argument to users.
            e.g. context about which table a column argument should come from.
    """

    name: str
    description: Optional[str]
    argument_type: str = Field(alias='type')
    optional: Optional[bool] = Field(alias='optional')
    context: Optional[Dict[str, Any]]

    class Config:
        allow_population_by_field_name = True


class AcceleratorCreate(BaseModel):
    """
    The required fields for creating an Accelerator


    Attributes:
        name:
            The name of the Accelerator
        description:
            A short description of how to use the Accelerator
        arguments:
            Valid list of AcceleratorArguments
        operations:
            Valid list of AcceleratorOperations
    """

    name: str
    description: Optional[str]
    arguments: Optional[List[AcceleratorArgumentCreate]]
    operations: List[AcceleratorOperationCreate]


class Accelerator(AcceleratorCreate):
    """
    A full Accelerator definition, complete with required arguments and definitions
    for what operations an Accelerator will create
    """

    id: int


class AcceleratorApply(BaseModel):
    """
    Represents the arguments that get passed so some given Accelerator to create a Dataset

    Attributes:
        name:
            The name of the Dataset that will be created by the Accelerator
        arguments:
            A dictionary of arguments to pass to the Accelerator.
    """

    name: Optional[str]
    arguments: Dict[str, Any]
