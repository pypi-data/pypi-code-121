import os
from google.protobuf.duration_pb2 import Duration
from google.cloud.dataproc_v1 import ClusterControllerClient, Cluster, ClusterConfig
from google.cloud import storage
import subprocess
import sys


##
# @file
# @brief Helper functions for batch projects.


class ZIDSBatchHelper:
    """! General class for a variety of helper functions for batch processing projects
    The capabilities of this class include:
    *) Parsing batch configuration file
    *) Creating a Dataproc Cluster
    *) Uploading jars, stages and wheel archive to a given bucket
    """

    def __init__(self, stage_config):
        """! Initialize the class, primarily fill out configuration parameters

            Args:
                stage_config : Configuration dictionary, loaded from configuration file.
        """
        # Save the entire config file for cluster creation
        self.config = stage_config

        self.user_email = ''
        env_type = os.environ.get('SPRING_PROFILES_ACTIVE')
        if (not env_type == 'production') and (not env_type == 'staging'):
            command = 'gcloud config get-value account'
            user_email = subprocess.check_output(command, shell=True).decode(sys.stdout.encoding)
            self.user_email = user_email.split("@")[0]

        self.bucket_name = stage_config['bucket_name']
        self.project_id = stage_config['project_id']
        self.project_name = stage_config['project_name']
        self.region = stage_config['region']
        self.zone = self.region + '-b'  # TODO: Check if we can configure this as well
        self.template_id = stage_config['template_id']
        self.unique_iteration_id = stage_config['unique_iteration_id']
        self.cluster_name = stage_config['cluster_conf']['managed_cluster']['cluster_name']
        self.cluster_duration = stage_config['cluster_duration_sec']
        self.managed_cluster = stage_config['cluster_conf']['managed_cluster']

        if self.unique_iteration_id:
            self.folder_path = self.project_name + '/' + self.user_email + \
                               '/unique_iteration_id_' + self.unique_iteration_id
        else:
            self.folder_path = self.project_name + '/' + self.user_email + '/main'

        self.bucket_path = f'gs://{self.bucket_name}/{self.folder_path}'
        self.project_path = 'projects/{project_id}/regions/{region}'.format(project_id=self.project_id,
                                                                            region=self.region)
        # Placeholders for file upload actions
        self.storage_client = None
        self.bucket = None

    def create_dataproc_cluster(self):
        """! Create a GCP cluster on DataProc based on configurations from batch_config.json
        """

        # Defined used paths
        main_project_path = os.path.abspath(os.getcwd())

        # Extract pip packages for the cluster
        pip_packages = ''
        with open(main_project_path + '/requirements_docker.txt') as f:
            required = f.read().splitlines()
            required = [x for x in required if "#" not in x]
            pip_packages = ' '.join(required)

        client = ClusterControllerClient(
            client_options={"api_endpoint": f"{self.region}-dataproc.googleapis.com:443"}
        )

        # Instantiate a cluster
        cluster = Cluster()
        cluster.cluster_name = self.cluster_name
        cluster_init_action = {"executable_file": f"{self.bucket_path}/batch_files/scripts/cluster-init-actions.sh"}
        if self.managed_cluster:
            # Configure pip packages
            self.config['cluster_conf']['managed_cluster']['config']['gce_cluster_config']['metadata']['PIP_PACKAGES'] \
                = pip_packages

            # Configure initialization script
            cluster_init_list = self.config['cluster_conf']['managed_cluster']['config']['initialization_actions']
            if not isinstance(cluster_init_list, list):
                cluster_init_list = []

            cluster_init_list.append(cluster_init_action)

        managed_cluster_config = self.config['cluster_conf']['managed_cluster']['config']
        cluster_config = ClusterConfig(managed_cluster_config)

        cluster_duration = Duration(seconds=self.cluster_duration)
        cluster_config.lifecycle_config = {
            'idle_delete_ttl': cluster_duration
        }

        cluster.config = cluster_config

        # Getting cluster if it exists
        exist_cluster = None
        try:
            exist_cluster = client.get_cluster(
                project_id=self.project_id,
                region=self.region,
                cluster_name=self.cluster_name,
            )
            print(f'Cluster {self.cluster_name} retrieved successfully')

        except Exception as e:
            # A "404", not found exception, is expected here and should only be noted
            if "404" in str(e):
                print(f"Cluster {self.cluster_name} not found. Creating...")
            else:
                print(f'Error getting cluster: {e}')
                raise e

        # Updating the cluster if it exists
        if exist_cluster:
            try:
                updated_config_list = [
                    'config.worker_config.num_instances',
                    'config.secondary_worker_config.num_instances',
                    'labels'
                ]
                client.update_cluster(
                    project_id=self.project_id,
                    region=self.region,
                    cluster_name=self.cluster_name,
                    cluster=cluster,
                    update_mask={
                        "paths": updated_config_list
                    }
                )
                print(f'cluster {self.cluster_name} was updated successfully')

            except Exception as e:
                print(f'error updating cluster: {e}')

        # If no existing cluster was found, create it
        else:
            try:
                client.create_cluster(
                    project_id=self.project_id,
                    region=self.region,
                    cluster=cluster
                )
                print(f'Cluster {self.cluster_name} created successfully')

            except Exception as e:
                print(f'Error creating cluster: {e}')

    def get_client_check_cluster(self) -> (bool, ClusterControllerClient):
        """! Set up a client and check for an existing cluster
            Returns:
                Cluster: If a cluster was found, return its class
                ClusterControllerClient: Client for controlling the cluster
        """

        # Set up a client
        client = ClusterControllerClient(
            client_options={"api_endpoint": f"{self.region}-dataproc.googleapis.com:443"}
        )

        # Getting cluster if it exists
        cluster = None
        cluster_exists = False
        try:
            cluster = client.get_cluster(
                project_id=self.project_id,
                region=self.region,
                cluster_name=self.cluster_name,
            )
            print(f'Cluster {self.cluster_name} retrieved successfully')

        except Exception as e:
            # A "404", not found exception, is expected here and should only be noted
            if "404" in str(e):
                print(f"Cluster {self.cluster_name} not found.")
            else:
                print(f'Error getting cluster: {e}')
                raise e
        if cluster:
            cluster_exists = True
        return client, cluster_exists

    def start_dataproc_cluster(self):
        """! Start an existing GCP cluster on DataProc based on configurations from batch_config.json
        """
        client, existing_cluster = self.get_client_check_cluster()

        if existing_cluster:
            try:
                operation = client.start_cluster(
                    request={"project_id": self.project_id,
                             "region": self.region,
                             "cluster_name": self.cluster_name}
                )
                response = operation.result()
                print(f'Started cluster {self.cluster_name}. Result: {response} ')

            except Exception as e:
                print(f'Failed starting cluster {self.cluster_name}')

    def stop_dataproc_cluster(self):
        """! Stop an existing GCP cluster on DataProc based on configurations from batch_config.json
        """

        client, existing_cluster = self.get_client_check_cluster()

        if existing_cluster:
            try:
                operation = client.stop_cluster(
                    request={"project_id": self.project_id,
                             "region": self.region,
                             "cluster_name": self.cluster_name}
                )
                response = operation.result()
                print(f'Stopped cluster {self.cluster_name}. Result: {response} ')

            except Exception as e:
                print(f'Failed stopping cluster {self.cluster_name}')

    def delete_dataproc_cluster(self):
        """! Delete an existing DataProc cluster according to project specific configuration.
        Since we can't update certain parameters on an existing cluster, we need the option
        to delete it
        """

        client, existing_cluster = self.get_client_check_cluster()

        if existing_cluster:
            try:
                operation = client.delete_cluster(
                    project_id=self.project_id,
                    region=self.region,
                    cluster_name=self.cluster_name,
                )
                response = operation.result()
                print(f'Deleted cluster {self.cluster_name}. Result: {response} ')

            except Exception as e:
                print(f'Failed deleting cluster {self.cluster_name}')

    def connect_dataproc_cluster(self):
        """! Connect via ssh to an existing DataProc cluster according to project specific configuration.
        Connection will be made to the master node
        """

        # No need for the "client" variable that returns from the function
        _, existing_cluster = self.get_client_check_cluster()

        if existing_cluster:
            try:
                command = f'gcloud compute ssh {self.cluster_name}-m ' \
                          f'--project={self.project_id} ' \
                          f'--zone={self.zone} ' \
                          f'--tunnel-through-iap'
                process = subprocess.run(command, shell=True, check=True)

                print(f'Connection to cluster {self.cluster_name} ended. Result: {process.returncode}')

            except subprocess.CalledProcessError as e:
                print(f'Failed on connection to cluster {self.cluster_name}, Error: {e}')

    def upload_files_to_bucket(self, upload_type: str):
        """! Upload jars, stages, cluster init script and wheel file to a given bucket
                Args:
                    upload_type: String reflecting which file type we wish to upload to
                                 bucket (jars, stages, whl, cluster-init, all)
        """
        valid_types = {'all', 'jars', 'stages', 'whl', 'cluster-init'}
        if upload_type not in valid_types:
            print(f"Can't determine file type {upload_type}. "
                  f"Please use one of: 'all', 'jars', 'stages', 'whl', 'cluster-init'")
            return

        print(f'Uploading files of type: {upload_type} to bucket: {self.bucket_name}')

        self.storage_client = storage.Client(project=self.project_id)
        self.bucket = self.storage_client.get_bucket(self.bucket_name)

        parent_path = os.path.abspath(os.path.join(os.getcwd(), 'batch_files'))
        script_path = os.path.join(parent_path, 'scripts')

        if upload_type == 'all' or upload_type == 'jars':
            self.upload_jars_to_bucket(parent_path)
        if upload_type == 'all' or upload_type == 'stages':
            self.upload_stages_main_to_bucket(parent_path)
        if upload_type == 'all' or upload_type == 'whl':
            self.upload_whl_to_bucket(parent_path)
        if upload_type == 'all' or upload_type == 'cluster-init':
            self.upload_cluster_init_to_bucket(script_path)

    def upload_cluster_init_to_bucket(self, root_dir):
        """! Upload cluster initialization script to a given bucket
                Args:
                    root_dir: Directory in which we search for the cluster initialization script
        """
        name = 'cluster-init-actions.sh'
        path_local = os.path.join(root_dir, name)
        bucket_blob_path = path_local[path_local.index(self.project_name) + len(self.project_name):].replace('\\', '/')
        blob = self.bucket.blob(self.folder_path + bucket_blob_path)
        blob.upload_from_filename(path_local)
        # self.gsutils_upload_one_file(path_local, bucket_blob_path)
        print(f'uploaded cluster init script to: {bucket_blob_path}')

    def upload_jars_to_bucket(self, root_dir):
        """! Upload relevant jars to a given bucket
            Args:
                root_dir: Directory in which we search for the jars directory
        """

        for path, subdirs, files in os.walk(root_dir + '/jars'):
            for name in files:
                path_local = os.path.join(path, name)
                bucket_blob_path = path_local[path_local.index(self.project_name) +
                                              len(self.project_name):].replace('\\', '/')
                blob = self.bucket.blob(self.folder_path + bucket_blob_path)
                blob.upload_from_filename(path_local)
            # print(path_local)
            # print(bucket_blob_path)
        print('uploaded jars main successfully')

    def upload_stages_main_to_bucket(self, root_dir):
        """! Upload relevant stages to a given bucket
            Args:
                root_dir: Directory in which we search for the stages directory
        """

        for path, subdirs, files in os.walk(root_dir + '/stages'):
            for name in files:
                if name == 'main.py':
                    path_local = os.path.join(path, name)
                    bucket_blob_path = path_local[path_local.index(self.project_name) +
                                                  len(self.project_name):].replace('\\', '/')
                    blob = self.bucket.blob(self.folder_path + bucket_blob_path)
                    blob.upload_from_filename(path_local)
                # print(path_local)
                # print(bucket_blob_path)
                # print(name)
        print('uploaded stages main successfully')

    def upload_whl_to_bucket(self, root_dir):
        """! Upload relevant wheel file to a given bucket
            Args:
                root_dir: Directory in which we search for the wheel archive
        """

        parent_path = os.path.abspath(os.path.join(root_dir, ".."))
        dist = parent_path + '/dist'
        onlyfiles = [os.path.join(dist, f) for f in os.listdir(dist) if os.path.isfile(os.path.join(dist, f))]
        for path_local in onlyfiles:
            bucket_blob_path = path_local[path_local.index(self.project_name) +
                                          len(self.project_name):].replace('\\', '/')
            blob = self.bucket.blob(self.folder_path + bucket_blob_path)
            blob.chunk_size = 1024 * 1024
            blob.upload_from_filename(path_local)
        # print(path_local)
        # print(project_bucket_folder + bucket_blob_path)

        print(f'uploaded package whl successfully to: {self.folder_path}')

    def gsutils_upload_one_file(self, local_path, target_path):
        """! Upload relevant wheel file to a given bucket
            Args:
                local_path: Directory from which we copy the data
                target_path: Directory on the remote location to which we upload the data
        """

        command = '''gsutil -o GSUtil:parallel_composite_upload_threshold=150M -m cp \
        "''' + local_path + '''" \
        "''' + self.bucket_path + target_path + '''" \
        '''

        process = subprocess.call(command, shell=True)

