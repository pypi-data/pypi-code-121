import configparser
import copy
from typing import Any
from typing import Dict


"""
https://blog.gruntwork.io/authenticating-to-aws-with-the-credentials-file-d16c0fbcbf9e

$ aws configure
AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json

AWS prompts you to enter your Access Key ID and Secret Access Key and stores them in ~/.aws/credentials:

[default]
aws_access_key_id=AKIAIOSFODNN7EXAMPLE
aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

It also stores the other settings you entered in ~/.aws/config:

[default]
region=us-west-2
output=json
"""


async def gather(hub) -> Dict[str, Any]:
    """
    load profiles from unencrypted AWS credential files.

    Add "aws.iam" to the "acct.extras" section of your idem config file.

    Example:
    .. code-block:: yaml

        acct:
          extras:
            aws.iam:
              paths:
                - ~/.aws/credentials
                - /path/to/other/credential/file
              # Optional overrides
              region: us-east-1
    """
    sub_profiles = {}
    config = configparser.ConfigParser()

    try:
        ctx = copy.copy(hub.OPT.acct.extras.get("aws.iam", {}))
    except AttributeError:
        return sub_profiles

    credential_files = ctx.pop("paths", [])
    config.read(credential_files)

    for profile in set(config.sections()):
        sub_profiles[profile] = {name: value for name, value in config.items(profile)}
        sub_profiles[profile].update(ctx)

    return sub_profiles
