# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.configuration import AgentConfig
from contrast.reporting import teamserver_messages, reporting_client
from contrast.utils.loggers import logger


def validate_config():
    try:
        exit_status = _validate()
        sys.exit(exit_status)
    except Exception as e:
        _log("Unexpected error while validating agent config:")
        _log(f"{e!r}")
        _log("Unable to validate agent config")
        sys.exit(1)


def _log(msg):
    print(f"[contrast-validate-config] {msg}")


def _validate():
    """
    Validates the config and returns an appropriate exit status
    """
    _log("Validating Contrast configuration")
    _log("You may see agent logs in structured log format")

    logger.setup_basic_agent_logger()

    if not _check_config():
        return 1

    if not _check_connection():
        return 1

    return 0


def _valid_proxy(config):
    """
    If proxy use is enabled, verify the proxy url is provided.
    """
    enabled = config.get("api.proxy.enable")
    if not enabled:
        # If proxy isn't enabled then it's "valid"
        _log("Proxy use disabled")
        return True

    url = config.get("api.proxy.url")
    if url:
        # Just check that's a populated string, not that it's a url
        _log("Proxy use enabled")
        return True

    _log("Proxy enabled but no proxy url provided")
    return False


def _valid_cert(config):
    """
    If certificate use is enabled, verify that the three required files are present.
    """
    enabled = config.get("api.certificate.enable")
    if not enabled:
        # If certificate use isn't enabled then it's "valid"
        _log("Certificate use disabled")
        return True

    ca_file = config.get("api.certificate.ca_file")
    if not ca_file:
        _log("CA file path not provided")
        return False

    cert_file = config.get("api.certificate.cert_file")
    if not cert_file:
        _log("Cert file path not provided")
        return False

    key_file = config.get("api.certificate.key_file")
    if not key_file:
        _log("Key file path not provided")
        return False

    _log("Certificate use enabled")
    return True


def _check_config():
    _log("Loading config")

    config = AgentConfig()
    config.is_service_bypassed = True

    _log("Config loaded successfully")

    _log("Checking API configuration")

    missing_values = config.check_for_api_config()
    if missing_values:
        for missing_value in missing_values:
            _log(f"Missing required config value: {missing_value}")
        return False

    if not _valid_proxy(config) or not _valid_cert(config):
        return False

    return True


def _check_connection():
    client = reporting_client.ReportingClient()
    msg = teamserver_messages.ServerActivity()

    _log("Sending test request to Contrast UI")

    resp = client.send_message(msg)

    if resp is None:
        _log("Request failed")
        _log("Unable to establish a connection with current configuration")
        return False

    _log(f"Response: {resp.status_code} {resp.reason}")
    if resp.text:
        _log(resp.text)

    # note: status code 400 for ServerActicity just means the server doesn't exist
    # it still indicates a successful connection to teamserver
    # TODO: PYT-2080 Use ServerCreate instead

    if resp.status_code == 401:
        _log("You are connecting to the Contrast UI but have improper authorization")
        return False

    if resp.status_code > 401:
        _log("You are connecting to the Contrast UI but are seeing an unexpected error")
        return False

    _log(f"{resp.status_code} status code indicates success for this endpoint")
    _log("Connection to the Contrast UI successful")
    return True
