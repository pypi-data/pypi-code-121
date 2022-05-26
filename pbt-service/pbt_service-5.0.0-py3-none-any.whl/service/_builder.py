"""Context app builder."""

from typing import Dict

from .fn import setup_logger, new_log
from .ext.api import API

from ._config import Config
from ._sentry import init_sentry

log = new_log(__name__)


def _as_service(app: API, config: Config, options: Dict) -> None:
    """Config service app."""
    for router in config.routers:
        app.include_router(router)


def _as_rpc(app: API, config: Config, options: Dict) -> None:
    """Config rpc app."""
    app.routes.clear()


def build(
    config: Config,
    prefix: str = '/',
    prepare: bool = True,
    disable_doc: bool = False,
    **options,
) -> API:
    """Build app."""
    init_kw = {
        'prefix': prefix,
        'debug': config.debug,
    }

    skip_doc_kw = {
        'openapi_url': None,
        'swagger_ui_parameters': {'defaultModelsExpandDepth': -1},
    }

    if prepare and disable_doc:
        init_kw.update(skip_doc_kw)

    app = API(**init_kw)

    if config.log_config.exists():
        setup_logger(config.log_config.as_posix(), debug=config.debug)
    else:
        log.warning(
            f'Log config not found: {config.log_config.as_posix()}',
        )

    init_sentry(config)

    if not prepare:
        # Skip any for possible pipeline using
        log.warning('App is not prepared by request')
        return app

    app.config = config
    app.title = config.service_name
    app.description = config.service_info

    configure = {True: _as_rpc, False: _as_service}
    configure[config.rpc_mode](app, config, options)

    for middleware in config.middleware:
        app.add_middleware(middleware)

    return app


__all__ = ('build', )
