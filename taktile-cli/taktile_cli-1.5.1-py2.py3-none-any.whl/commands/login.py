from requests.exceptions import HTTPError

from tktl import __version__
from tktl.commands import BaseTaktileApiCommand, CommandBase
from tktl.core.config import set_api_key, settings
from tktl.core.exceptions import APIClientException
from tktl.core.loggers import LOG
from tktl.core.schemas.user import TaktileUser
from tktl.login import logout
from tktl.version import TaktileVersionChecker


class LogInCommand(BaseTaktileApiCommand):
    def execute(self):
        try:
            user = self.client.call(
                verb="get",
                path=f"{settings.API_V1_STR}/users/me",
                model=TaktileUser,
            )
        except HTTPError as e:
            raise APIClientException(e.response.status_code, e.response.reason)
        LOG.log(f"Authentication successful for user: {user.username}", color="green")
        return True


class LogOutCommand(CommandBase):
    def execute(self):
        logout()


class ShowVersionCommand(CommandBase):
    def execute(self, check: bool = False):
        LOG.log(__version__)
        if check:
            TaktileVersionChecker.look_for_new_version()


class SetApiKeyCommand(CommandBase):
    def execute(self, api_key):
        if not api_key:
            LOG.error("API Key cannot be empty.")
            return
        set_api_key(api_key)
        LOG.log(
            f"Successfully added your API Key to {settings.TAKTILE_CONFIG_FILE} You're ready to go!"
        )
