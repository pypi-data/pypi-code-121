from typing import Optional
import requests
from tinybird.syncasync import sync_to_async
import click
from tinybird.feedback_manager import FeedbackManager

PYPY_URL = 'https://pypi.org/pypi/tinybird-cli/json'
requests_get = sync_to_async(requests.get, thread_sensitive=False)


class CheckPypi:

    async def get_latest_version(self) -> Optional[str]:
        version: Optional[str] = None
        try:
            response: requests.Response = await requests_get(PYPY_URL)
            if response.status_code != 200:
                click.ClickException(FeedbackManager.error_exception(error=response.content.decode('utf-8')))
            version = response.json()['info']['version']
        except Exception as e:
            click.ClickException(FeedbackManager.error_exception(error=str(e)))

        return version
