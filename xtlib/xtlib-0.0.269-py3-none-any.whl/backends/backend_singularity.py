#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# backend_singularity.py: support for running jobs under the Microsoft Singularity platform (similiar to AML and ITP)

import os

from azureml.core import Environment, Experiment, ScriptRunConfig, Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.contrib.aisc.aiscrunconfig import AISuperComputerConfiguration
import azureml.core

from xtlib import utils
from xtlib import constants
from xtlib import file_utils
from xtlib.backends.backend_aml import AzureML
from xtlib.console import console

class Singularity(AzureML):

    def __init__(self, compute, compute_def, core, config, username=None, arg_dict=None, disable_warnings=True):
        super(Singularity, self).__init__(compute, compute_def, core, config, username, arg_dict, disable_warnings)

        # blobfuse is still busted if we are using their default docker images
        # for now, let's assume we are using latest good pytorch-xtlib docker image
        self.mounting_enabled = True   # False

    # API call
    def get_name(self):
        return "singularity"

    # API call
    def provides_container_support(self):
        '''
        Returns:
            returns True if docker run command is handled by the backend.
        Description:
            For Singularity, they only support containers we can cannot run native to launch our own docker.
        '''
        return True   
        
    # API call
    def add_service_log_copy_cmds(self, cmds, dest_dir, args):

        self.append(cmds, "mkdir -p {}".format(dest_dir))

        # copy known singularity log directories 
        for log_dir in ["azureml-logs", "system_logs", "user_logs"]:
            self.append(cmds, "cp -r -v $AZUREML_CR_EXECUTION_WORKING_DIR_PATH/{} {}".format(log_dir, dest_dir))

        # this is now copy in user_logs above
        #self.append(cmds, "cp -r -v $AZUREML_CR_EXECUTION_WORKING_DIR_PATH/user_logs/std_log.txt {}".format(dest_dir))

    # API call
    def adjust_run_commands(self, job_id, job_runs, using_hp, experiment, service_type, snapshot_dir, env_vars, args):

        # call AML to do the normal work
        super().adjust_run_commands(job_id, job_runs, using_hp, experiment, service_type, snapshot_dir, env_vars, args)

        # move long/secret env vars into a file
        text = ""
        for key in ["XT_BOX_SECRET", "XT_SERVER_CERT", "XT_STORE_CREDS", "XT_DB_CREDS"]:
            value = env_vars[key]
            text += "{}={}\n".format(key, value)

            # remove from environt_variables
            del env_vars[key]

        # write text to set_env file in bootstrap dir
        bootstrap_dir = args["bootstrap_dir"]
        fn = bootstrap_dir + "/" + constants.FN_SET_ENV_VARS
        with open(fn, "wt") as outfile:
            outfile.write(text)

    def configure_rc_for_docker(self, rc, trainer, args):
        use_docker = trainer.run_config.docker.use_docker

        if use_docker:
            # old idea: this tells Singularity to use my docker image "as is" (don't build a new image with it as the base)
            # new idea: I don't know what this does anymore
            rc.environment.python.user_managed_dependencies = True

            rc.docker = trainer.run_config.docker  
            rc.docker.use_docker = True
            docker = rc.environment.docker

            old_env = trainer.run_config.environment
            old_registry = old_env.docker.base_image_registry  

            container_registry, image_url, sing_dict = self.get_docker_container_registry(args)
            sing_wrap = sing_dict["sing_wrap"]

            if sing_wrap:
                # wrap our docker image with a singularity-compliant image
                docker.base_image = None
                docker.base_image_registry = None

                sha256 = sing_dict["sha256"]
                post_sing_steps = sing_dict["post_sing_steps"]

                if sha256:
                    image_url2 = image_url.split(":")[0] + "@sha256:" + sha256
                else:
                    image_url2 = image_url
                registry_url = old_registry.address

                # tell singularity to upgrade my docker image to be singularity-compliant
                fn = file_utils.get_xtlib_dir() + "/backends/" + constants.FN_BUILD_STEPS_TEMPLATE
                with open(fn, "rt") as infile:
                    build_steps_template = infile.read()
                
                build_steps = build_steps_template.format(registry_url, image_url, registry_url, image_url2)

                # add singularity cleanup commands to docker build steps
                if post_sing_steps:
                    for step in post_sing_steps:
                        build_steps += "\n" + step

                docker.base_dockerfile = build_steps
            
            else:
                # use our docker image directly (no wrapping)
                #docker.base_image = image_url
                docker.base_image = old_registry.address + "/" + image_url
                docker.base_dockerfile = None

                registry = azureml.core.ContainerRegistry()
                docker.base_image_registry = registry
                registry.address = old_registry.address
                registry.username = old_registry.username
                registry.password = old_registry.password


    def run_job_on_singularity(self, experiment, trainer, arg_parts, args):
        ws = experiment.workspace

        armid = (
            f"/subscriptions/{ws.subscription_id}/"
            f"resourceGroups/{ws.resource_group}/"
            "providers/Microsoft.MachineLearningServices/"
            f"virtualclusters/{trainer._compute_target}"
        )

        src = ScriptRunConfig(source_directory=trainer.source_directory, command=arg_parts)

        rc = src.run_config 
        rc.target = "aisupercomputer"
        rc.node_count = 1
        
        # add env vars from trainer
        for name, value in trainer.run_config.environment.environment_variables.items():
            rc.environment_variables[name] = value

        # Neither of these settings will be required once this task is marked Done:
        # https://dev.azure.com/msdata/Vienna/_workitems/edit/1644223
        rc.environment_variables['AZUREML_COMPUTE_USE_COMMON_RUNTIME'] = 'true'
        rc.environment_variables['JOB_EXECUTION_MODE'] = 'basic'
        rc.environment_variables['OMPI_COMM_WORLD_SIZE'] = '1' # SKU=G1
        
        rc.environment = Environment(name="xt_env")

        self.configure_rc_for_docker(rc, trainer, args)

        location = utils.safe_value(self.compute_def, "location", None)
        vm_size = utils.safe_value(self.compute_def, "vm-size", None)
        sla_tier = utils.safe_value(self.compute_def, "sla", "basic").capitalize()
        
        username = args["username"]

        ai = AISuperComputerConfiguration()
        rc.aisupercomputer = ai
        ai.instance_type = vm_size       # "NC6_v3"     
        ai.location = location
        ai.sla_tier = sla_tier
        ai.image_version = '' 
        ai.scale_policy.auto_scale_interval_in_sec = 47
        ai.scale_policy.max_instance_type_count = 1
        ai.scale_policy.min_instance_type_count = 1
        ai.virtual_cluster_arm_id = armid
        ai.enable_azml_int = False
        ai.interactive = False
        ai.ssh_public_key = None

        # submit the job
        run = Experiment(workspace=ws, name=username).submit(src)

        #run.wait_for_completion(show_output=True)
        return run
            
    # API call
    def run_job_on_service(self, job_id, workspace, sing_ws_name, trainer, experiment, xt_exper_name, sing_exper_name, compute_target, cwd, run_name, box_name, 
            node_index, repeat, fake_submit, arg_parts, args):
        monitor_cmd = None

        console.diag("before AML experiment.submit(trainer)")

        # SUBMIT the run and return an AML run object
        if fake_submit:
            sing_run = None 
            sing_run_id = "fake_sing_id"
            sing_run_number = 999
        else:
            sing_run = self.run_job_on_singularity(experiment, trainer, arg_parts, args)
            sing_run_id = sing_run.id
            sing_run_number = sing_run.number

        # copy to submit-logs
        utils.copy_data_to_submit_logs(args, self.serializable_trainer, "sing_submit.json")

        console.diag("after AML experiment.submit(trainer)")

        jupyter_monitor = args["jupyter_monitor"]
        sing_run_name = sing_exper_name + ".{}".format(run_name)

        # set "xt_run_name" property for fast access to run in future
        if not fake_submit:
            sing_run.add_properties({"xt_run_name": sing_run_name})
            sing_run.set_tags({"xt_run_name": sing_run_name})

        console.print("  friendly name:", sing_run.display_name)
        #console.print("  experiment_url:", sing_run._experiment_url)

        #run_url = sing_run._run_details_url
        run_url = sing_run.portal_url + "/runs/" + sing_run.id
        console.print("  run url:", run_url)

        if jupyter_monitor:
            fn = self.make_monitor_notebook(sing_ws_name, sing_run_name)
            dir = os.path.dirname(fn)
            #console.print("jupyter notebook written to: " + fn)
            monitor_cmd = "jupyter notebook --notebook-dir=" + dir
        
        return run_name, monitor_cmd, sing_run_name, sing_run_number, sing_run_id

       


