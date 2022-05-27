import os


def __init__(hub):
    # Remember not to start your app in the __init__ function
    # This function should just be used to set up the plugin subsystem
    # The run.py is where your app should usually start
    for dyne in ["idem"]:
        hub.pop.sub.add(dyne_name=dyne)


def cli(hub):
    hub.pop.config.load(["tf_idem_auto"], cli="tf_idem_auto")
    # Your app's options can now be found under hub.OPT.tf_idem_auto
    kwargs = dict(hub.OPT.tf_idem_auto)
    hub.test = None

    # Initialize the asyncio event loop
    hub.pop.loop.create()

    # Start the async code
    coroutine = hub.tf_idem_auto.init.run(**kwargs)
    hub.pop.Loop.run_until_complete(coroutine)


async def run(hub, **kwargs):
    """
    This is the entrypoint for the async code in your project
    """
    hub.log.info("tf_idem_auto conversion started...")

    # Get names of all modules defined in main.tf
    list_of_modules = get_module_list(hub)

    if not list_of_modules:
        hub.log.warning("Either main.tf doesn't exist or no modules found in main.tf")

    # Get tfvars_data, if tfvars file is present
    tfvars_data = collect_tfvars_data(hub)

    # Read terraform state file from S3 or 'tf_state_file_path'. Filter managed and data resources that belong
    # to modules obtained above and store processed tf_state data in file.
    # This step also gives the list of relevant resource types to describe in next step
    resource_types = hub.tf_idem_auto.tf_state_data_processor.process_tf_state_data(
        list_of_modules
    )
    hub.log.info("Filtered Terraform state data is written in 'processed_tfstate.json'")
    hub.log.info("Idem Resource types : %s", resource_types)

    # Perform idem describe on list of resource_types obtained above and write the response in file
    if hub.OPT.tf_idem_auto.idem_describe:
        hub.tf_idem_auto.idem_describe.run_idem_describe(resource_types)
        hub.log.info(
            "Consolidated SLS file is generated in '%s'",
            hub.OPT.tf_idem_auto.idem_describe_path,
        )

    # Read the consolidated SLS file from idem_describe_path. Filter the SLS data with
    # resources that are managed by Terraform only in all modules of cluster.
    (
        tf_reseource_type_name_and_resource_map,
        filtered_sls_data,
    ) = hub.tf_idem_auto.sls_file_filter.filter_sls()

    # Preprocessing is completed now. Starting with file by file conversion for each module in cluster
    hub.tf_idem_auto.tf_sls.run_tf_to_sls_auto_convesion(
        tf_reseource_type_name_and_resource_map, filtered_sls_data, tfvars_data
    )


def get_module_list(hub):
    list_of_modules = set()
    # Get the list of all files from main.tf expected to be present in current directory and create module list.
    for file in os.listdir():
        if file.endswith(".tf"):
            main_tf_data = hub.tf_idem_auto.utils.parse_tf_data(file)
            module = main_tf_data.get("module")
            if module is not None:
                for module_name in set().union(*(d.keys() for d in module)):
                    # fetch the list of modules present in the main.tf
                    list_of_modules.add(f"module.{module_name}")
    return list_of_modules


def collect_tfvars_data(hub):
    # Look for tfvars file in current directory and parse it into dictionary, if present
    tfvars_data = {}
    for file in os.listdir():
        if file.endswith(".tfvars"):
            tfvars_data = hub.tf_idem_auto.utils.parse_tf_data(file)
            break
    return tfvars_data
