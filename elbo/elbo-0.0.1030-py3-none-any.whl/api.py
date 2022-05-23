import base64
import json

from elbo.connector import ElboConnector
from elbo.resources import ElboResources


class ElboRestApi:
    def __init__(self):
        self._elbo_connector = ElboConnector()

    def request_machine_create(self):
        """
        Request the receiver to run the task.
        :return: None
        """
        params = {}
        response = self._elbo_connector.request(
            ElboResources.CREATE_ENDPOINT, params=params
        )
        return response

    def provision_machine_create_compute(self, compute_type, session_id, open_ports, sources_path=None):
        """
        Request to provision the chosen to compute type.
        """
        params = {
            "chosen_compute_type": base64.b64encode(
                bytes(json.dumps(compute_type), "utf-8")
            ),
            "session_id": session_id,
            "open_ports": open_ports,
            "sources_path": sources_path
        }

        response = self._elbo_connector.request(
            ElboResources.CREATE_ENDPOINT, params=params
        )
        return response

    def provision_compute(
        self, compute_type, session_id, task_config, config_file_path
    ):
        """
        Request to provision the chosen to compute type.

        :param task_config: The task config
        :param config_file_path: The config file path
        :param compute_type: To compute type
        :param session_id: The session id
        :return:
        """
        params = {
            "chosen_compute_type": base64.b64encode(
                bytes(json.dumps(compute_type), "utf-8")
            ),
            "session_id": session_id,
            "config_file_path": config_file_path,
            "task_config": base64.b64encode(bytes(json.dumps(task_config), "utf-8")),
        }

        response = self._elbo_connector.request(
            ElboResources.PROVISION_ENDPOINT, params=params
        )
        return response
