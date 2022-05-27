import os
from collections import ChainMap


def compare_and_filter_sls(hub, tf_resources, idem_resource_uuid_and_resource_map):
    idem_resource_type_resource_id_separator = (
        hub.tf_idem_auto.utils.idem_resource_type_resource_id_separator
    )
    tf_idem_resource_type_map = hub.tf_idem_auto.utils.tf_idem_resource_type_map
    tf_resource_type_uuid = hub.tf_idem_auto.utils.tf_resource_type_uuid
    tf_reseource_type_name_and_resource_map = {}
    security_group_ids = []
    filtered_sls_data = {}
    for tf_resource in tf_resources:
        tf_resource_type = tf_resource["type"]
        tf_resource_name = tf_resource["name"]

        # Constructing map to avoid iterating over tf_data again : <tf_resource_type__tf_resource_name, tf_resource>
        tf_reseource_type_name_and_resource_map[
            f"{tf_resource_type}__{tf_resource_name}"
        ] = tf_resource

        for resource_instance in tf_resource["instances"]:
            attributes = resource_instance["attributes"]
            if tf_resource_type == "aws_security_group":
                security_group_ids.append(attributes["id"])
            tf_uuid = (
                "id"
                if tf_resource_type not in tf_resource_type_uuid
                else tf_resource_type_uuid[tf_resource_type]
            )
            if (
                tf_uuid in attributes
                and f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{attributes[tf_uuid]}"
                in idem_resource_uuid_and_resource_map
            ):
                filtered_sls_data[
                    f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{attributes[tf_uuid]}"
                ] = {
                    "resource": idem_resource_uuid_and_resource_map[
                        f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{attributes[tf_uuid]}"
                    ],
                    "idem_resource_id": attributes[tf_uuid],
                }
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
                    in idem_resource_uuid_and_resource_map
                ):
                    filtered_sls_data[
                        f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{tf_unique_value}"
                    ] = {
                        "resource": idem_resource_uuid_and_resource_map[
                            f"{tf_idem_resource_type_map.get(tf_resource_type)}{idem_resource_type_resource_id_separator}{tf_unique_value}"
                        ],
                        "idem_resource_id": idem_unique_value,
                    }
                else:
                    hub.log.warning(
                        "Invalid uuid key defined for tf resource type '%s'",
                        tf_resource_type,
                    )

    if security_group_ids:
        security_group_rules = get_security_group_rules(
            security_group_ids, idem_resource_uuid_and_resource_map
        )
        filtered_sls_data.update(security_group_rules)

    return tf_reseource_type_name_and_resource_map, filtered_sls_data


# Constructing map to avoid iterating over sls_data again : <idem_resource_uuid, idem_resource>
def construct_idem_resource_uuid_value_and_resource_map(hub, sls_data):
    idem_resource_type_resource_id_separator = (
        hub.tf_idem_auto.utils.idem_resource_type_resource_id_separator
    )
    idem_resource_type_uuid = hub.tf_idem_auto.utils.idem_resource_type_uuid
    idem_resource_uuid_and_resource_map = {}
    for idem_resource_name in sls_data:
        resource_data = sls_data[idem_resource_name]
        resource_type = list(resource_data.keys())[0][
            :-8
        ]  # truncating '.present' from end
        resource_uuid_key = (
            "resource_id"
            if resource_type not in idem_resource_type_uuid
            else idem_resource_type_uuid[resource_type]
        )
        idem_filters = [resource_uuid_key]
        if "::" in resource_uuid_key:
            idem_filters = resource_uuid_key.split("::")

        resource_attribute_dicts = list(resource_data.values())[0]
        resource_attributes = dict(ChainMap(*resource_attribute_dicts))

        idem_unique_value = ""
        idem_unique_key_value = ""
        idem_unique_key_value_found_successfully = True
        for idem_filter in idem_filters:
            # NOTE : If uuid is not properly declared in idem_resource_type_uuid, then all sls instances of this
            # resource type will be ignored in filtered sls data. Henceforth, in TF to SLS file conversion, such
            # resource types will not appear in SLS
            if idem_filter not in resource_attributes:
                hub.log.warning(
                    "Invalid uuid key defined for idem resource type '%s'",
                    resource_type,
                )
                idem_unique_key_value_found_successfully = False
                break
            idem_unique_value = (
                idem_unique_value
                + (":" if idem_unique_value else "")
                + resource_attributes[idem_filter]
            )
            idem_unique_key_value = (
                idem_unique_key_value
                + ("-" if idem_unique_key_value else "")
                + resource_attributes[idem_filter]
            )
        # TODO : Check if we have to use idem_unique_value or idem_unique_key_value
        if idem_unique_key_value_found_successfully:
            idem_resource_uuid_and_resource_map[
                f"{resource_type}{idem_resource_type_resource_id_separator}{idem_unique_value}"
            ] = resource_data

    return idem_resource_uuid_and_resource_map


def filter_sls(hub):
    if hub.test:
        if hub.test.tf_idem_auto.unit_test:
            output_dir_path = f"{hub.test.tf_idem_auto.current_path}/expected_output"
        else:
            output_dir_path = f"{hub.test.tf_idem_auto.current_path}/output"
    else:
        output_dir_path = hub.OPT.tf_idem_auto.output_directory_path
    tf_data = hub.tf_idem_auto.utils.read_tf_state(
        os.path.join(output_dir_path, "processed_tfstate.json")
    )
    if hub.test:
        idem_describe_path = (
            f"{hub.test.tf_idem_auto.current_path}/resources/idem_describe_response.sls"
        )
    else:
        idem_describe_path = hub.OPT.tf_idem_auto.idem_describe_path
    sls_data = hub.tf_idem_auto.utils.parse_sls_data(idem_describe_path)
    idem_resource_uuid_and_resource_map = (
        construct_idem_resource_uuid_value_and_resource_map(hub, sls_data)
    )
    tf_reseource_type_name_and_resource_map, filtered_sls_data = compare_and_filter_sls(
        hub, tf_data["resources"], idem_resource_uuid_and_resource_map
    )
    return tf_reseource_type_name_and_resource_map, filtered_sls_data


def get_security_group_rules(security_group_ids, idem_resource_uuid_and_resource_map):
    security_group_rules = {}
    for key, value in idem_resource_uuid_and_resource_map.items():
        sgr_resource = {}
        if "aws.ec2.security_group_rule.present" in value:
            resource = ChainMap(*value["aws.ec2.security_group_rule.present"])
            if resource.get("group_id") in security_group_ids:
                sgr_resource["resource"] = value
                sgr_resource["idem_resource_id"] = key
                security_group_rules[key] = sgr_resource
    return security_group_rules


def get_resource_id_from_sls_data(sls_resource_data):
    sls_data_list = list(sls_resource_data.values())[0]
    for resource_attr in sls_data_list:
        if resource_attr == "resource_id":
            return sls_data_list[resource_attr]
