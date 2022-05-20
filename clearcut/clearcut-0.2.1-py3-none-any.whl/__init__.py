import logging
from typing import Tuple

from opentelemetry.trace import Tracer

from clearcut.logutils import log_block, get_logger
from clearcut.otlputils import get_tracer, context_from_carrier, set_attribute, spanner


def get_logger_tracer(name) -> Tuple[logging.Logger, Tracer]:
    return get_logger(name), get_tracer(name)
