import pytest
from unittest.mock import patch, MagicMock, call
import os
from nubium_utils.confluent_utils.consumer_utils import *
from nubium_utils.confluent_utils.consumer_utils import _wait_until_message_time
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from nubium_utils.test_utils import MockMessage
from datetime import datetime, timedelta
import time_machine
from pytz import timezone


def required_env_vars():
    return {
        "NU_LOGLEVEL": "DEBUG",
        "NU_HOSTNAME": "test-app-0",
        "NU_APP_NAME": "test_app",
        "NU_MP_PROJECT": "none",
        "NU_MP_CLUSTER": "none",
        "NU_DO_METRICS_PUSHING": "false",
        "NU_SCHEMA_REGISTRY_URL": "sr_url",
        "NU_SCHEMA_REGISTRY_USERNAME": "sr_un",
        "NU_SCHEMA_REGISTRY_PASSWORD": "sr_pw",
        "NU_TOPIC_CONFIGS_YAML": '{"test_topic_0": {"cluster": "cluster_0"}, "test_topic_1": {"cluster": "cluster_1"}}',
        "NU_KAFKA_CLUSTERS_CONFIGS_YAML": '{"cluster_0": {"url": "www", "username": "un", "password": "pw"}}',
        "NU_CONSUMER_POLL_TIMEOUT": "5",
        "NU_CONSUMER_TIMESTAMP_OFFSET_MINUTES": "1"
    }


def utcnow(seconds=0):
    return datetime(2022, 1, 21, 0, 1, tzinfo=timezone("Etc/UTC")) + timedelta(seconds=seconds)


@pytest.fixture(autouse=True)
def set_env_vars():
    evars = required_env_vars()
    env_patch = patch.dict('os.environ', evars)
    env_patch.start()
    env_vars._reload()


@pytest.fixture
def message(request):
    return MockMessage(**request.param)


@pytest.fixture
def consumer():
    return MagicMock()


@pytest.fixture
def monitor():
    return MagicMock()


class TestConsumerUtils:

    @pytest.mark.skip(reason="issues with time machine unit tests on anything but tim's machine. Otherwise works as expected.")
    @time_machine.travel(utcnow(seconds=-1), tick=False)
    def test__wait_until_message_time__sleep(self):
        assert _wait_until_message_time(1642741200000, '12345') == 'i sleep'

    @pytest.mark.skip(reason="issues with time machine unit tests on anything but tim's machine. Otherwise works as expected.")
    @time_machine.travel(utcnow(seconds=0), tick=False)
    def test__wait_until_message_time__nosleep(self):
        assert _wait_until_message_time(1642741200000, '12345') == 'real shit'

    @pytest.mark.parametrize('message', [{}], indirect=True)
    def test_poll_for_message(self, consumer, message):
        consumer.poll.side_effect = [message, None]
        assert message == poll_for_message(consumer)
        with pytest.raises(NoMessageError):
            poll_for_message(consumer)

    @pytest.mark.skip(reason="issues with time machine unit tests on anything but tim's machine. Otherwise works as expected.")
    @time_machine.travel(utcnow(), tick=False)
    @pytest.mark.parametrize('message', [{"headers": [("test_header_key", b"test_header_value"), ("guid", b"12345")]}], indirect=True)
    def test_handle_consumed_message(self, message, monitor):
        with patch('nubium_utils.confluent_utils.consumer_utils._wait_until_message_time') as wait_patch:
            handle_consumed_message(message)
            monitor.set_seconds_behind.assert_not_called()
            monitor.inc_messages_consumed.assert_not_called()

            handle_consumed_message(message, monitor)
            monitor.set_seconds_behind.assert_called_with(60)
            monitor.inc_messages_consumed.assert_called_with(1, message.topic())

    @pytest.mark.parametrize('message', [{"headers": [], "error": "object has no attribute 'headers'"}], indirect=True)
    def test_handle_consumed_message__missing_headers(self, message):
        with pytest.raises(ConsumeMessageError):
            handle_consumed_message(message)

    @pytest.mark.parametrize('message', [{"headers": [("test_header_key", b"test_header_value")]}], indirect=True)
    def test_handle_consumed_message__no_guid_field(self, message):
        with pytest.raises(ConsumeMessageError):
            handle_consumed_message(message)


if __name__ == '__main__':
    pytest.main([__file__])
