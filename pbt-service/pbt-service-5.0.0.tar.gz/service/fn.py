"""Common funcs."""

import os
import sys
import toml

from dotenv import load_dotenv
from functools import lru_cache
from typing import Dict, List, Tuple
from pathlib import Path
from yarl import URL

from .ext.api import API
from .log import setup_logger, new_log

log = new_log(__name__)


def load_env(env_file: str):
    """Load related env file."""
    _dot_env = Path(project_dir() / env_file).resolve()
    if not _dot_env.exists():
        sys.exit(f'Create `{env_file}` in project dir')
    load_dotenv(_dot_env.as_posix())


def is_debug() -> bool:
    """If debug."""
    return 'true' in str(os.environ.get('DEBUG', '')).lower()


def is_testing():
    """If test in progress."""
    _loaded = sys.modules.keys()
    _py_test = '_pytest.python_path' in _loaded
    _unit = 'unittest' in _loaded
    return _py_test or _unit


def log_config_path() -> Path:
    """Log config path."""
    return Path(project_dir() / 'log.yaml').resolve()


def i18n_static_path() -> Path:
    """i18n static path."""
    return Path(project_dir() / 'i18n').resolve()


@lru_cache
def project_dir() -> Path:
    """Project dir."""
    return Path(os.getcwd()).resolve()


poetry_config_path: Path = Path(project_dir()) / 'pyproject.toml'


def read_project_config() -> Dict:
    """Read project pyproject.toml."""
    try:
        with open(poetry_config_path.as_posix()) as _toml_conf:
            return toml.loads(_toml_conf.read())
    except Exception as _read_project_cfg_exc:
        log.exception(_read_project_cfg_exc)
        sys.exit(f'Poetry config error: {_read_project_cfg_exc}')


poetry_config: Dict = read_project_config()


@lru_cache
def get_config_locale_codes() -> List[str]:
    """Get config locales codes list, like: [en_US, ru_RU, ...]."""
    # os.environ['PROJECT_DIR'] = os.getcwd()
    return poetry_config.get('i18n', {}).get('locales', [])


@lru_cache
def get_config_locales() -> Tuple[str]:
    """Get config locales list, like: [en, ru]."""
    locale_codes = get_config_locale_codes()
    return tuple([str(code[0:2]).lower() for code in locale_codes])


def get_version() -> str:
    """Get app version."""
    try:
        return poetry_config['tool']['poetry']['version']
    except Exception as _read_app_version:
        log.exception(_read_app_version)
        sys.exit(f'App version error: {_read_app_version}')


locales = get_config_locales()


def api_socket(app: API) -> Tuple[str, int]:
    """Get api socket."""
    return str(app.config.service_host), int(app.config.service_port)


def api_http_url(app: API) -> str:
    """Api url with http schema."""
    _host, _port = api_socket(app)
    return str(URL.build(scheme='http', host=_host, port=_port))


def doc_swagger_url(app: API) -> str:
    """Service swagger url."""
    _host, _port = api_socket(app)
    _url = URL.build(scheme='http', host=_host, port=_port, path=app.docs_url)
    return str(_url)


def doc_redoc_url(app: API) -> str:
    """Service redoc url."""
    _host, _port = api_socket(app)
    _url = URL.build(scheme='http', host=_host, port=_port, path=app.redoc_url)
    return str(_url)


__all__ = (
    'new_log',
    'project_dir',
    'is_debug',
    'is_testing',
    'poetry_config',
    'setup_logger',
    'locales',
    'load_env',
    'log_config_path',
    'get_version',
    'i18n_static_path',
    'doc_swagger_url',
    'doc_redoc_url',
)
