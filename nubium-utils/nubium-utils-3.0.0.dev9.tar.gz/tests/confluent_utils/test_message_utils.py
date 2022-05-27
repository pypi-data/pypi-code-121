import pytest
from unittest.mock import patch, MagicMock, call
import os
from nubium_utils.confluent_utils.confluent_runtime_vars import env_vars
from nubium_utils.confluent_utils.message_utils import *


class TestMessageUtils:
    def test_handle_no_messages(self):
        with patch('nubium_utils.confluent_utils.message_utils.confirm_produce') as confirm:
            handle_no_messages()
            confirm.assert_not_called()

            producers = MagicMock()
            handle_no_messages(producers=producers)
            confirm.assert_called_with(producers)

    def test_shutdown_cleanup(self):
        with patch('nubium_utils.confluent_utils.message_utils.confirm_produce') as confirm:
            consumer = MagicMock()
            producers = MagicMock()
            shutdown_cleanup(producers=producers, consumer=consumer)

            consumer.close.assert_called()
            confirm.assert_called_with(producers, timeout=30)


if __name__ == '__main__':
    pytest.main([__file__])
