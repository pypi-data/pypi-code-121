"""
Class for pushing metrics to Prometheus metrics cache (pushgateway)
"""
import socket
import logging
from prometheus_client import push_to_gateway
from nubium_utils.general_runtime_vars import env_vars

LOGGER = logging.getLogger(__name__)


class MetricsPusher:
    """
    Pushes metrics to a prometheus pushgateway
    """

    def __init__(self,
                 job=None,
                 metrics_service_name=None,
                 metrics_service_port=None,
                 metrics_pod_port=None):
        """
        Initializes metrics pusher

        :param job: (str) Unique name of running application
        :param metrics_service_name: (str) host name of metrics service
        :param metrics_service_port: (sr) port of metrics service
        :param metrics_pod_port: (str) port for metrics cache on individual pod
        """

        if not job:
            job = env_vars()['NU_HOSTNAME']
        if not metrics_service_name:
            metrics_service_name = env_vars()['NU_METRICS_SERVICE_NAME']
        if not metrics_service_port:
            metrics_service_port = env_vars()['NU_METRICS_SERVICE_PORT']
        if not metrics_pod_port:
            metrics_pod_port = env_vars()['NU_METRICS_POD_PORT']

        self.job = job
        self.metrics_service_name = metrics_service_name
        self.metrics_service_port = metrics_service_port
        self.metrics_pod_port = metrics_pod_port

        self.metrics_pod_ips = None

    def set_metrics_pod_ips(self):
        """
        Queries metrics service for gateway IP addresses

        A single Kubernetes service redirects to multiple IP addresses for
        redundant Prometheus pushgateways.
        :return: None
        """
        socket_info_list = socket.getaddrinfo(
            self.metrics_service_name, self.metrics_service_port)
        self.metrics_pod_ips = {f'{result[-1][0]}:{self.metrics_pod_port}'
                                for result in socket_info_list}
        LOGGER.debug(f'Set gateway addresses: {self.metrics_pod_ips}')

    def push_metrics(self, registry):
        for gateway in self.metrics_pod_ips:
            try:
                push_to_gateway(gateway, job=self.job, registry=registry, timeout=15)
            except Exception as error:
                LOGGER.error(f'Failed to push to pushgateway {gateway}\n{error}')
