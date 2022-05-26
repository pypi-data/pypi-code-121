import uuid
from unittest.mock import patch

from sym.flow.cli.symflow import symflow as click_command


@patch(
    "sym.flow.cli.helpers.api.SymAPI.revoke_token",
)
class TestTokensRevoke:
    def test_revoke_token(self, mock_api, click_setup):
        with click_setup() as runner:
            result = runner.invoke(
                click_command,
                ["tokens", "revoke", str(uuid.uuid4())],
            )
            assert result.exit_code == 0
