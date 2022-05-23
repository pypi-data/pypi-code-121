import os
from logging import getLogger
from typing import Callable, Dict, List, Optional, Union

from helios import DataObfuscatorConfiguration, HeliosBase, HeliosTags, version
from helios.instrumentation import default_instrumentation_list

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.util import types
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.trace import set_span_in_context
from opentelemetry.context import attach
from opentelemetry.instrumentation.propagators import set_global_response_propagator, TraceResponsePropagator

from helios.sampler import HeliosRatioBasedSampler

SAMPLING_RATIO_RESOURCE_ATTRIBUTE_NAME = 'telemetry.sdk.sampling_ratio'
_OPENTELEMETRY_SDK_VERSION = version.__version__

_LOG = getLogger(__name__)


class Helios(HeliosBase):
    HS_DISABLED_ENV_VAR = 'HS_DISABLED'

    __instance = None

    @staticmethod
    def init(
        api_token: str,
        service_name: str,
        enabled: bool = False,
        collector_endpoint: Optional[str] = None,
        test_collector_endpoint: Optional[str] = None,
        sampling_ratio: Optional[Union[float, int, str]] = 1.0,
        environment: Optional[str] = None,
        commit_hash: Optional[str] = None,
        max_queue_size: Optional[int] = None,
        resource_tags: Optional[Dict[str, Union[bool, float, int, str]]] = None,
        debug: Optional[bool] = False,
        data_obfuscation: Optional[DataObfuscatorConfiguration] = None,
        **kwargs
    ):

        if os.environ.get(Helios.HS_DISABLED_ENV_VAR) in ['True', 'true']:
            _LOG.warn(f'Helios instrumentation disabled by {Helios.HS_DISABLED_ENV_VAR} env var')
            return None

        if not enabled:
            _LOG.warn("Helios instrumentation disabled by 'enabled' initialization flag set to False")
            return None

        return Helios(
            api_token=api_token,
            service_name=service_name,
            collector_endpoint=collector_endpoint,
            test_collector_endpoint=test_collector_endpoint,
            sampling_ratio=sampling_ratio,
            environment=environment,
            commit_hash=commit_hash,
            max_queue_size=max_queue_size,
            resource_tags=resource_tags,
            debug=debug,
            data_obfuscation=data_obfuscation,
            **kwargs
        )

    @staticmethod
    def get_instance(*args, **kwargs):
        if Helios.__instance is None:
            Helios.__instance = Helios.init(*args, **kwargs)
        return Helios.__instance

    @staticmethod
    def has_instance() -> bool:
        return Helios.__instance is not None

    def init_tracer_provider(self) -> TracerProvider:
        if self.resource_tags:
            resource_tags = self.resource_tags.copy()
        else:
            resource_tags = dict()
        resource_tags.update({
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT:
                self.get_deployment_environment(),
            HeliosTags.ACCESS_TOKEN:
                self.api_token,
            ResourceAttributes.SERVICE_NAME:
                self.service_name,
            ResourceAttributes.SERVICE_VERSION:
                self.get_commit_hash(),
            ResourceAttributes.TELEMETRY_SDK_VERSION:
                _OPENTELEMETRY_SDK_VERSION,
            ResourceAttributes.TELEMETRY_SDK_NAME:
                'helios-opentelemetry-sdk',
            SAMPLING_RATIO_RESOURCE_ATTRIBUTE_NAME:
                self.sampling_ratio
        })

        set_global_response_propagator(TraceResponsePropagator())

        return TracerProvider(
            id_generator=self.id_generator,
            sampler=self.get_sampler(),
            resource=Resource.create(resource_tags),
        )

    def get_deployment_environment(self) -> str:
        if self.environment:
            return self.environment

        environment = None
        if os.environ.get('CI'):
            environment = self.get_ci_environment()

        if os.environ.get('JENKINS_URL'):
            environment = 'Jenkins'

        if not environment and self.resource_tags:
            environment = \
                self.resource_tags.get(
                    ResourceAttributes.DEPLOYMENT_ENVIRONMENT)

        return environment or os.environ.get('HS_ENVIRONMENT', os.environ.get('DEPLOYMENT_ENV', ''))

    def get_ci_environment(self) -> str:
        if os.environ.get('GITHUB_ACTIONS'):
            return 'Github Actions'

        if os.environ.get('BITBUCKET_BUILD_NUMBER'):
            return 'Bitbucket Pipeline'

        if os.environ.get('TRAVIS'):
            return 'Travis CI'

        if os.environ.get('GITLAB_CI'):
            return 'Gitlab Pipeline'

        if os.environ.get('CIRCLECI'):
            return 'CircleCI'

        if os.environ.get('DRONE'):
            return 'Drone'

        return None

    def get_commit_hash(self) -> str:

        if self.commit_hash:
            return self.commit_hash

        commit_hash = None
        if os.environ.get('CI'):
            commit_hash = self.get_ci_commit_hash()

        if not commit_hash and self.resource_tags:
            commit_hash = \
                self.resource_tags.get(
                    ResourceAttributes.SERVICE_VERSION)

        return commit_hash or os.environ.get('COMMIT_HASH', '')

    def get_ci_commit_hash(self):
        if os.environ.get('GITHUB_ACTIONS'):
            return os.environ.get('GITHUB_SHA')

        if os.environ.get('BITBUCKET_BUILD_NUMBER'):
            return os.environ.get('BITBUCKET_COMMIT')

        if os.environ.get('TRAVIS'):
            return os.environ.get('TRAVIS_COMMIT')

        if os.environ.get('GITLAB_CI'):
            return os.environ.get('CI_COMMIT_SHA')

        if os.environ.get('CIRCLECI'):
            return os.environ.get('CIRCLE_SHA1')

        if os.environ.get('DRONE'):
            return os.environ.get('DRONE_COMMIT_SHA')

        return None

    def get_sampler(self):
        if self.custom_sampler:
            return self.custom_sampler

        ratio = self.sampling_ratio if self.sampling_ratio is not None else 1.0

        return HeliosRatioBasedSampler(ratio)

    def create_custom_span(self,
                           name: str,
                           attributes: types.Attributes = None,
                           wrapped_fn: Optional[Callable[[], any]] = None,
                           set_as_current_context: bool = False):
        tracer = self.tracer_provider.get_tracer('helios')
        new_context = None
        result = None
        with tracer.start_as_current_span(name, attributes=attributes) as custom_span:
            custom_span.set_attribute('hs-custom-span', 'true')
            if set_as_current_context:
                new_context = set_span_in_context(custom_span)

            if wrapped_fn is None:
                custom_span.end()
            else:
                try:
                    result = wrapped_fn()
                except Exception as e:
                    custom_span.set_status(Status(status_code=StatusCode.ERROR, description=str(e)))
                    custom_span.record_exception(e)
                    raise e
                finally:
                    custom_span.end()

        attach(new_context) if new_context else None
        return result

    def get_instrumentations(self) -> List[BaseInstrumentor]:
        return default_instrumentation_list
