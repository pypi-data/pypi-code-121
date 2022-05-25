import os
import sys
from typing import List
from google.cloud.dataproc_v1.types.workflow_templates import TemplateParameter
from google.cloud.dataproc_v1.types import OrderedJob
from dsframework.base.batch.workflow_base import ZIDS_Workflow


class Workflow(ZIDS_Workflow):

    def __init__(self):
        """! Loads config file and initializes parameters.
        """
        self.default_jars = ['gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar']
        main_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

        self.pip_packages = ''
        with open(main_project_path + '/requirements_docker.txt') as req_file:
            required_pkg = req_file.read().splitlines()
            required_pkg = [x for x in required_pkg if "#" not in x]
            self.pip_packages = ' '.join(required_pkg)

        super().__init__(self.pip_packages)

        self.whl_pipes_file_name = self.project_name + '_pipes.zip'
        self.whl_no_pipes_file_name = self.project_name + '_no_pipes.zip'

        # Initialize spark properties.
        self.spark_properties = self.config["spark_properties"]

    def create_job(self, stage_name, prerequisite_list=None) -> OrderedJob():
        """! Create a job from a given stage

            Args:
                stage_name: Name of the stage to create
                prerequisite_list: list of stage id's that are mandatory to run before current stage

            Returns:
                An Ordered Job, to be inserted into the workflow template
        """
        stage_dir = f'batch_files/stages/{stage_name}'
        python_files = [self.whl_pipes_file_name,
                        self.whl_no_pipes_file_name]
        stage_job = self.create_ordered_job(stage_dir, self.spark_properties, python_files)

        if prerequisite_list is not None:
            stage_job.prerequisite_step_ids = prerequisite_list

        return stage_job

    def create_stages(self) -> List[OrderedJob]:
        """! Create the stages for the workflow stages
            Returns:
                A List of Ordered Jobs, to be inserted into the workflow template
        """
        # stage get_data
        stage_get_data_job = self.create_job("get_data")

        # stage run_pipeline
        prerequisite_list = [stage_get_data_job.step_id]
        stage_run_pipeline_job = self.create_job("run_pipeline", prerequisite_list)

        # stage set_data
        prerequisite_list = [stage_run_pipeline_job.step_id]
        stage_set_data_job = self.create_job("set_data", prerequisite_list)

        return [stage_get_data_job, stage_run_pipeline_job, stage_set_data_job]

    def finalize_jobs(self, workflow_template):
        """! Finalize the jobs, introduce additional parameters, etc.
            Args:
                workflow_template: Workflow templates. Includes jobs that we wish to modify
        """

        # Make sure to change jobs according to specific configuration
        if self.config['specific_jobs_to_run'] and len(self.config['specific_jobs_to_run']):
            specific_jobs_to_run = []
            for job in workflow_template.jobs:
                if job.step_id in self.config['specific_jobs_to_run']:
                    specific_jobs_to_run.append(job)
                    if self.config['force_remove_all_prerequisite']:
                        job.prerequisite_step_ids = []
                    if len(job.prerequisite_step_ids) and not all(
                            elem in specific_jobs_to_run for elem in job.prerequisite_step_ids):
                        raise Exception("job depends on another job not in specific_jobs_to_run list")
            workflow_template.jobs = specific_jobs_to_run

        # Set start and end dates from Airflow composer
        workflow_template.parameters = []

        start_date_param = TemplateParameter()
        start_date_param.description = "start date from airflow composer"
        start_date_param.name = "START_DATE"

        end_date_param = TemplateParameter()
        end_date_param.description = "end date from airflow composer"
        end_date_param.name = "END_DATE"

        extra_param = TemplateParameter()
        extra_param.description = "allow adding extra parameters"
        extra_param.name = "PARAMS"

        for job in workflow_template.jobs:
            start_date_param.fields.append("jobs['" + job.step_id + "'].pysparkJob.args[1]")
            end_date_param.fields.append("jobs['" + job.step_id + "'].pysparkJob.args[2]")
            extra_param.fields.append("jobs['" + job.step_id + "'].pysparkJob.args[3]")

        workflow_template.parameters.append(start_date_param)
        workflow_template.parameters.append(end_date_param)
        workflow_template.parameters.append(extra_param)

    def export_template_structure(self):
        """! Create the workflow template, and return it for external usage
            Returns:
                workflow_template: A ready to use template, WorkflowTemplate() class
        """
        # Define template structure
        workflow_template = self.create_template_structure()
        workflow_template.jobs = self.create_stages()
        self.finalize_jobs(workflow_template)
        return workflow_template

    def create_workflow_template(self, create_yaml: bool = False):
        """! Create the workflow template, along with all relevant stages
            Args:
                create_yaml: Boolean, deciding whether we should create a yaml file out of the template
        """

        # Check if a cluster exists. Not mandatory, as the workflow can create a cluster on the fly
        self.check_cluster()

        # Define template structure
        workflow_template = self.export_template_structure()

        print(f'{workflow_template}')

        # Make sure that the template does not exist
        self.check_template()

        # If needed, create a .yaml file, don't use Cloud API
        if create_yaml:
            self.create_yaml_file(workflow_template)

        else:
            # Create template by using Cloud API
            self.create_template(workflow_template)


if __name__ == "__main__":
    """! Triggers the creation of the workflow template, starting from
    basic configuration, defining and creating jobs from the existing stages, 
    and up to creating and instantiating the workflow, if needed.
        Args:
        System argument 1 - Action to be performed on a template (create, delete, instantiate)
    """

    template_action = "none"
    if sys.argv and len(sys.argv) > 1:
        template_action = sys.argv[1]
    workflow = Workflow()

    if template_action == 'create':
        workflow.create_workflow_template()

    if template_action == 'create_yaml':
        workflow.create_workflow_template(True)

    # At this point, a template is either previously or recently created
    template = workflow.get_workflow_template()

    if template_action == 'delete' and template:
        workflow.delete_workflow_template(template)

    if template_action == 'instantiate' and template:
        workflow.instantiate_template(template)
