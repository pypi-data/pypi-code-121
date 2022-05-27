import json
import os
import re
from collections import ChainMap
from collections import OrderedDict

import yaml


def convert_tf_file_to_sls(
    hub,
    root,
    tf_file,
    filtered_sls_data,
    tfvars_data,
    tf_reseource_type_name_and_resource_map,
    output_sls_path,
):
    idem_resource_type_resource_id_separator = (
        hub.tf_idem_auto.utils.idem_resource_type_resource_id_separator
    )
    tf_idem_resource_type_map = hub.tf_idem_auto.utils.tf_idem_resource_type_map
    # TODO : Remove this check when target/input folder is no more required
    if tf_file.endswith(".txt"):
        return None, None, None
    input_tf_file_path = root
    output_sls_file_path = f"{output_sls_path}/sls/{tf_file.replace('.tf', '.sls')}"
    hub.log.info("input : '%s'", input_tf_file_path)
    converted_sls_data = OrderedDict()
    idem_resource_id_map = OrderedDict()
    security_group_ids = []
    variables = OrderedDict()
    idem_resource_id_tf_resource_map = OrderedDict()
    obj = hub.tf_idem_auto.utils.parse_tf_data(input_tf_file_path)
    if "resource" in obj:
        resources = obj.get("resource")
        for tf_resource in resources:
            tf_resource_type = list(tf_resource.keys())[0]
            tf_resource_name = list(tf_resource[tf_resource_type].keys())[0]

            tf_resource_identifier = f"{tf_resource_type}__{tf_resource_name}"
            if tf_resource_identifier not in tf_reseource_type_name_and_resource_map:
                continue
            tf_state_for_resource_under_processing = (
                tf_reseource_type_name_and_resource_map[tf_resource_identifier]
            )

            if tf_state_for_resource_under_processing:
                resource_index = 0
                for instance in tf_state_for_resource_under_processing["instances"]:
                    attributes = instance["attributes"]
                    if tf_resource_type == "aws_security_group":
                        security_group_ids.append(attributes["id"])
                    tf_uuid = (
                        "id"
                        if tf_resource_type
                        not in hub.tf_idem_auto.utils.tf_resource_type_uuid
                        else hub.tf_idem_auto.utils.tf_resource_type_uuid[
                            tf_resource_type
                        ]
                    )
                    filtered_sls_resource = None
                    if (
                        tf_uuid in attributes
                        and f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{attributes[tf_uuid]}"
                        in filtered_sls_data
                    ):
                        filtered_sls_resource = filtered_sls_data[
                            f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{attributes[tf_uuid]}"
                        ]
                    else:
                        (
                            tf_unique_key_value_found_successfully,
                            tf_unique_value,
                            idem_unique_value,
                        ) = hub.tf_idem_auto.utils.generate_tf_unique_value(
                            tf_uuid, attributes, tf_resource_type
                        )
                        if (
                            tf_unique_key_value_found_successfully
                            and f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{tf_unique_value}"
                            in filtered_sls_data
                        ):
                            filtered_sls_resource = filtered_sls_data[
                                f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{tf_unique_value}"
                            ]

                    if filtered_sls_resource:
                        if len(tf_state_for_resource_under_processing["instances"]) > 1:
                            resource_path_to_update = f"{tf_resource_type}.{tf_resource_name}-{resource_index}"
                        else:
                            resource_path_to_update = (
                                f"{tf_resource_type}.{tf_resource_name}"
                            )
                        converted_sls_data[
                            resource_path_to_update
                        ] = filtered_sls_resource["resource"]
                        idem_resource_id_tf_resource_map[
                            f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{filtered_sls_resource.get('idem_resource_id')}"
                        ] = tf_resource
                        idem_resource_attributes_map = dict(
                            ChainMap(
                                *list(filtered_sls_resource["resource"].values())[0]
                            )
                        )
                        if "arn" in idem_resource_attributes_map:
                            idem_resource_id_map[
                                f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{idem_resource_attributes_map.get('arn')}"
                            ] = {
                                "resource": filtered_sls_resource["resource"],
                                "resource_path": resource_path_to_update,
                                "type": "arn",
                            }
                        idem_resource_id_map[
                            f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{filtered_sls_resource.get('idem_resource_id')}"
                        ] = {
                            "resource": filtered_sls_resource["resource"],
                            "resource_path": resource_path_to_update,
                            "type": "resource_id",
                        }
                        converted_sls_data.update({})
                    resource_index = resource_index + 1
            else:
                hub.log.warning(
                    "No resource found for '%s - %s'",
                    tf_resource_type,
                    tf_resource_name,
                )

            if security_group_ids:
                security_group_rule_index = 0
                for resource in filtered_sls_data.values():
                    if "aws.ec2.security_group_rule.present" in resource["resource"]:
                        resource_map = ChainMap(
                            *resource["resource"]["aws.ec2.security_group_rule.present"]
                        )
                        if resource_map.get("group_id") in security_group_ids:
                            converted_sls_data[
                                resource_path_to_update
                                + "-rule-"
                                + str(security_group_rule_index)
                            ] = resource["resource"]
                            idem_resource_id_map[
                                f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{resource['idem_resource_id']}"
                            ] = {
                                "resource": resource["resource"],
                                "resource_path": resource_path_to_update
                                + "-rule-"
                                + str(security_group_rule_index),
                                "type": "resource_id",
                            }
                            security_group_rule_index = security_group_rule_index + 1

    if "variable" in obj:
        variables.update(convert_variables_tf_to_sls(obj.get("variable"), tfvars_data))
    if "locals" in obj:
        local_variables = obj.get("locals")
        parameterized_locals = parameterize_values(local_variables, {})
        for key, value in parameterized_locals.items():
            variables.update({f"local_{key}": value})
    os.makedirs(os.path.dirname(output_sls_file_path), exist_ok=True)
    if "variables.tf" in input_tf_file_path:
        output_sls_file_path = (
            f"{output_sls_path}/params/{tf_file.replace('.tf', '.sls')}"
        )
        os.makedirs(os.path.dirname(output_sls_file_path), exist_ok=True)
    with open(output_sls_file_path, "w") as file:
        yaml.dump(
            dict(converted_sls_data), file, default_flow_style=False, Dumper=MyDumper
        )
    return idem_resource_id_map, idem_resource_id_tf_resource_map, variables


def parameterize_values(obj, new_dict):
    """
    Recursively goes through the dictionary obj and replaces keys with the convert function.
    """
    if isinstance(obj, str):
        return parameterize(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_dict[k] = parameterize_values(v, {})
            # return new_dict
    elif isinstance(obj, (list, set, tuple)):
        for item in obj:
            parameterize_values(item, new_dict)
    else:
        return obj
    return new_dict


def convert_variables_tf_to_sls(variables, tfvars_data):
    sls_vars = dict()
    for variable in variables:
        for key, value in variable.items():
            if key in tfvars_data:
                sls_vars[key] = tfvars_data.get(key)
                continue
            type = value.get("type")
            val = value.get("default")
            if type:
                if "list" in type:
                    new_val = json.dumps(value.get("default"))
                else:
                    new_val = val if val is not None else ""
            else:
                new_val = val if val is not None else ""
            sls_vars[key] = new_val

    return sls_vars


def convert_tf_files_to_sls(
    hub,
    root,
    filtered_sls_data,
    tf_reseource_type_name_and_resource_map,
    tfvars_data,
    directory_name,
    count,
):
    if hub.test:
        if hub.test.tf_idem_auto.unit_test:
            output_dir_path = f"{hub.test.tf_idem_auto.current_path}/expected_output"
        else:
            output_dir_path = f"{hub.test.tf_idem_auto.current_path}/output"
    else:
        output_dir_path = hub.OPT.tf_idem_auto.output_directory_path
    module_output_directory_path = os.path.join(
        output_dir_path,
        os.sep.join(root.split(os.sep)[count:]),
    )
    dir_list = os.walk(root)
    complete_resource_map = {}
    complete_tf_resource_map = {}
    complete_list_of_variables = {}
    name_of_files_in_module = []
    for path, subdirs, files in dir_list:
        for file in files:
            file_path = os.path.join(path, file)
            output_sls_path = os.path.join(
                output_dir_path,
                os.sep.join(path.split(os.sep)[count:]),
            )
            if file.endswith(".tf"):
                (
                    resource_map,
                    idem_resource_id_tf_resource_map,
                    variables,
                ) = convert_tf_file_to_sls(
                    hub,
                    file_path,
                    file,
                    filtered_sls_data,
                    tfvars_data,
                    tf_reseource_type_name_and_resource_map,
                    output_sls_path,
                )
                if resource_map is not None:
                    complete_resource_map.update(resource_map)
                if idem_resource_id_tf_resource_map is not None:
                    complete_tf_resource_map.update(idem_resource_id_tf_resource_map)
                if variables is not None:
                    complete_list_of_variables.update(variables)
                name_of_files_in_module.append(f"sls.{file[:-3]}")

    # Perform argument binding of all values in each resource of file, wherever possible
    resolve_argument_binding(
        hub,
        complete_resource_map,
        complete_tf_resource_map,
        module_output_directory_path,
        complete_list_of_variables,
    )

    # Generate parent init file
    os.makedirs(
        os.path.dirname(f"{module_output_directory_path}/init.sls"),
        exist_ok=True,
    )
    with open(f"{module_output_directory_path}/init.sls", "w") as _file:
        yaml.dump(
            {"include": sorted(name_of_files_in_module)},
            _file,
            default_flow_style=False,
        )

    # Generate variables.sls file to contain all the variables used in the module
    os.makedirs(
        os.path.dirname(f"{module_output_directory_path}/params/variables.sls"),
        exist_ok=True,
    )
    with open(f"{module_output_directory_path}/params/variables.sls", "w") as file1:
        yaml.dump(
            complete_list_of_variables, file1, default_flow_style=False, Dumper=MyDumper
        )

    generate_resource_ids_file(hub, module_output_directory_path, complete_resource_map)
    generate_params_init_file(module_output_directory_path)
    generate_delete_infra_file(
        directory_name, module_output_directory_path, complete_resource_map
    )

    return "All sls files generated."


def resolve_argument_binding(
    hub,
    complete_resource_map,
    complete_tf_resource_map,
    sls_directory,
    complete_list_of_variables,
):
    dir_list = os.walk(sls_directory)
    for path, subdir, files in dir_list:
        for file in files:
            file_path_arg = os.path.join(path, file)
            sls_file = open(file_path_arg)
            sls_file_data = yaml.safe_load(sls_file)
            if file not in (
                "variables.sls",
                "tags.sls",
                "resource_ids.sls",
                "init.sls",
            ):
                with open(file_path_arg, "a") as file:
                    file.truncate(0)
                    hub.tf_idem_auto.arg_binding_params_resolver.resolve_argument_bindings(
                        sls_file_data,
                        complete_tf_resource_map,
                        complete_resource_map,
                        complete_list_of_variables,
                        file,
                    )

            else:
                argument_binded_resource = sls_file_data
                os.makedirs(
                    os.path.dirname(file_path_arg),
                    exist_ok=True,
                )
                with open(file_path_arg, "w") as file1:
                    yaml.dump(argument_binded_resource, file1, Dumper=MyDumper1)


# Generate /params/resource_ids.sls file to store mapping of name and id of all resources that belong to the module
def generate_resource_ids_file(
    hub, module_output_directory_path, complete_resource_map
):
    idem_resource_type_resource_id_separator = (
        hub.tf_idem_auto.utils.idem_resource_type_resource_id_separator
    )
    resource_ids = {}
    for resource_id in complete_resource_map:

        resource = complete_resource_map[resource_id]
        if resource["type"] == "resource_id":
            idem_resource_type = list(resource["resource"].keys())[0].replace(
                ".present", ""
            )
            resource_ids[resource["resource_path"]] = resource_id.replace(
                f"{idem_resource_type}{idem_resource_type_resource_id_separator}", ""
            )
    with open(f"{module_output_directory_path}/params/resource_ids.sls", "w") as file1:
        yaml.dump(dict(resource_ids), file1, default_flow_style=False)


# Generate /params/init.sls file to initialize all variables and resource-ids
def generate_params_init_file(module_output_directory_path):
    param_list = []
    for file in os.listdir(f"{module_output_directory_path}/params/"):
        param_list.append(file[:-4])
    init_dict = {"include": sorted(param_list)}
    with open(f"{module_output_directory_path}/params/init.sls", "w") as file2:
        yaml.dump(init_dict, file2)


# Generate delete-{module_name}.sls file to destroy full cluster
def generate_delete_infra_file(
    module_name, module_output_directory_path, complete_resource_map
):
    delete_resource_map = {}
    attributes_to_include = ["name", "role_name", "policy_arn", "user_name"]
    for resource_id in complete_resource_map:
        resource_data = {}
        # truncating '.present' from end and append '.absent'
        resource_absent_key = f"{list(complete_resource_map[resource_id]['resource'].keys())[0][:-8]}.absent"
        resource_data[resource_absent_key] = []
        resource_attributes = list(
            complete_resource_map[resource_id]["resource"].values()
        )[0]
        # Since some resources have all attributes under one big dictionary and some have one attribute as one dict.
        if len(resource_attributes) == 1 and len(resource_attributes[0]) > 1:
            for attribute in resource_attributes[0]:
                if attribute in attributes_to_include:
                    resource_data[resource_absent_key].append(
                        {attribute: resource_attributes[0][attribute]}
                    )
        else:
            for attribute in resource_attributes:
                if list(attribute.keys())[0] in attributes_to_include:
                    resource_data[resource_absent_key].append(attribute)
        # If resource doesn't have any of the attributes to be included, then add resource_path as 'name'
        if len(resource_data[resource_absent_key]) == 0:
            resource_data[resource_absent_key].append(
                {"name": complete_resource_map[resource_id]["resource_path"]}
            )
        delete_resource_map[
            complete_resource_map[resource_id]["resource_path"]
        ] = resource_data
    with open(f"{module_output_directory_path}/delete-{module_name}.sls", "w") as _file:
        yaml.dump(delete_resource_map, _file, default_flow_style=False, Dumper=MyDumper)


class MyDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()
            super().write_line_break()


class MyDumper1(yaml.SafeDumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()
            super().write_line_break()

    def write_single_quoted(self, text, split=True):
        super().write_plain(text)


def convert_var_to_param(var_input):
    variable_names = []
    variable_name = var_input.group()[6:-1]
    variable_names.append(variable_name)  # Collect all the variables
    return f'{{{{ params.get("{variable_name}") }}}}'


def parameterize(resolved_value):
    parameterized_value = re.sub(
        r"\${var\.[\w-]+}", convert_var_to_param, resolved_value
    )
    return parameterized_value


tf_attributes_to_ignore = ["count", "lifecycle"]


def parameterize_resource(
    hub, tf_resource, sls_resource, tf_resource_type, tf_resource_name
):
    tf_idem_resource_type_map = hub.tf_idem_auto.utils.tf_idem_resource_type_map
    tf_resource_filtered = tf_resource[tf_resource_type][tf_resource_name]
    for tf_attribute in tf_resource_filtered:
        if tf_attribute not in tf_attributes_to_ignore:
            attribute_value = tf_resource_filtered[tf_attribute]
            if (
                not (
                    isinstance(attribute_value, dict)
                    or isinstance(attribute_value, list)
                    or isinstance(attribute_value, bool)
                )
                and "${var." in attribute_value
                and not " ? " in attribute_value
                and not "merge" in attribute_value
            ):
                parameterized_value = parameterize(attribute_value)
                for attributes in sls_resource[
                    tf_idem_resource_type_map.get(tf_resource_type) + ".present"
                ]:
                    update_parameter_values_in_sls(
                        attributes, tf_attribute, parameterized_value
                    )
    return sls_resource


def update_parameter_values_in_sls(attributes, tf_attribute, parameterized_value):
    for idem_attribute in attributes:
        if idem_attribute == tf_attribute:
            attributes[idem_attribute] = parameterized_value
    return attributes


def run_tf_to_sls_auto_convesion(
    hub, tf_reseource_type_name_and_resource_map, filtered_sls_data, tfvars_data
):
    for file in os.listdir():
        if file.endswith(".tf"):
            obj = hub.tf_idem_auto.utils.parse_tf_data(file)
            module = obj.get("module")
            # Perform tf to sls conversion for each module
            if module is not None:
                for mod in module:
                    for directory_name in mod.keys():
                        count = os.path.abspath(
                            mod.get(directory_name).get("source")
                        ).count("/")
                        for root, dirs, files in os.walk(
                            os.path.abspath(mod.get(directory_name).get("source"))
                        ):
                            # TODO : Detailed log explaining steps briefly is required here
                            convert_tf_files_to_sls(
                                hub,
                                root,
                                filtered_sls_data,
                                tf_reseource_type_name_and_resource_map,
                                tfvars_data,
                                directory_name,
                                count,
                            )
            else:
                # TODO : Detailed log explaining steps briefly is required here
                count = os.getcwd().count("/")
                convert_tf_files_to_sls(
                    hub,
                    os.getcwd(),
                    filtered_sls_data,
                    tf_reseource_type_name_and_resource_map,
                    tfvars_data,
                    file,
                    count,
                )
