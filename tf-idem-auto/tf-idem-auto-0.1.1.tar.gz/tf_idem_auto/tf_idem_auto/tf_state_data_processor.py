import json
import os
import pathlib

import boto3


# Processing resources
def process_tf_state_resources(hub, tf_state_resources, list_of_modules):
    processed_tf_state_resources = []
    idem_resource_types = (
        set()
    )  # Set of unique idem_resource_types, later used to perform 'Idem Describe' upon
    for resource in tf_state_resources:
        if "module" in resource and list_of_modules:
            if (
                resource["mode"] == "managed"
                and resource.get("module") in list_of_modules
            ):
                tf_resource_type = resource["type"]

                # Safe check to identify that the tool supports all concerned resource types of terraform and Idem
                # If no support found, then log the warning and ignore this resource data
                if (
                    tf_resource_type
                    not in hub.tf_idem_auto.utils.tf_idem_resource_type_map
                ):
                    hub.log.warning(
                        "Add mapping for the resource '%s'", tf_resource_type
                    )
                    continue

                idem_resource_type = (
                    hub.tf_idem_auto.utils.tf_idem_resource_type_map.get(
                        tf_resource_type
                    )
                )

                # Safe checks to identify that the tool knows uuid of all concerned resource types of terraform and Idem
                # If no uuid found, then log the warning and ignore this resource data
                if (
                    tf_resource_type not in hub.tf_idem_auto.utils.tf_resource_type_uuid
                    and tf_resource_type
                    not in hub.tf_idem_auto.utils.tf_resource_type_default_uuid
                ):
                    hub.log.warning(
                        "Add tf unique identifier for '%s'", tf_resource_type
                    )
                    if (
                        idem_resource_type
                        not in hub.tf_idem_auto.utils.idem_resource_type_uuid
                        and idem_resource_type
                        not in hub.tf_idem_auto.utils.idem_resource_type_default_uuid
                    ):
                        hub.log.warning(
                            f"Add idem unique identifier for '%s'", idem_resource_type
                        )
                    continue

                idem_resource_types.add(idem_resource_type)
                processed_tf_state_resources.append(resource)

            elif (
                resource["mode"] == "data" and resource.get("module") in list_of_modules
            ):
                # processed_tf_state_resources.append(resource)
                continue  # Placeholder to process 'data' constructs of Terraform
        else:
            if resource["mode"] == "managed":
                tf_resource_type = resource["type"]

                # Safe check to identify that the tool supports all concerned resource types of terraform and Idem
                # If no support found, then log the warning and ignore this resource data
                if (
                    tf_resource_type
                    not in hub.tf_idem_auto.utils.tf_idem_resource_type_map
                ):
                    hub.log.warning(
                        "Add mapping for the resource '%s'", tf_resource_type
                    )
                    continue

                idem_resource_type = (
                    hub.tf_idem_auto.utils.tf_idem_resource_type_map.get(
                        tf_resource_type
                    )
                )

                # Safe checks to identify that the tool knows uuid of all concerned resource types of terraform and Idem
                # If no uuid found, then log the warning and ignore this resource data
                if (
                    tf_resource_type not in hub.tf_idem_auto.utils.tf_resource_type_uuid
                    and tf_resource_type
                    not in hub.tf_idem_auto.utils.tf_resource_type_default_uuid
                ):
                    hub.log.warning(
                        "Add tf unique identifier for '%s'", tf_resource_type
                    )
                    if (
                        idem_resource_type
                        not in hub.tf_idem_auto.utils.idem_resource_type_uuid
                        and idem_resource_type
                        not in hub.tf_idem_auto.utils.idem_resource_type_default_uuid
                    ):
                        hub.log.warning(
                            f"Add idem unique identifier for '%s'", idem_resource_type
                        )
                    continue

                idem_resource_types.add(idem_resource_type)
                processed_tf_state_resources.append(resource)

    return processed_tf_state_resources, idem_resource_types


def process_tf_state_data(hub, list_of_modules):
    if hub.test:
        tf_state_file_path = (
            f"{hub.test.tf_idem_auto.current_path}/resources/tfstate.json"
        )
        tf_state_data = hub.tf_idem_auto.utils.read_tf_state(tf_state_file_path)

    else:
        if hub.OPT.tf_idem_auto.get_tf_state_from_s3:
            s3_client = boto3.client("s3")
            response = s3_client.get_object(
                Bucket=hub.OPT.tf_idem_auto.tf_state_bucket_name,
                Key=hub.OPT.tf_idem_auto.tf_state_key,
            )
            res = response["Body"].read().decode("utf-8")
            tf_state_data = json.loads(res)
        else:
            tf_state_data = hub.tf_idem_auto.utils.read_tf_state(
                hub.OPT.tf_idem_auto.tf_state_file_path
            )

    # Processing resources
    tf_state_data["resources"], resource_types = process_tf_state_resources(
        hub, tf_state_data["resources"], list_of_modules
    )

    # TODO : If any more constructs need to be processed in tf_state, add the logic here

    # Write the processed_tf_state data in 'processed_tfstate.json'
    if hub.test:
        if hub.test.tf_idem_auto.unit_test:
            output_dir_path = f"{hub.test.tf_idem_auto.current_path}/expected_output"
        else:
            output_dir_path = f"{hub.test.tf_idem_auto.current_path}/output"
        pathlib.Path(output_dir_path).mkdir(exist_ok=True)

    else:
        output_dir_path = hub.OPT.tf_idem_auto.output_directory_path
    processed_tf_state_file_path = os.path.join(
        output_dir_path, "processed_tfstate.json"
    )
    hub.log.info(
        "Processed terraform state file is saved in '%s'", processed_tf_state_file_path
    )
    tf_state_json = json.dumps(tf_state_data, indent=3)
    with open(processed_tf_state_file_path, "w") as outfile:
        outfile.write(tf_state_json)
        outfile.write("\n")
    return resource_types
