from otel_extensions import (
    TelemetryOptions,
    init_telemetry_provider,
    flush_telemetry_data,
)
from contextlib import contextmanager
import os
import tempfile
import logging

telemetry_initialized = False

SERVICE_NAME = "UTF-Queue-Client-CLI"

SILABS_NET_CA = """
-----BEGIN CERTIFICATE-----
MIIDMjCCAhqgAwIBAgIUDGFjXuAmh2l8HHbGrbQcyurWMRowDQYJKoZIhvcNAQEL
BQAwFTETMBEGA1UEAxMKc2lsYWJzLm5ldDAeFw0yMDA1MjkyMDQyNDBaFw0zMDA1
MjcyMDQzMDlaMBUxEzARBgNVBAMTCnNpbGFicy5uZXQwggEiMA0GCSqGSIb3DQEB
AQUAA4IBDwAwggEKAoIBAQDqdttEFsMBoz1eemC5Sk/1GuDGRtW7WPE1mUBVAqQV
n+2cKXOMUjsNlYWBeDez6iVrgdRf1d68IybiR7wsw7LENeBUemFUzcecr8E3sc+G
0hHJQIkl6H6msLQ4z9l2e8lv4tnJ5IumN6iyI6nB6sV3u6hn90R0HNOR1KWV7QZT
83DrRF/GACDw9Es37lGzFhHE0Ja7woSeM7aKrtM6jmCk17RX1m9QNNCXTtEB15DR
fLFd0Tv2rlWpBfo6T/w7FtMgictIEhhGf5vdTxZ+r0RFJFIgE7JiMVNBFix94GQT
TaV21axWhmWZjeOQ9AGi5jknDoqK/iJJ0dInyt6NieyTAgMBAAGjejB4MA4GA1Ud
DwEB/wQEAwIBBjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBSSND8TQ6IRgHJo
xqvhfdBD66fw8jAfBgNVHSMEGDAWgBSSND8TQ6IRgHJoxqvhfdBD66fw8jAVBgNV
HREEDjAMggpzaWxhYnMubmV0MA0GCSqGSIb3DQEBCwUAA4IBAQBvxRyKhEwd9wqi
M6yrCaYeyy0mW1LJfVRJlTMT4/2NHUcZHKDfETwiuFSNa06HIk0TlH52U4n/liSE
7nzeWrvq0WNKWqKT7LzHTR4Gb1nUJVtwFl9Gyipb5fum2vhbEPxCb7uCCglFAM5v
8fNOxw7U/YPczKdoOhtg8rdzW+iFfD/aN4vtAinSke73DcMvaB7Vwun+J69THQb7
kjFq6FbvO1QSiNqT5RHHXZfiA5/0LW2txue47iIgWIsEWAYi1VFV5tiD2FkO3H3E
C3mfuIr4wTAmgihcu5ZVpV+IY2kyYFISzwkp27DexBJ0bngL6W+nQp74XJjmiAcR
XBhoBcSg
-----END CERTIFICATE-----
"""

DEFAULT_SILABS_NET_CA_CERT_FILE = "/usr/local/share/ca-certificates/vault-ca-prod.crt"


def get_or_make_ca_file() -> str:
    if os.path.isfile(DEFAULT_SILABS_NET_CA_CERT_FILE):
        return DEFAULT_SILABS_NET_CA_CERT_FILE
    temp_dir = tempfile.gettempdir()
    ca_file_name = "silabs-net-ca.crt"
    ca_file_path = os.path.join(temp_dir, ca_file_name)
    if not os.path.isfile(ca_file_path):
        with open(ca_file_path, "w") as f:
            f.write(SILABS_NET_CA)
    return ca_file_path


@contextmanager
def setup_telemetry():
    logging.getLogger("opentelemetry.util._time").setLevel(logging.ERROR)
    global telemetry_initialized
    if not telemetry_initialized:
        if os.environ.get("OTEL_EXPORTER_OTLP_CERTIFICATE") is None:
            os.environ["OTEL_EXPORTER_OTLP_CERTIFICATE"] = get_or_make_ca_file()
        options = TelemetryOptions(
            OTEL_SERVICE_NAME=SERVICE_NAME,
            OTEL_EXPORTER_OTLP_ENDPOINT=os.environ.get(
                "OTEL_EXPORTER_OTLP_ENDPOINT",
                "https://otel-collector-http.silabs.net",
            ),
            OTEL_EXPORTER_OTLP_PROTOCOL=os.environ.get(
                "OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf"
            ),
        )
        init_telemetry_provider(options)
        telemetry_initialized = True
    yield
    flush_telemetry_data()
