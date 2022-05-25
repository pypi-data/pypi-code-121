from dsocli.exceptions import DSOException
from dsocli.logger import Logger
from dsocli.providers import Providers
from dsocli.releases import ReleaseProvider
from dsocli.constants import *
from dsocli.contexts import ContextMode
from dsocli.aws_s3_utils import *
from dsocli.settings import *
from dsocli.configs import Config


__default_spec = {
    'foo': 'bar',
}


def get_default_spec():
    return __default_spec.copy()


class AwsCfnReleaseProvider(ReleaseProvider):

    def __init__(self):
        super().__init__('release/aws/cfn/v1')

    def create(self):
        Logger.debug(f"Building CFN release: namespace={Config.get_namespace(ContextMode.Target)}, application={Config.get_application(ContextMode.Target)}, stage={Config.get_stage(ContextMode.Target)}, scope={Config.scope}")
        return 'release1.zip'


def register():
    Providers.register(AwsCfnReleaseProvider())
