import logging
import sys
from logstash_formatter import LogstashFormatterV1


def log_setup(logfile=None):

    if logfile is not None:
        handler = logging.handlers.RotatingFileHandler(
            logfile, maxBytes=10 * 1000 * 1000, encoding="utf-8"
        )
    else:
        handler = logging.StreamHandler(stream=sys.stdout)

    handler.setFormatter(LogstashFormatterV1())
    logging.basicConfig(handlers=[handler], level=logging.DEBUG)

    # Disable some handlers
    for name in [
        "kazoo.client",
        "pykafka.simpleconsumer",
        "pykafka.handlers",
        "pykafka.balancedconsumer",
        "pykafka.connection",
        "pykafka.membershipprotocol",
        "pykafka.cluster",
        "pykafka.topic",
        "py4j.java_gateway",
    ]:
        logging.getLogger(name).disabled = True
