from arpeggio.cleanpeg import NOT, prefix
from pulumi.resource import ResourceOptions
import pulumi_random as random
import pulumi_aws_native.s3 as s3_native

def RandomPassword(stem, provider=None, parent=None, depends_on=None):
    password = random.RandomPassword(
        f'pw-{stem}',
        length=24,
        upper=True,
        lower=True,
        number=True,
        special=True,
        override_special="!#$%&*",
        opts=ResourceOptions(parent=parent, depends_on=depends_on)
    )
    return password

def RandomString(stem, provider=None, parent=None, depends_on=None):
    password = random.RandomString(
        f'pw-{stem}',
        length=24,
        upper=True,
        lower=True,
        number=True,
        special=True,
        override_special="!#$%&*[]<>",
        opts=ResourceOptions(parent=parent, depends_on=depends_on)
    )
    return password