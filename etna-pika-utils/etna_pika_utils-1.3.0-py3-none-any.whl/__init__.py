import ssl
from typing import Any, Dict

import pika


def _build_connection_parameters(
    *,
    credentials: pika.PlainCredentials,
    host: str,
    port: int,
    virtual_host: str = None,
    ssl_context: ssl.SSLContext = None,
) -> pika.ConnectionParameters:
    extra_params: Dict[str, Any] = {}

    # pika does not accept None as default argument, so we must not pass anything if the argument is not there
    if virtual_host is not None:
        extra_params["virtual_host"] = virtual_host
    if ssl_context is not None:
        extra_params["ssl_options"] = pika.SSLOptions(ssl_context)

    return pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        **extra_params,
    )


def build_connection_parameters(
    *,
    username: str,
    password: str,
    host: str,
    port: int,
    virtual_host: str = None,
    ssl_context: ssl.SSLContext = None,
) -> pika.ConnectionParameters:
    """
    Build the connection parameters for RabbitMQ

    :param username:                the username to use to connect to the RabbitMQ server
    :param password:                the password to use to connect to the RabbitMQ server
    :param host:                    the host to connect to
    :param port:                    the port to use when connecting
    :param virtual_host:            the virtual host to use (default is None)
    :param ssl_context:             the SSL context to use (default is None, to use no encryption)
    :return:                        the connection parameters
    """
    return _build_connection_parameters(
        credentials=pika.PlainCredentials(username, password),
        host=host,
        port=port,
        virtual_host=virtual_host,
        ssl_context=ssl_context,
    )


def build_connection_parameters_from_url(
    *,
    url: str,
    virtual_host: str = None,
    ssl_context: ssl.SSLContext = None,
) -> pika.ConnectionParameters:
    """
    Build the connection parameters for RabbitMQ from a URL

    :param url:                     the URL specifying connection parameters
    :param virtual_host:            the virtual host to use (default is None)
    :param ssl_context:             the SSL context to use (default is None, to use no encryption)
    :return:                        the connection parameters
    """
    url_params = pika.URLParameters(url)
    return _build_connection_parameters(
        credentials=url_params.credentials,
        host=url_params.host,
        port=url_params.port,
        virtual_host=virtual_host,
        ssl_context=ssl_context,
    )
