"""! @brief ZIDS_Dag base class for the batch dag class.
The DAG (Directed acyclic graph) will trigger the workflow, derived from the workflow template"""

from json import load as json_load
import sys
import os
import logging
import subprocess


##
# @file
# @brief Defines dag base class.
class ZIDS_Dag():
    def __init__(self):
        """! ZIDS_Dag initializer.
        Loads config file.
        """

        file_path = sys.modules[self.__class__.__module__].__file__
        curr_path = file_path[:file_path.rfind("batch_files")]

        dag_config = None
        with open(curr_path + '/batch_files/batch_config.json') as batch_cfg_file:
            dag_config = json_load(batch_cfg_file)

        # Configure logger
        self.logger = logging.getLogger('DAG_logger')
        level = logging.getLevelName(dag_config['log_level'].upper())
        self.logger.setLevel(level)

        self.user_email = ''
        self.environment = dag_config['environment']
        self.bucket_name = dag_config['bucket_name']
        self.project_id = dag_config['project_id']
        self.project_name = dag_config['project_name']
        self.target = dag_config['target']
        self.template_id = dag_config['template_id']
        self.region = dag_config['region']
        self.unique_template_id = dag_config['unique_template_id']

        # For Stg and Prd environments, we want DAG to be created and immediately be active
        self.start_as_paused = True

        env_type = os.environ.get('SPRING_PROFILES_ACTIVE')
        if (env_type == 'production') or (env_type == 'staging'):
            self.start_as_paused = False
        else:
            # If we're not under staging or production envs, get user email for personalized dag folder path
            command = 'gcloud config get-value account'
            user_email = subprocess.check_output(command, shell=True).decode(sys.stdout.encoding)
            self.user_email = user_email.split("@")[0]

        # Set the upload folder for the dag file
        if self.unique_template_id:
            self.folder_path = self.project_name + '/' + self.user_email + '/unique_template_id_' \
                               + self.unique_template_id
        else:
            self.folder_path = self.project_name + '/' + self.user_email

    def get_basic_dag_code(self) -> str:
        """! Get basic code for dag creation
        Returns:
            A string, containing tailored code for creation of a DAG
        """
        dag_str = '''
        # STEP 1: Libraries needed
        from json import dumps as json_dumps
        from datetime import timedelta, datetime
        from airflow import models
        from airflow.providers.google.cloud.operators.dataproc import DataprocInstantiateWorkflowTemplateOperator

        region = "''' + self.region + '''"
        zone = region + '-b'
        project_id = "''' + self.project_id + '''"
        template_id = "''' + self.template_id + '''"
        bucket_name = "''' + self.bucket_name + '''"
        project_name = "''' + self.project_name + '''"
        target = "''' + self.target + '''"
        orig_project_name = project_name
        unique_template_id = "''' + self.unique_template_id + '''"
        if unique_template_id:
            template_id = template_id + '_' + unique_template_id
            orig_project_name = orig_project_name + '_' + unique_template_id

        dags_bucket_path = f'gs://{bucket_name}/dags'
        extra_dag_job_params = json_dumps({"MODE": "AIRFLOW", "TEST_EXEC_DATE": "{{ next_execution_date }}"})
        
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        now = now - timedelta(days=1)
        # STEP 3: Set default arguments for the DAG
        default_dag_args = {
            'start_date': now,
            'depends_on_past': False,
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1,
            'retry_delay': timedelta(minutes=5)
        }
        # Define a DAG (directed acyclic graph) of tasks.
        # Any task you create within the context manager is automatically added to the
        # DAG object.
        with models.DAG(
            orig_project_name + '_' + target + '_workflow_dag',
            description='DAG for deployment a Dataproc Cluster for ' + project_id,
            # schedule_interval=timedelta(days=1),
            schedule_interval='@daily',
            default_args=default_dag_args,
            is_paused_upon_creation=''' + str(self.start_as_paused) + '''
        ) as dag:

            start_template_job = DataprocInstantiateWorkflowTemplateOperator(
                # The task id of your job
                task_id="dataproc_workflow_dag_python",
                # The template id of your workflow
                template_id=template_id,
                project_id=project_id,
                # The region for the template
                region=region,
                parameters={"START_DATE": "{{ execution_date }}","END_DATE": "{{ next_execution_date }}", "PARAMS": extra_dag_job_params}
            )

        '''
        return dag_str

    def import_dag(self):
        """! Dag import.
                This function imports the created DAG file into a GCP composer.
        """

        source = self.file_name

        command = '''gcloud composer environments storage dags import \
            --environment "''' + self.environment + '''" \
            --location "''' + self.region + '''" \
            --source "''' + source + '''" \
            --destination "''' + self.folder_path + '''"
        '''

        process = subprocess.call(command, shell=True)

        os.unlink(self.file_name)
        dag_path = self.bucket_name + '/dags/' + self.folder_path + '/' + source
        print(f'finish uploading dag to - {dag_path}')

    def delete_dag(self):
        """! Dag deletion.
                This function deletes an existing DAG from a GCP composer.
        """

        source = self.file_name

        command = '''gcloud composer environments storage dags delete \
            --environment "''' + self.environment + '''" \
            --location "''' + self.region + '''"\
             "''' + source + '''"
        '''

        process = subprocess.call(command, shell=True)

        os.unlink(self.file_name)
        dag_path = self.bucket_name + '/dags/' + self.folder_path + '/' + source
        print(f'finish deleting dag from - {dag_path}')

    def create_dag(self):
        """! ZIDS_Dag main function.
        This function is the "entrypoint" for the dag creation.
        """

        raise NotImplementedError

