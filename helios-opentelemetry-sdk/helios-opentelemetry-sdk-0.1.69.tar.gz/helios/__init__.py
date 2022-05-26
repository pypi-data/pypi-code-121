import os
from opentelemetry.propagators import textmap

from helios.base import HeliosBase, HeliosTags  # noqa: F401 (ignore lint error: imported but not used)
from helios.base.data_obfuscator import DataObfuscator, DataObfuscatorConfiguration, ExpectedValueType
from helios.base.tracing.suppress_tracing import SuppressTracing
from helios.helios import Helios
from helios.helios_test_trace import HeliosTestTrace
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from opentelemetry.util import types
from opentelemetry.propagate import inject, extract
from opentelemetry.context import get_current
from logging import getLogger

_LOG = getLogger(__name__)


def initialize(api_token: str,
               service_name: str,
               enabled: bool = False,
               collector_endpoint: Optional[str] = None,
               test_collector_endpoint: Optional[str] = None,
               sampling_ratio: Optional[Union[float, int, str]] = 1.0,
               environment: Optional[str] = None,
               resource_tags: Optional[Dict[str, Union[bool, float, int, str]]] = None,
               debug: Optional[bool] = False,
               max_queue_size: Optional[int] = None,
               data_obfuscation_allowlist: Optional[List[Union[str, Tuple[str, ExpectedValueType]]]] = None,
               data_obfuscation_hmac_key: Optional[str] = None,
               **kwargs) -> Helios:

    auto_init = kwargs.get('auto_init', False)
    if Helios.has_instance() and not auto_init and Helios.get_instance().auto_init:
        _LOG.warning('Helios already auto-initialized')
        return Helios.get_instance()

    data_obfuscation = None if data_obfuscation_hmac_key is None else DataObfuscatorConfiguration(
        allowlist=data_obfuscation_allowlist,
        hmac_key=data_obfuscation_hmac_key
    )
    return Helios.get_instance(
        api_token=api_token,
        service_name=service_name,
        enabled=enabled,
        collector_endpoint=collector_endpoint,
        test_collector_endpoint=test_collector_endpoint,
        sampling_ratio=sampling_ratio,
        environment=environment,
        resource_tags=resource_tags,
        max_queue_size=max_queue_size,
        debug=debug,
        data_obfuscation=data_obfuscation,
        **kwargs
    )


def auto_initialize(_):
    api_token = os.environ.get('HS_TOKEN')
    service_name = os.environ.get('HS_SERVICE_NAME')
    if api_token is None or service_name is None:
        _LOG.warning('HS_TOKEN and HS_SERVICE_NAME must be provided')
        return

    sampling_ratio = os.environ.get('HS_SAMPLING_RATIO')
    debug = os.environ.get('HS_DEBUG') in ['True', 'true']
    return initialize(api_token=api_token,
                      service_name=service_name,
                      enabled=True,
                      sampling_ratio=sampling_ratio,
                      debug=debug,
                      auto_init=True)


def create_custom_span(name: str,
                       attributes: types.Attributes = None,
                       wrapped_fn: Optional[Callable[[], any]] = None,
                       set_as_current_context: bool = False):
    if not Helios.has_instance():
        _LOG.debug('Cannot create custom span before initializing Helios')
        return

    hs = Helios.get_instance()
    return hs.create_custom_span(name, attributes, wrapped_fn, set_as_current_context)


def validate(spans, validations_callback, expected_number_of_spans=1):
    if len(spans) <= expected_number_of_spans:
        for s in spans:
            validations_callback(s)
    else:
        validated_spans_count = 0
        for s in spans:
            try:
                validations_callback(s)
                validated_spans_count += 1
            except AssertionError:
                continue
        assert validated_spans_count == expected_number_of_spans


def inject_current_context(carrier, setter: textmap.Setter = None):
    carrier = carrier if carrier is not None else {}
    current_context = get_current()
    if setter is not None:
        inject(carrier, context=current_context, setter=setter)
    else:
        inject(carrier, context=current_context)
    return carrier


def extract_context(carrier):
    carrier = carrier if carrier else {}
    context = extract(carrier)
    return context


def initialize_test(api_token=None):
    return HeliosTestTrace(api_token)


def obfuscate_data(key: str, msg: Any, length: Optional[int] = None) -> str:
    return DataObfuscator.hash(key, msg, length)


__all__ = [
    'initialize',
    'initialize_test',
    'extract_context',
    'inject_current_context',
    'validate',
    'create_custom_span',
    'auto_initialize',
    'SuppressTracing',
    'obfuscate_data',
]
