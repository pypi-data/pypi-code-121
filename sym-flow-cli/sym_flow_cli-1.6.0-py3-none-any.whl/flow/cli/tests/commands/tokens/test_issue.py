import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

from sym.flow.cli.commands.tokens.issue import to_timedelta
from sym.flow.cli.errors import InvalidExpiryError
from sym.flow.cli.symflow import symflow as click_command


class TestTokensIssue:
    @pytest.mark.parametrize(
        "expiry, expected_timedelta",
        [
            ("3s", timedelta(seconds=3)),
            ("30m", timedelta(minutes=30)),
            ("10d", timedelta(days=10)),
            ("1mo", timedelta(days=30)),
        ],
    )
    def test_to_timedelta(self, expiry, expected_timedelta):
        assert to_timedelta(MagicMock(), MagicMock(), expiry) == expected_timedelta

    @pytest.mark.parametrize(
        "expiry",
        [
            "0s",
            "03s",
            "not a number",
            "3y",
            "m",
        ],
    )
    def test_to_timedelta_invalid(self, expiry):
        with pytest.raises(InvalidExpiryError):
            to_timedelta(MagicMock(), MagicMock(), expiry)

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.create_token",
        return_value=str(uuid.uuid4()),
    )
    def test_issue_token(self, mock_api, click_setup):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["tokens", "issue", "--username", "bot-user", "--expiry", "3d"],
            )
            assert result.exit_code == 0

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.create_token",
        return_value=str(uuid.uuid4()),
    )
    def test_create_token_with_label(self, mock_api, click_setup):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                [
                    "tokens",
                    "issue",
                    "--username",
                    "bot-user",
                    "--expiry",
                    "3d",
                    "--label",
                    "a label",
                ],
            )
            assert result.exit_code == 0

    @patch(
        "sym.flow.cli.helpers.api.SymAPI.create_token",
        return_value=str(uuid.uuid4()),
    )
    def test_issue_token_short_options(self, mock_api, click_setup):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["tokens", "issue", "-u", "bot-user", "-e", "3d", "-l", "a label"],
            )
            assert result.exit_code == 0
