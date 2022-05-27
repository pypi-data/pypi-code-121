from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING
import re

import yaml

from pyrasgo import errors
from pyrasgo.schemas.transform import Transform

if TYPE_CHECKING:
    from pyrasgo.primitives.dataset import Dataset


def replace_source_variable_args(
    operation_args: Dict[str, any],
    used_transform: Transform,
    top_source_table_arguments: List[str],
    fqtn_to_arg_names: Dict[str, any],
) -> Tuple[any, List[any], Dict[str, str]]:
    """
    Replace source table and operation FQTNs with variable names
    """

    def replace_table_arg(
        value: str, fqtn_to_arg_names: Dict[str, str], top_source_table_arguments: List[any]
    ) -> Tuple[Dict[str, str], List[any], str]:
        """
        If this argument has a mapping to a previous operation or table we already know we need, replace the value
        with that argument name. Otherwise add a new source_table argument for it.

        returns:
            - updated fqtn mapping
            - updated top level source args
            - the replaced name of the source arg
        """
        if str(value) in fqtn_to_arg_names:
            return fqtn_to_arg_names, top_source_table_arguments, f"{{{{{fqtn_to_arg_names[value]}}}}}"

        table_arg_name = f'source_table{"_"+str(len(top_source_table_arguments)) if top_source_table_arguments else ""}'
        argument_create = {
            "name": table_arg_name,
            "description": 'A source table argument that must be passed to this Accelerator',
            "argument_type": 'dataset',
        }

        fqtn_to_arg_names[value] = table_arg_name
        top_source_table_arguments.append(argument_create)
        return fqtn_to_arg_names, top_source_table_arguments, f"{{{{{table_arg_name}}}}}"

    transform_args = {}
    for arg, value in operation_args.items():
        arg_type = next(iter([x.type for x in used_transform.arguments if x.name == arg]), None)

        if arg == 'source_table' or arg_type == 'table':
            fqtn_to_arg_names, top_source_table_arguments, replaced_value = replace_table_arg(
                value, fqtn_to_arg_names, top_source_table_arguments
            )
            transform_args[arg] = replaced_value
        elif arg_type == 'table_list' and isinstance(value, List):
            val_list = []
            for table_arg in value:
                fqtn_to_arg_names, top_source_table_arguments, replaced_value = replace_table_arg(
                    table_arg, fqtn_to_arg_names, top_source_table_arguments
                )
                val_list.append(replaced_value)
            transform_args[arg] = val_list
        else:
            transform_args[arg] = value

    return (
        {
            'transform_name': used_transform.name,
            'transform_arguments': transform_args,
        },
        top_source_table_arguments,
        fqtn_to_arg_names,
    )


def escape_name(name: str) -> str:
    """
    Remove non-alphanumerics, replace spaces with '_' and lowercase everything to get valid python var name
    """
    escaped = re.sub(r'[^a-zA-Z0-9_]', '', name).replace(' ', '_').lower()
    return f'_{escaped}' if escaped and escaped[0].isnumeric() else escaped  # leading digits bad


def dataset_to_accelerator_yaml(dataset: Dataset) -> str:

    from pyrasgo.api.get import Get

    get = Get()

    top_source_table_arguments = []
    accelerator_operations = {}
    used_transforms = {x.id: x for x in dataset._available_transforms}
    fqtn_to_arg_names = {}

    # Operations
    for operation in dataset._api_operation_set.operations:

        # get the transform def, fetch it if we haven't already got it from the list we inherited from the dataset.
        # It could be deleted and that's okay, we really just need the name.
        used_transforms[operation.transform_id] = used_transforms.get(
            operation.transform_id, get.transform(operation.transform_id)
        )
        used_transform = used_transforms.get(operation.transform_id)
        if not used_transform:
            raise errors.RasgoResourceException(
                f"Transform {operation.transform_id} referenced in {operation.operation_name} is not available"
            )

        (
            accelerator_operations[escape_name(operation.operation_name)],
            top_source_table_arguments,
            fqtn_to_arg_names,
        ) = replace_source_variable_args(
            operation.operation_args, used_transform, top_source_table_arguments, fqtn_to_arg_names
        )
        fqtn_to_arg_names[operation.dw_table.fqtn] = escape_name(operation.operation_name)

    # Insights
    for insight in dataset._api_dataset.insights:
        used_transforms[insight.transform_id] = used_transforms.get(
            insight.transform_id, get.transform(insight.transform_id)
        )
        used_transform = used_transforms.get(insight.transform_id)
        if not used_transform:
            raise errors.RasgoResourceException(
                f"Transform {insight.transform_id} referenced in {insight.name} is not available"
            )

        parsed, top_source_table_arguments, fqtn_to_arg_names = replace_source_variable_args(
            insight.transform_arguments, used_transform, top_source_table_arguments, fqtn_to_arg_names
        )
        accelerator_operations[escape_name(insight.name)] = {'operation_type': 'INSIGHT', **parsed}

    final_args = {x.pop('name'): x for x in top_source_table_arguments}
    accelerator_dict = {
        'name': f"{dataset.name} Accelerator",
        'description': f"Accelerator template created from Dataset {dataset.id}",
        'arguments': final_args,
        'operations': accelerator_operations,
    }

    # Doc section
    # Uses the output table of the dataset to build a default doc section
    output_operation = next(
        iter([x for x in dataset._api_operation_set.operations if x.dw_table_id == dataset._api_dataset.dw_table_id]),
        None,
    )
    if output_operation:
        accelerator_dict['doc'] = {
            'output_tables': {
                escape_name(output_operation.operation_name): {
                    x.column_name: {'description': f'{x.column_name}:{x.data_type}'}
                    for x in output_operation.dw_table.columns
                }
            }
        }

    return yaml.safe_dump(accelerator_dict, sort_keys=False)
