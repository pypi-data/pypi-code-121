from sym.flow.cli.helpers.config import store_login_config
from sym.flow.cli.symflow import symflow as click_command


def test_config_get_org(click_setup, test_org, auth_token):
    with click_setup() as runner:
        store_login_config("foo@bar.com", test_org, auth_token)
        result = runner.invoke(click_command, ["config", "get", "org"])

        assert result.stdout.strip() == test_org["slug"]
