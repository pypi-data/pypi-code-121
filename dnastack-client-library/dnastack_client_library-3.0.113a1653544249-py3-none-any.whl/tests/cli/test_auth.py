import requests
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from traceback import print_exc

import re
from subprocess import Popen, PIPE
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from dnastack.common.environments import env, flag
from .base import CliTestCase
from ..exam_helper import client_id, client_secret, token_endpoint, authorization_endpoint, personal_access_endpoint, \
    redirect_url, device_code_endpoint


class TestAuthentication(CliTestCase):
    re_url = re.compile(r'https://[^\s]+/authorize\?user_code=[^\s]+')
    test_resource_id = 'test-data-connect'
    test_resource_url = env('E2E_PROTECTED_DATA_CONNECT_URL',
                            default='https://collection-service.viral.ai/data-connect/')

    def setUp(self) -> None:
        super().setUp()
        self.invoke('endpoints', 'add', '-t', 'data_connect', self.test_resource_id)
        self.invoke('endpoints', 'set', self.test_resource_id, 'url', self.test_resource_url)

    def test_client_credentials_flow(self):

        self._configure_endpoint(
            self.test_resource_id,
            {
                'authentication.client_id': client_id,
                'authentication.client_secret': client_secret,
                'authentication.grant_type': 'client_credentials',
                'authentication.resource_url': self.test_resource_url,
                'authentication.token_endpoint': token_endpoint,
            }
        )

        result = self.invoke('auth', 'login')
        self.assertEqual(0, result.exit_code, 'Logging into all endpoints should also work.')

        result = self.invoke('auth', 'login', '--endpoint-id', self.test_resource_id)
        self.assertEqual(0, result.exit_code, 'The login command with a single endpoint should also work.')

    def test_personal_access_token_flow(self):
        if flag('E2E_WEBDRIVER_TESTS_DISABLED'):
            self.skipTest('All webdriver-related tests as disabled with E2E_WEBDRIVER_TESTS_DISABLED.')

        email = env('E2E_AUTH_PAT_TEST_EMAIL')
        token = env('E2E_AUTH_PAT_TEST_TOKEN')

        if not email or not token:
            self.skipTest('The PAT flow test does not have both email (E2E_AUTH_PAT_TEST_EMAIL) and personal access '
                          'token (E2E_AUTH_PAT_TEST_TOKEN).')

        self._configure_endpoint(
            self.test_resource_id,
            {
                'authentication.authorization_endpoint': authorization_endpoint,
                'authentication.client_id': client_id,
                'authentication.client_secret': client_secret,
                'authentication.grant_type': 'authorization_code',
                'authentication.personal_access_endpoint': personal_access_endpoint,
                'authentication.personal_access_email': email,
                'authentication.personal_access_token': token,
                'authentication.redirect_url': redirect_url,
                'authentication.resource_url': self.test_resource_url,
                'authentication.token_endpoint': token_endpoint
            }
        )

        result = self.invoke('auth', 'login', '--endpoint-id', self.test_resource_id)
        self.assertEqual(0, result.exit_code)

    def test_device_code_flow(self):
        if flag('E2E_WEBDRIVER_TESTS_DISABLED'):
            self.skipTest('All webdriver-related tests as disabled with E2E_WEBDRIVER_TESTS_DISABLED.')

        email = env('E2E_AUTH_DEVICE_CODE_TEST_EMAIL')
        token = env('E2E_AUTH_DEVICE_CODE_TEST_TOKEN')

        if not email or not token:
            self.skipTest('This device-code test requires both email (E2E_AUTH_DEVICE_CODE_TEST_EMAIL) and personal '
                          'access token (E2E_AUTH_DEVICE_CODE_TEST_TOKEN).')

        self._configure_endpoint(
            self.test_resource_id,
            {
                'authentication.client_id': client_id,
                'authentication.device_code_endpoint': device_code_endpoint,
                'authentication.grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                'authentication.redirect_url': redirect_url,
                'authentication.resource_url': self.test_resource_url,
                'authentication.token_endpoint': token_endpoint
            }
        )

        self._logger.debug('Initiating the auth command in a different process...')

        auth_cmd = ['python3', '-m', 'dnastack', 'auth', 'login']
        p = Popen(auth_cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        device_code_url = None
        while device_code_url is None:
            exit_code = p.poll()
            if exit_code is not None:
                self._logger.error(f'CLI: EXIT: {exit_code}')
                self._logger.error(f'CLI: STDOUT: {p.stdout.read()}')
                self._logger.error(f'CLI: STDERR: {p.stderr.read()}')
                self.fail('The CLI has unexpectedly stopped running.')
            try:
                output = p.stdout.readline()
                matches = TestAuthentication.re_url.search(output)

                if matches:
                    device_code_url = matches.group(0)
                    self._logger.debug('Detected the device code URL')
                else:
                    self._logger.debug('Waiting...')
                    sleep(1)
            except KeyboardInterrupt:
                p.kill()
                raise RuntimeError('User terminated')

        self._confirm_device_code(device_code_url, email, token)
        self._logger.debug('Waiting for the CLI to join back...')

        while True:
            exit_code = p.poll()
            if exit_code is not None:
                break

        output = p.stdout.read()

        self.assertEqual(exit_code, 0, 'Unexpected exit code')
        self.assertIn("authenticating... ok", output.lower())

    def _confirm_device_code(self, device_code_url, email: str, token: str, allow=True):
        inside_docker_container = bool(
            env('PYTHON_VERSION', required=False) and env('PYTHON_SETUPTOOLS_VERSION', required=False) and env(
                'PYTHON_PIP_VERSION', required=False))
        asked_for_headless_mode = flag('E2E_HEADLESS')
        use_headless_mode = inside_docker_container or asked_for_headless_mode

        self._logger.debug(f'webdriver: asked_for_headless_mode => {asked_for_headless_mode}')
        self._logger.debug(f'webdriver: inside_docker_container => {inside_docker_container}')
        self._logger.debug(f'webdriver: use_headless_mode => {use_headless_mode}')

        chrome_options = Options()
        chrome_options.headless = use_headless_mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)

        self._logger.debug(f'Web driver: Activated')

        driver.get(device_code_url)

        self._logger.debug(f'Web driver: Go to {device_code_url}')

        try:
            driver.execute_script(
                f"document.querySelector('form[name=\"token\"] input[name=\"token\"]').value = '{token}';"
                f"document.querySelector('form[name=\"token\"] input[name=\"email\"]').value = '{email}';"
            )
        except JavascriptException:
            # Show any information available from the driver.
            self._logger.error(f'Failed to execute the script on {driver.current_url}.')
            self._logger.error(f'Here is what the driver can see.\n\n{driver.page_source}\n')

            print_exc()

            driver.quit()
            self.fail(f'Failed to log in with {email} at {device_code_url} due to JavaScript error')
        except:
            print_exc()

            driver.quit()
            self.fail(f'Failed to log in with {email} at {device_code_url} due to unexpected error')

        sleep(5)
        self._logger.debug(f'Web driver: Current: URL: {driver.current_url}')
        self._logger.debug(f'Web driver: Current: Source: {driver.page_source}')

        token_form = driver.find_element(By.CSS_SELECTOR, "form[name='token']")
        token_form.submit()

        sleep(2)

        try:
            driver.find_element(By.ID, "continue-btn").click()

            if allow:
                driver.find_element(By.ID, "allow-btn").click()
            else:
                driver.find_element(By.ID, "deny-btn").click()
        except NoSuchElementException:
            # Show any information available from the driver.
            self._logger.error(f'Failed to execute the script on {driver.current_url}.')
            self._logger.error(f'Here is what the driver can see.\n\n{driver.page_source}\n')
        finally:
            driver.quit()
            self._logger.debug(f'Web driver: Deactivated')
