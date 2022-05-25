from arpeggio.cleanpeg import NOT, prefix
from pulumi import ComponentResource, ResourceOptions, StackReference
from resources import sm


def SecretsManager(stem, props, name=None, secrets=None, provider=None, parent=None, depends_on=None):
    # Create Secret
    secret = sm.Secret(
        stem,
        props,
        name=name,
        parent=parent,
        depends_on=depends_on,
        provider=provider
    )

    # Secreat Version & key/value pair
    secret_version = sm.SecretVersion(
        stem,
        props,
        sec_id=secret.id,
        secrets=secrets,
        parent=parent,
        depends_on=secret,
        provider=provider
    )

    return secret

