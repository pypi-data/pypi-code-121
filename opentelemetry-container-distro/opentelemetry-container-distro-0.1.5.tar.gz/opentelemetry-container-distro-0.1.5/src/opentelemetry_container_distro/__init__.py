import os
from typing import List, Optional
from unittest import mock

from opentelemetry.environment_variables import OTEL_TRACES_EXPORTER
from opentelemetry.instrumentation.distro import BaseDistro  # type: ignore
from opentelemetry.sdk._configuration import _OTelSDKConfigurator
from opentelemetry.sdk.resources import (
    Resource,
    ResourceDetector,
    get_aggregated_resources,
)
from opentelemetry_resourcedetector_docker import DockerResourceDetector
from opentelemetry_resourcedetector_kubernetes import (
    KubernetesDownwardAPIEnvironmentResourceDetector,
    KubernetesDownwardAPIVolumeResourceDetector,
)
from opentelemetry_resourcedetector_process import ProcessResourceDetector

# Generally speaking, the beahvior of the opentelemetry-distro (just a thin layer over
# opentelemetry-sdk) is what I want to preserve here.  The only realy shortcoming of
# the opentelemetry-sdk implementation is that it doesn't allow you to inject
# resource detectors, and it is hardwired to use a very plain `Resource.create` call,
# which will use the OTEL_RESOURCE_ATTRIBUTES and/or OTEL_SERVICE_NAME to provide a
# very minimal Resource.
#
# The approach here will be to use mock to temporarily replace Resource.create with
# our own function. Although this couples tightly to the opentelemetry-sdk
# implementation, it is minimally invasive and doesn't require reproducing large swaths
# of opentelemetry.sdk._configuration.  Hopefully in a future version I can send an
# upstream PR to opentelemetry-sdk that allows for pluggable resource detectors through
# entrypoints as well.


class OpenTelemetryContainerConfigurator(_OTelSDKConfigurator):
    def __init__(self, additional_detectors: Optional[List[ResourceDetector]] = None):
        self.resource_detectors = [
            DockerResourceDetector(),
            KubernetesDownwardAPIVolumeResourceDetector(),
            KubernetesDownwardAPIEnvironmentResourceDetector(),
            ProcessResourceDetector(),
        ]
        super().__init__()

    def _mocked_resource_create(self, auto_resource):
        return Resource.create(auto_resource).merge(self.resource)

    def _configure(self, **kwargs):
        self.resource = get_aggregated_resources(self.resource_detectors)
        with mock.patch(
            'opentelemetry.sdk._configuration.Resource', spec=Resource
        ) as MockedResource:
            MockedResource.create = self._mocked_resource_create
            return super()._configure(**kwargs)


class OpenTelemetryContainerDistro(BaseDistro):
    def _configure(self, **kwargs):
        os.environ.setdefault(OTEL_TRACES_EXPORTER, "otlp_proto_grpc")
