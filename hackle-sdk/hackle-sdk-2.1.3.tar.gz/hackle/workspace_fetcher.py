import threading
import time
import traceback

import requests
from requests import exceptions as requests_exceptions

from hackle import logger as hackle_logger
from hackle import version
from hackle.commons import enums
from hackle.workspace import Workspace


class WorkspaceFetcher(object):
    def __init__(self, sdk_key=None, update_interval=None, blocking_timeout=None, logger=None, timeout=None):
        self.sdk_key = sdk_key
        self.workspace_url = enums.Default.WORKSPACE_URL
        self.update_interval = update_interval or enums.Default.DEFAULT_POLL_INTERVAL
        self.blocking_timeout = blocking_timeout or enums.Default.DEFAULT_BLOCKING_TIMEOUT
        self.logger = hackle_logger.adapt_logger(logger or hackle_logger.NoOpLogger())
        self.timeout = timeout
        self._workspace_fetch_ready_event = threading.Event()
        self._polling_thread = threading.Thread(target=self._run)
        self._polling_thread.setDaemon(True)
        self._polling_thread.start()

    def _handle_response(self, response):
        try:
            response.raise_for_status()
        except requests_exceptions.RequestException as err:
            self.logger.error('Failed to pool Workspace: {}'.format(err))
            return

        self._set_workspace(response.content.decode('utf-8'))

    def fetch(self):
        request_headers = {enums.Default.SDK_KEY_HEADER: self.sdk_key,
                           enums.Default.SDK_NAME_HEADER: 'python-sdk',
                           enums.Default.SDK_VERSION_HEADER: version.__version__}
        try:
            response = requests.get(
                self.workspace_url,
                headers=request_headers,
                timeout=self.timeout or enums.Default.REQUEST_TIMEOUT
            )
        except requests_exceptions.RequestException:
            self.logger.error('Failed to pool Workspace: {}'.format(traceback.format_exc()))
            return

        self._handle_response(response)

    @property
    def is_running(self):
        return self._polling_thread.is_alive()

    def _run(self):
        try:
            while self.is_running:
                self.fetch()
                time.sleep(self.update_interval)
        except (OSError, OverflowError) as err:
            self.logger.error('Error : {}'.format(str(err)))
            raise

    def start(self):
        if not self.is_running:
            self._polling_thread.start()

    def _set_workspace(self, content):
        if content or self._workspace_fetch_ready_event.is_set():
            self._workspace = Workspace(content)
            self._workspace_fetch_ready_event.set()

    def get_workspace(self):
        self._workspace_fetch_ready_event.wait(self.blocking_timeout)
        if hasattr(self, '_workspace'):
            return self._workspace
        return None

    def stop(self):
        if self.is_running:
            self._polling_thread.join(self.blocking_timeout)
