import os
import logging

SECRETS_DIR = "/run/secrets"
SECRETS_DELIM = "__"

logger = logging.getLogger(__file__)


def load_secrets(
    secrets_dir: str = SECRETS_DIR,
    secrets_delim: str = SECRETS_DELIM,
):
    """
    Read docker secrets and set environment variables.

    Examples
    --------
    >>> # 'AWS_ACCESS_KEY_ID__eugene_personal' is in '/run/secrets' folder
    >>> os.getenv("AWS_ACCESS_KEY_ID")
    >>> load_secrets()
    >>> os.getenv("AWS_ACCESS_KEY_ID")
    <eugene's access key id>
    """

    if not os.path.exists(secrets_dir):
        logger.debug(f"No docker secrets - '{secrets_dir}' not exists.")
        return

    secrets = {f.name.rsplit(secrets_delim, 1)[0]: f.path for f in os.scandir(secrets_dir) if f.is_file()}
    for env, fp in secrets.items():
        try:
            with open(fp, "r") as f:
                os.environ[env] = f.read()
            logging.debug(f"Env. '{env}' is loaded from docker secrets.")
        except Exception as ex:
            logging.warning(f"Loading env. '{env}' is failed! - {ex}")
