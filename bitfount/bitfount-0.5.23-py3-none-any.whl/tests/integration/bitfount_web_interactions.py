"""Provides methods for interacting with the Bitfount Web frontend via Selenium."""
from contextlib import contextmanager
import logging
from pathlib import Path
import threading
import time
from typing import Generator

import chromedriver_autoinstaller
from requests import HTTPError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bitfount.hub.api import _STAGING_AM_URL, BitfountAM, BitfountSession
from bitfount.hub.authentication_flow import (
    _HUB_API_IDENTIFIER,
    _SCOPES,
    _STAGING_AUTH_DOMAIN,
    _STAGING_CLIENT_ID,
)

SCREENSHOT_DIRECTORY: Path = Path("selenium-screenshots")
IMPLICIT_WAIT_TIME = 8  # seconds; high value due to slow GitHub runner

logger = logging.getLogger(__name__)


@contextmanager
def webdriver_factory(
    wait_time: int = IMPLICIT_WAIT_TIME,
) -> Generator[WebDriver, None, None]:
    """Create a Selenium webdriver instance."""
    chromedriver_autoinstaller.install()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.implicitly_wait(wait_time)
        yield driver


def save_screenshot(file_name: str, driver: WebDriver) -> None:
    """Saves a screenshot of the Selenium driver view."""
    SCREENSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    file_path = SCREENSHOT_DIRECTORY / f"{file_name}_{str(int(time.time()))}.png"
    file_path = file_path.resolve()
    driver.get_screenshot_as_file(str(file_path))


def _oauth_sign_in(username: str, password: str, driver: WebDriver) -> None:
    """Sign in to the oauth form using the supplied username and password."""
    try:
        # Supply login details to Auth0 login panel
        driver.find_element_by_css_selector("input[name='username']").send_keys(
            username
        )
        driver.find_element_by_css_selector("input[name='password']").send_keys(
            password
        )
        driver.find_element_by_css_selector("button[name='action']").click()
    except Exception as e:
        logger.error("Exception encountered whilst signing in.")
        save_screenshot("perform_login", driver)
        raise e


class WebdriverBitfountSession(BitfountSession):
    """A BitfountSession implementation using Selenium Webdriver.

    An implementation of BitfountSession which uses a Selenium Webdriver to approve
    the session access.
    """

    def __init__(
        self,
        username: str,
        password: str,
        # Below are the inherited args
        user_storage_path: Path,
        auth_domain: str = _STAGING_AUTH_DOMAIN,
        client_id: str = _STAGING_CLIENT_ID,
        scopes: str = _SCOPES,
        audience: str = _HUB_API_IDENTIFIER,
    ):
        super(WebdriverBitfountSession, self).__init__(
            user_storage_path=user_storage_path,
            auth_domain=auth_domain,
            client_id=client_id,
            scopes=scopes,
            audience=audience,
        )
        self._username = username
        self.password = password

    def _do_verification(self, user_code: str, verification_uri: str) -> None:
        """Opens web browser for verification."""
        with webdriver_factory() as driver:
            try:
                # Load Auth0 location
                driver.get(verification_uri)

                # Extract code
                secure_code_field = driver.find_element_by_css_selector(
                    "input[aria-label='Secure code']"
                )
                secure_code = secure_code_field.get_attribute("value")
                if secure_code != user_code:
                    raise ValueError(
                        f"Secure codes differ: {user_code} != {secure_code}"
                    )

                # If code ok, click button
                driver.find_element_by_css_selector("button[value='confirm']").click()
                # Perform login
                _oauth_sign_in(self._username, self.password, driver)
                # Wait for page to load
                driver.find_element_by_xpath(
                    "//p[text()='Your device is now connected.']"
                )
            except Exception as e:
                logger.error(
                    f"Exception encountered whilst attempting to perform oauth "
                    f"verification at {verification_uri}."
                )
                save_screenshot("do_verification", driver)
                raise e


class ExtendedBitfountAM(BitfountAM):
    """Extends BitfountAM with methods relevant to testing."""

    def __init__(self, session: WebdriverBitfountSession, access_manager_url: str):
        super().__init__(session, access_manager_url)

    def grant_proactive_access(
        self, pod_id: str, user_to_grant: str, role: str
    ) -> None:
        """Sets a pod to grant proactive access to the username specified."""
        response = self.session.post(
            f"{self.access_manager_url}/api/casbin",
            timeout=10,
            json={
                "podIdentifier": pod_id,
                "grantee": user_to_grant,
                "role": role,
            },
        )

        if response.status_code not in (200, 201):
            raise HTTPError(
                f"Unexpected response ({response.status_code}): {response.text}"
            )


def get_bitfount_session(
    username: str, password: str, token_dir: Path
) -> WebdriverBitfountSession:
    """Creates and returns a WebdriverBitfountSession."""
    return WebdriverBitfountSession(
        username=username,
        user_storage_path=token_dir / username,
        password=password,
    )


def oidc_flow(
    url: str,
    username: str,
    password: str,
) -> None:
    """Opens provided oidc url and logs in before closing browser.

    This is run in a separate thread so that the Modeller can respond to the challenges
    from the pods. Otherwise this ends up blocking the Modeller.

    Args:
        url (str): the oidc authentication url to open. This is provided at run-time.
        username (str): the username of the user to log in as
        password (str): the password of the user
    """

    def execute_oidc_flow() -> None:
        with webdriver_factory() as driver:
            try:
                logger.warning("opening url in browser")
                driver.get(url)

                # Wait for a maximum of 30 seconds for the OIDC Confirmation to appear
                # The webdriver won't wait for the full 30 seconds if the element is
                # located before this time.
                WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//button[@value="confirm"]')
                    )
                )
                driver.find_element_by_css_selector("button[value='confirm']").click()

                _oauth_sign_in(username, password, driver)

                # Wait for a maximum of 30 seconds for the device to connect
                WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//p[text()='Your device is now connected.']")
                    )
                )

            except Exception as e:
                logger.error(
                    f"Exception encountered whilst attempting to perform oidc auth "
                    f"verification at {url}."
                )
                save_screenshot("do_oidc_verification", driver)
                raise e

    oidc_thread = threading.Thread(target=execute_oidc_flow, name="oidc")
    oidc_thread.start()


def grant_proactive_access(
    modeller_username: str,
    pod_id: str,
    role: str,
    pod_session: WebdriverBitfountSession,
) -> None:
    """Grants proactive access to a pod for a given modeller."""
    am = ExtendedBitfountAM(pod_session, _STAGING_AM_URL)
    am.grant_proactive_access(
        pod_id=pod_id,
        user_to_grant=modeller_username,
        role=role,
    )
