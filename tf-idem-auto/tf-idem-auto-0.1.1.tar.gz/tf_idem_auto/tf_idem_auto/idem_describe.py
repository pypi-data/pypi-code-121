import os
import subprocess

import yaml


def run_idem_describe(hub, resource_types):
    hub.log.warning(
        "Total count of resource types to be describe : '%s'", len(resource_types)
    )
    count = 1
    temp_file_path = os.path.join(
        hub.OPT.tf_idem_auto.output_directory_path, "temp_file.sls"
    )
    for resource_type in resource_types:
        hub.log.warning("'%d' -> idem describe '%s' - Started!", count, resource_type)
        temp_file = open(temp_file_path, "w")
        process = subprocess.Popen(
            ["idem", "describe", resource_type], stdout=temp_file
        )
        process.wait()
        temp_file.close()
        copy_sls_data = {}
        read_file = open(temp_file_path)  # Open the sls file
        sls_data = yaml.load(
            read_file.read(), Loader=yaml.FullLoader
        )  # Read the data from sls file. Parse using yaml parser
        read_file.close()
        if len(sls_data) == 0:
            hub.log.warning(
                "idem describe '%s' - Completed with no data!", resource_type
            )
            count = count + 1
            continue
        for idem_resource_name in sls_data:
            copy_sls_data[f"{resource_type}.{idem_resource_name}"] = sls_data[
                idem_resource_name
            ]
        with open(hub.OPT.tf_idem_auto.idem_describe_path, "a") as sls_file:
            yaml.dump(copy_sls_data, sls_file, default_flow_style=False)
        hub.log.warning("idem describe '%s' - Completed!", resource_type)
        count = count + 1
    os.remove(temp_file_path)
