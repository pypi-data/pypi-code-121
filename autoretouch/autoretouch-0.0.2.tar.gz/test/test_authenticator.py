import time
from unittest import TestCase
from assertpy import assert_that
import os
import signal

from autoretouch.api_client.client import AutoRetouchAPIClient
from test.api_config_dev import CONFIG_DEV

USER_AGENT = "Python-Unit-Test-0.0.1"


class TestAuthenticator(TestCase):

    test_org_id = "d92fe1cd-7166-4f5d-b43f-a100758d42c9"
    refresh_token = ""
    credentials_path = "../tmp/test-credentials.json"

    # @skip("For manual local testing only")
    def test_login(self):
        client = AutoRetouchAPIClient(
            organization_id=self.test_org_id,
            api_config=CONFIG_DEV,
            credentials_path=self.credentials_path,
            user_agent=USER_AGENT
        )
        client.login()
        os.environ["AR_REFRESH_TOKEN"] = client.auth.credentials.refresh_token

    @classmethod
    def setup(cls):
        # valid refresh token should be set in the environment
        cls.refresh_token = os.environ["AR_REFRESH_TOKEN"]
        if not cls.refresh_token:
            cls.test_login()
        # if os.path.isfile(cls.credentials_path):
        #     os.remove(cls.credentials_path)

    def test_new_instance_does_nothing_and_can_access_public_endpoint(self):
        client = AutoRetouchAPIClient(
            organization_id=self.test_org_id,
            api_config=CONFIG_DEV,
            credentials_path=self.credentials_path,
            user_agent=USER_AGENT
        )
        assert_that(client.auth.credentials).is_none()
        assert_that(os.path.isfile(self.credentials_path)).is_false()

        assert_that(client.get_api_status()).is_equal_to(200)

    def test_login_with_refresh_token(self):
        assert_that(self.refresh_token).is_not_empty()
        client = AutoRetouchAPIClient(
            organization_id=self.test_org_id,
            api_config=CONFIG_DEV,
            refresh_token=self.refresh_token,
            credentials_path=self.credentials_path,
            user_agent=USER_AGENT
        )
        # timeout after 1 second = make sure we're not waiting on a tab in the browser
        signal.alarm(1)
        client.login()
        # reset alarm so that no Exception is raised
        signal.alarm(0)

        assert_that(client.auth.credentials.expires_at).is_greater_than(time.time())
        assert_that(client.get_organizations()).is_not_empty()

    def test_should_persist_new_credentials(self):
        pass

    def test_should_refresh_expired_token(self):
        pass

    def test_revoke_authentication(self):
        credentials_path = "../tmp/other-credentials.json"
        client = AutoRetouchAPIClient(api_config=CONFIG_DEV, credentials_path=credentials_path, user_agent=USER_AGENT)

        under_test = client.auth

        assert_that(under_test.credentials.refresh_token).is_not_empty()
        assert_that(under_test.credentials.access_token).is_not_empty()

        assert_that(client.get_organizations()).is_not_empty()

        under_test.revoke_refresh_token()

        assert_that(client.get_organizations).raises(RuntimeError)

        os.remove(credentials_path)
