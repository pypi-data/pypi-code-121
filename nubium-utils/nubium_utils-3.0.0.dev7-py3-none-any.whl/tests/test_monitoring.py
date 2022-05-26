import unittest
from unittest import mock
import socket

from prometheus_client import CollectorRegistry

from nubium_utils.metrics import MetricsManager, MetricsPusher


class TestMonitor(unittest.TestCase):
    def setUp(self):
        self.metrics_manager = MetricsManager(
            job="test-job",
            app="test-app",
            registry=CollectorRegistry(),
            metrics_pusher=mock.MagicMock(),
        )

    def test_registry_is_intialized_when_created_without_registry_argument(self):
        assert self.metrics_manager.registry.__class__ == CollectorRegistry

    def test_gauges_are_created_with_specific_labels(self):
        assert self.metrics_manager.messages_consumed._labelnames == (
            "app",
            "job",
            "topic",
        )
        assert self.metrics_manager.message_errors._labelnames == (
            "app",
            "job",
            "exception",
        )
        assert self.metrics_manager.messages_produced._labelnames == (
            "app",
            "job",
            "topic",
        )
        assert self.metrics_manager.seconds_behind._labelnames == (
            "app",
            "job"
        )

    def test_utility_functions_set_specific_label_values_on_each_gauge(self):
        self.metrics_manager.set_seconds_behind(11)
        assert (
                self.metrics_manager.seconds_behind._metrics[
                    ("test-app", "test-job")
                ]._value._value
                == 11
        )

    def test_utility_functions_increment_specific_label_values_on_each_gauge(self):
        self.metrics_manager.inc_messages_consumed(1, "test-topic")
        assert (
            self.metrics_manager.messages_consumed._metrics[
                ("test-app", "test-job", "test-topic")
            ]._value._value
            == 1
        )

        self.metrics_manager.inc_messages_produced(1, "test-topic")
        assert (
            self.metrics_manager.messages_produced._metrics[
                ("test-app", "test-job", "test-topic")
            ]._value._value
            == 1
        )

    def test_increment_message_errors_increases_corresponding_exception_label(self):
        self.metrics_manager.inc_message_errors(ValueError("test-value-error"))
        assert (
            self.metrics_manager.message_errors._metrics[
                ("test-app", "test-job", "ValueError")
            ]._value._value
            == 1
        )

    def test_registered_custom_metrics_are_incrementable(self):
        self.metrics_manager.register_custom_metric("totally_legit", "See! It even has a legit description!")
        self.metrics_manager.inc_custom_metric("totally_legit")
        self.metrics_manager.inc_custom_metric("totally_legit", 7)
        assert (
            self.metrics_manager.custom_gauges["totally_legit"]._metrics[
                ("test-app", "test-job", "totally_legit")
            ]._value._value
            == 8
        )

    def test_unregistered_custom_metrics_raise_error(self):
        with self.assertRaisesRegex(ValueError, "hammer_time.*not registered") as exc:
            self.metrics_manager.inc_custom_metric("hammer_time")


class TestMetricsPusher(unittest.TestCase):
    """
    Tests for the class that manages pushing metrics to a metrics cache
    """

    def test_initialization(self):
        """
        Class should initialize with correct arguments
        """
        metrics_pusher = MetricsPusher(
            "test-job", "test-service-name", "test-service-port", "test-pod-port"
        )
        assert metrics_pusher is not None

    def test_set_gateways(self):
        """
        Set gateways returns 2 IP addresses when called with mocked values
        """

        metrics_pusher = MetricsPusher(
            "test-job", "test-service-name", "test-service-port", "test-pod-port"
        )

        # Mock out the socket.getaddrinfo call return value
        addrinfo_mock = [
            (
                socket.AddressFamily.AF_INET,
                socket.SocketKind.SOCK_DGRAM,
                17,
                "",
                ("127.0.0.1", 8080),
            ),
            (
                socket.AddressFamily.AF_INET,
                socket.SocketKind.SOCK_DGRAM,
                6,
                "",
                ("127.0.0.1", 8080),
            ),
            (
                socket.AddressFamily.AF_INET,
                socket.SocketKind.SOCK_DGRAM,
                17,
                "",
                ("127.0.0.2", 8080),
            ),
            (
                socket.AddressFamily.AF_INET,
                socket.SocketKind.SOCK_DGRAM,
                6,
                "",
                ("127.0.0.2", 8080),
            ),
        ]

        with mock.patch("nubium_utils.metrics.metrics_pusher.socket") as socket_patch:
            socket_patch.getaddrinfo.return_value = addrinfo_mock
            metrics_pusher.set_metrics_pod_ips()
            assert metrics_pusher.metrics_pod_ips == {
                "127.0.0.1:test-pod-port",
                "127.0.0.2:test-pod-port",
            }

    def test_push_metrics(self):
        """
        Assert that the push metrics function is called for every gateway
        """

        metrics_pusher = MetricsPusher(
            "test-job", "test-service-name", "test-service-port", "test-pod-port"
        )

        metrics_pusher.metrics_pod_ips = {
            "test-ip-address-1:test-port",
            "test-ip-address-2:test-port",
        }

        with mock.patch(
            "nubium_utils.metrics.metrics_pusher.push_to_gateway"
        ) as push_to_gateway_patch:
            registry = CollectorRegistry()
            metrics_pusher.push_metrics(registry)
            assert (
                unittest.mock.call(
                    "test-ip-address-1:test-port",
                    job="test-job",
                    registry=registry,
                    timeout=15,
                )
                in push_to_gateway_patch.call_args_list
            )
            assert (
                unittest.mock.call(
                    "test-ip-address-2:test-port",
                    job="test-job",
                    registry=registry,
                    timeout=15,
                )
                in push_to_gateway_patch.call_args_list
            )
