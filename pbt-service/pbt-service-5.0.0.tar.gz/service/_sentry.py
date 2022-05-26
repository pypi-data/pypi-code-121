"""Sentry."""

from enum import Enum

from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.logging import LoggingIntegration

from .fn import get_version, new_log


log = new_log(__name__)


class Env(Enum):
    """Env - for sentry commonly."""

    develop = 'develop'
    production = 'production'


def init_sentry(config) -> None:
    """Init sentry from config."""
    if config.testing or not config.sentry_dsn:
        log.debug('Sentry was skipped')
        return

    _release = get_version()
    _env = str(config.environment.value)
    _dsn = str(config.sentry_dsn)

    try:
        sentry_init(
            dsn=_dsn,
            server_name=config.service_name,
            release=_release,
            environment=_env,
            attach_stacktrace=True,
            integrations=[LoggingIntegration()],
            request_bodies='always',
            with_locals=config.debug,
        )
    except Exception as fault_sentry:
        log.error(
            f'Fault init sentry by reason: {str(fault_sentry)}',
            extra={'config': config},
        )
        return

    log.debug(
        f'Set sentry {_release}@{_env} to {_dsn}',
        extra={'config': config},
    )


__all__ = 'init_sentry'
