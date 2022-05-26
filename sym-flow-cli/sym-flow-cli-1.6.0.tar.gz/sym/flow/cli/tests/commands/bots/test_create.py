from unittest.mock import patch

import pytest

from sym.flow.cli.commands.users.create import prompt_for_identity
from sym.flow.cli.models.service_type import ServiceType
from sym.flow.cli.symflow import symflow as click_command
from sym.flow.cli.tests.factories.users import BotUserFactory, ServiceFactory


@patch("sym.flow.cli.helpers.api.SymAPI.update_users")
class TestBotsCreate:
    @pytest.fixture
    def bot_users(self):
        yield BotUserFactory.create_batch(3)

    @pytest.fixture(autouse=True)
    def patchypatch(self, bot_users):
        with patch("sym.flow.cli.helpers.api.SymAPI.get_users", return_value=bot_users):
            yield

    def test_create(self, mock_apply, click_setup):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["bots", "create", "hal"],
            )
            assert result.exit_code == 0

    def test_create_bot_with_existing_username(self, mock_apply, click_setup, bot_users):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["bots", "create", bot_users[0].sym_identifier],
            )
            assert (
                f"A bot already exists with username: {bot_users[0].sym_identifier}"
                in result.output
            )
