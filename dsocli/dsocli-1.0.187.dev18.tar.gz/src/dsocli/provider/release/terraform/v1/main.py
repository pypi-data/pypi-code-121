from dsocli.exceptions import DSOException
from dsocli.logger import Logger
from dsocli.providers import Providers
from dsocli.artifacts import Artifactory
from dsocli.releases import ReleaseProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.contexts import Contexts
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
        Logger.debug(f"Building CFN release: namespace:{Config.namespace}, application={Config.application}, stage={Config.stage}")
        return 'release1.zip'


def register():
    Providers.register(AwsCfnReleaseProvider())
