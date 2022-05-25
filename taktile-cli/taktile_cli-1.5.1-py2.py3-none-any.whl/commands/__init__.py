from tktl.core.clients import DeploymentApiClient
from tktl.core.clients.taktile import TaktileApiClient
from tktl.core.loggers import LOG, Logger


class CommandBase(object):
    def __init__(self, api=None):
        self.api = api


class BaseDeploymentApiCommand:
    def __init__(self, logger: Logger = LOG):
        self.client = DeploymentApiClient(logger=logger)


class BaseTaktileApiCommand:
    def __init__(self, logger: Logger = LOG):
        self.client = TaktileApiClient(logger=logger)
