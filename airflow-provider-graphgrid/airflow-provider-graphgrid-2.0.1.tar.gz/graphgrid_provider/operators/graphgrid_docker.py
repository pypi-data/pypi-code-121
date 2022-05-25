"""Implement Docker"""
# pylint: disable=no-name-in-module,import-error
import os
from typing import Optional, Union, List, Dict

from airflow.exceptions import AirflowException
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount, DeviceRequest


# pylint: disable=too-few-public-methods
class GraphGridDockerOperator(DockerOperator):
    """Extend DockerOperator to add fields and GPU support"""
    template_fields = ('command', 'environment', 'container_name', 'image',
                       'mounts', 'gpu')

    def __init__(self, *args, mounts: Optional[List[Mount]] = None,
                 environment: Optional[Dict] = None,
                 docker_url="tcp://socat:2375",
                 network_mode="graphgrid",
                 labels: Optional[Union[dict, list]] = None,
                 gpu: Optional[bool] = False,
                 include_credentials: Optional[bool] = True,
                 **kwargs):
        self.container = None
        self.mounts = mounts if mounts is not None else []
        self.environment = environment if environment is not None else {}
        if include_credentials:
            graphgrid_data = os.environ.get("GRAPHGRID_DATA")

            if graphgrid_data is not None:
                credentials_external_path = os.path.join(graphgrid_data,
                                                         "graphgrid", "config",
                                                         "credentials")
                credentials_internal_path = os.environ.get(
                    "GRAPHGRID_CONFIG_CREDENTIALS_PATH")
                credentials_internal_filename = os.environ.get(
                    "CONFIG_CREDENTIAL_PROPERTIES_FILENAME")
                if credentials_internal_path is not None:
                    self.mounts.append(GraphGridMount(
                        target=credentials_internal_path,
                        source=credentials_external_path, type="bind"))

                self.environment.update({
                    "GRAPHGRID_CONFIG_CREDENTIALS_PATH": credentials_internal_path,
                    "CONFIG_CREDENTIAL_PROPERTIES_FILENAME": credentials_internal_filename
                })

        super().__init__(*args, docker_url=docker_url,
                         network_mode=network_mode, mounts=self.mounts,
                         environment=self.environment, **kwargs)
        if labels is None:
            self.labels = {}
        self.labels.update({"logspout.exclude": "true"})
        self.gpu = gpu
        self.gpu_request = DeviceRequest(count=-1, capabilities=[['gpu']])

    def _run_image_with_mounts(self, target_mounts, add_tmp_variable: bool) -> \
            Optional[str]:
        self.log.info(f"Running with gpu set to '{self.gpu}'.")
        if add_tmp_variable:
            self.environment['AIRFLOW_TMP_DIR'] = self.tmp_dir
        else:
            self.environment.pop('AIRFLOW_TMP_DIR', None)
        self.container = self.cli.create_container(
            command=self.format_command(self.command),
            name=self.container_name,
            environment={**self.environment, **self._private_environment},
            host_config=self.cli.create_host_config(
                auto_remove=False,
                mounts=target_mounts,
                network_mode=self.network_mode,
                shm_size=self.shm_size,
                dns=self.dns,
                dns_search=self.dns_search,
                cpu_shares=int(round(self.cpus * 1024)),
                mem_limit=self.mem_limit,
                cap_add=self.cap_add,
                extra_hosts=self.extra_hosts,
                privileged=self.privileged,
                device_requests=[self.gpu_request] if self.gpu else []
            ),
            image=self.image,
            user=self.user,
            entrypoint=self.format_command(self.entrypoint),
            working_dir=self.working_dir,
            tty=self.tty,
            labels=self.labels,
        )
        lines = self.cli.attach(container=self.container['Id'], stdout=True,
                                stderr=True, stream=True)
        try:
            self.cli.start(self.container['Id'])

            line = ''
            res_lines = []
            return_value = None
            for line in lines:
                if hasattr(line, 'decode'):
                    # Note that lines returned can also be byte sequences so
                    # we have to handle decode here
                    line = line.decode('utf-8')
                line = line.strip()
                res_lines.append(line)
                self.log.info(line)
            result = self.cli.wait(self.container['Id'])
            if result['StatusCode'] != 0:
                res_lines = "\n".join(res_lines)
                raise AirflowException('docker container failed: ' + repr(
                    result) + f"lines {res_lines}")
            if self.retrieve_output and not return_value:
                return_value = self._attempt_to_retrieve_result()
            ret = None
            if self.retrieve_output:
                ret = return_value
            elif self.do_xcom_push:
                ret = self._get_return_value_from_logs(res_lines, line)
            return ret
        finally:
            if self.auto_remove:
                self.cli.remove_container(self.container['Id'])


class GraphGridMount(Mount):
    """Extend docker mount to be templatized"""
    template_fields = ('source')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
