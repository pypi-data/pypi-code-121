import os

import hcl2


def process_tf_to_sls(hub):
    # Get the list of all files from main.tf. Process each module using source path
    # and convert into an sls as per directory structure
    for file in os.listdir():
        if file.endswith(".tfvars"):
            tfvars_data = hub.tf_idem_auto.utils.parse_tf_data(file)

    for file in os.listdir():
        if file.endswith(".tf"):
            if file == "main.tf":
                with open(file) as fp:
                    obj = hcl2.load(fp)
                    module = obj.get("module")
                    # Perform tf to sls conversion for each module
                    for mod in module:
                        for key in mod.keys():
                            for root, dirs, files in os.walk(
                                os.path.abspath(mod.get(key).get("source"))
                            ):
                                # Read the consolidated SLS file from idem_describe_input. Filter the SLS data with
                                # resources that are managed by Terraform only.
                                (
                                    tf_reseource_type_name_and_resource_map,
                                    filtered_sls_data,
                                ) = hub.tf_idem_auto.sls_file_filter.filter_sls()

                                # TODO : Detailed log explaining steps briefly is required here
                                hub.tf_idem_auto.tf_sls.convert_tf_files_to_sls(
                                    root,
                                    filtered_sls_data,
                                    tf_reseource_type_name_and_resource_map,
                                    tfvars_data,
                                    key,
                                )


def collect_module_list_and_idem_data(hub):
    # get module list
    list_of_modules = get_module_list()

    # Read terraform state file from 'tf_state_file_path'. Filter managed and data resources that belong to
    # list_of_modules. This step also gives the list of resource types to describe in next step
    resource_types = hub.tf_idem_auto.tf_state_data_processor.process_tf_state_data(
        list_of_modules
    )
    if hub.test:
        tf_state_processed_file_path = (
            f"{hub.test.tf_idem_auto.current_path}/resources/tfstate.json"
        )
    else:
        tf_state_processed_file_path = hub.OPT.tf_idem_auto.tf_state_processed_file_path

    hub.log.info(
        "Filtered Terraform state data is written in '%s'",
        tf_state_processed_file_path,
    )
    hub.log.info("Idem Resource types : %s", resource_types)

    # Perform idem describe on list of resource_types obtained above and write the response to consolidated sls file
    if hub.OPT.tf_idem_auto.idem_describe:
        hub.tf_idem_auto.idem_describe.run_idem_describe(resource_types)
        hub.log.info(
            "Consolidated SLS file is generated in '%s'",
            hub.OPT.tf_idem_auto.idem_describe_output,
        )


def get_module_list():
    list_of_modules = []
    # Get the list of all files from main.tf and create module list.
    for file in os.listdir():
        if file.endswith(".tf"):
            # Processing only main.tf which is mainly required for creating cluster
            if file == "main.tf":
                with open(file) as fp:
                    obj = hcl2.load(fp)
                    module = obj.get("module")
                    for mod_list in module:
                        for key in mod_list.keys():
                            # fetch the list of modules present in the main.tf
                            list_of_modules.append("module." + key)
    return list_of_modules
