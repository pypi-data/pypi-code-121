import logging
import time
from typing import Any

import requests
from jsonrpcclient import Error, Ok, parse, request_hex
from prometheus_client import Gauge, Info, start_http_server

from . import __version__
from .config import settings

logging.basicConfig(level=settings.get("LOG_LEVEL", default="INFO"))


class RouterMetrics:

    # Setting up Prometheus metrics to collect
    sinr = Gauge("sinr", "Signal to Noise Ratio (dB)")
    rssi = Gauge("rssi", "Received Signal Strength Indicator (dB)")
    rsrp = Gauge("rsrp", "Reference Symbol Received Power (dBm)")
    rsrq = Gauge("rsrq", "Reference Signal Received Quality (dB)")
    signal_strength = Gauge("signal_strength", "Mobile Signal Strength")
    connected_devices = Gauge(
        "connected_devices", "Number of connected devices on WiFi"
    )
    connection_time = Gauge("connection_time", "Current Connection Time (s)")
    network_info = Info("network_info", "Network connection information")
    total_upload_this_month = Gauge(
        "total_upload_this_month", "Total uploaded data this month (bytes)"
    )
    total_download_this_month = Gauge(
        "total_download_this_month", "Total downloaded data this month (bytes)"
    )
    total_transfer_this_month = Gauge(
        "total_transfer_this_month",
        "Total transferred data this month (bytes)",
    )
    linkhub_up = Gauge(
        "linkhub_up",
        "Marker whether or not the LinkHub scrape has worked (yes=1, no=0)",
    )

    def __init__(
        self,
        request_key: str,
        box_addr: str = "192.168.1.1",
        polling_interval_seconds: int = 5,
    ):
        logging.info("Setting up exporter.")
        self.request_key = request_key
        self.box_addr = box_addr
        self.url = f"http://{self.box_addr}/jrd/webapi"
        self.polling_interval_seconds = polling_interval_seconds
        self.timeout = self.polling_interval_seconds
        self.headers = {
            "_TclRequestVerificationKey": self.request_key,
            "Referer": f"http://{self.box_addr}/index.html",
        }

    def run_metrics_loop(self) -> None:
        """Metrics fetching loop"""

        while True:
            logging.debug("Fetching metrics.")
            self.fetch_metrics()
            time.sleep(self.polling_interval_seconds)

    def _box_api_request(self, method: str) -> dict[str, Any]:
        response = requests.post(
            self.url,
            json=request_hex(method),
            headers=self.headers,
            timeout=self.timeout,
        )
        logging.debug("Method: %s; response: %s", method, response.json())
        match parse(response.json()):
            case Ok(result, _):
                return result
            case Error(_, message, _, _):
                logging.error(
                    "API error: method: %s; message: %s", method, message
                )
                raise RuntimeError(message)
            case _:
                raise AssertionError("Impossible parsed response received.")

    def _read_network_info(self) -> None:
        """Requesting, parsing, and updating network info metrics."""
        results = self._box_api_request("GetNetworkInfo")
        logging.debug("Network info: %s", results)

        # Set Prometheus metrics
        if value := results.get("SINR"):
            self.sinr.set(value)
        if value := results.get("RSSI"):
            self.rssi.set(value)
        if value := results.get("RSRP"):
            self.rsrp.set(value)
        if value := results.get("RSRQ"):
            self.rsrq.set(value)
        if value := results.get("SignalStrength"):
            self.signal_strength.set(value)
        if (network_name := results.get("NetworkName")) and (
            cell_id := results.get("CellId")
        ):
            self.network_info.info(
                {
                    "network_name": network_name,
                    "cell_id": cell_id,
                }
            )

    def _read_system_status(self) -> None:
        """Requesting, parsing, and updating system status metrics."""
        results = self._box_api_request("GetSystemStatus")
        logging.debug("System status: %s", results)

        # Set Prometheus metrics
        if value := results.get("TotalConnNum"):
            self.connected_devices.set(value)

    def _read_usage_record(self) -> None:
        """Requesting, parsing, and updating usage record metrics."""
        results = self._box_api_request("GetUsageRecord")
        logging.debug("Usage record: %s", results)

        # Set Prometheus metrics
        if value := results.get("CurrConnTimes"):
            self.connection_time.set(value)
        if value := results.get("HCurrUseUL"):
            self.total_upload_this_month.set(value)
        if value := results.get("HCurrUseDL"):
            self.total_download_this_month.set(value)
        if value := results.get("HUseData"):
            self.total_transfer_this_month.set(value)

    def fetch_metrics(self) -> None:
        """Fetch all relevant metrics."""
        try:
            self._read_network_info()
            self._read_system_status()
            self._read_usage_record()
            self.linkhub_up.set(1)
        except:  # noqa: E722
            # TODO: This is not really working here yet,
            # since we are crashing right after
            self.linkhub_up.set(0)
            raise


def main() -> None:
    """Main entry point for the exporter"""
    logging.info("Linkhub Prometheus Exporter, version %s", __version__)
    # Add exporter metadata to what's exported
    exporter_info = Info("exporter_info", "Exporter information")
    exporter_info.info(
        {
            "version": __version__,
        }
    )

    try:
        router_metrics = RouterMetrics(
            request_key=settings.REQUEST_KEY,
            box_addr=settings.BOX_ADDRESS,
            polling_interval_seconds=settings.POLLING_INTERVAL_SECONDS,
        )
    except AttributeError as exc:
        # Every other setting besides REQUEST_KEY has defaults
        logging.error("Missing REQUEST_KEY configuration.")
        raise RuntimeError("Missing REQUEST_KEY configuration.") from exc

    logging.info(
        "Server starting on http://%s:%d",
        settings.EXPORTER_ADDRESS,
        settings.EXPORTER_PORT,
    )
    start_http_server(
        port=settings.EXPORTER_PORT, addr=settings.EXPORTER_ADDRESS
    )
    router_metrics.run_metrics_loop()


if __name__ == "__main__":
    main()
