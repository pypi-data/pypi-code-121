import sys
import subprocess

from os import environ, mkdir
from fire import Fire
from pathlib import Path
from uvicorn import run as asgi_run

from service import fn


sys.path.append(fn.project_dir().as_posix())

log = fn.new_log(__name__)


class Service:
    """Service commands."""

    def __init__(self):
        """Init."""
        self.log_config = fn.log_config_path()
        if self.log_config.exists():
            fn.setup_logger(self.log_config.as_posix())

    def develop(
        self,
        host: str = None,
        port: int = None,
        env_file: str = '.env',
    ) -> None:
        """Run dev service."""
        fn.load_env(env_file)

        # Overload from args after load env config
        if host:
            environ['SERVICE_HOST'] = host
        if port:
            environ['SERVICE_PORT'] = str(port)

        try:
            from main import app as main_app
        except ImportError as _main_load_exc:
            sys.exit(f'Failed import main app: {_main_load_exc}')

        greet = 'RPC' if  main_app.config.rpc_mode else 'Service'
        extra_output = {'config': main_app.config}
        if not main_app.config.skip_doc and not main_app.config.rpc_mode:
            extra_output.update({
                'swagger': fn.doc_swagger_url(main_app),
                'redoc': fn.doc_redoc_url(main_app),
            })

        log.warning(
            f'{greet} running on - {fn.api_http_url(main_app)}',
            extra=extra_output,
        )

        asgi_run(
            main_app,
            host=main_app.config.service_host,
            port=main_app.config.service_port,
            log_config=main_app.config.log_config.as_posix(),
        )

    def tests(self, env_file: str = '.env.test') -> None:
        """Run tests."""
        import pytest

        fn.load_env(env_file)
        pytest_conf = fn.poetry_config.get('tool', {}).get('pytest', {})
        pytest_opts = pytest_conf.get('ini_options', {}).get('addopts')

        if not pytest_opts:
            pytest_opts = 'tests'

        pytest_opts = pytest_opts.split()

        pytest.main(pytest_opts)

    def i18n_export(self):
        """Export i18n locales config for locale-gen ."""
        i18n_locales = fn.poetry_config.get('i18n', {}).get('locales', [])
        locales_path = Path(fn.project_dir() / 'locale.gen').resolve()
        with open(locales_path, 'w') as locale_gen:
            for locale_code in i18n_locales:
                locale_gen.write(f'{locale_code}.UTF-8 UTF-8\n')

    def i18n_compile(self):
        """Compile i18n translates."""
        domain_dir = fn.i18n_static_path().as_posix()
        try:
            subprocess.call(['pybabel', 'compile', '-d', domain_dir])
        except Exception as _locale_err:
            sys.exit(f'Check pybabel options: {_locale_err}')

    def i18n_add(self, lang_code: str):
        """Add i18n lang support by code like `en_US`."""
        domain_dir = fn.i18n_static_path().as_posix()
        root_message = Path(fn.i18n_static_path() / 'messages.pot').as_posix()
        i18n_locales = fn.poetry_config.get('i18n', {}).get('locales', [])
        if lang_code not in i18n_locales:
            section = 'pyproject.toml -> i18n -> locales'
            sys.exit(f'Add `{lang_code}` in section "{section}" before')

        try:
            subprocess.call([
                'pybabel',
                'init', '-l', lang_code,
                '-i', root_message,
                '-d', domain_dir,
            ])
        except Exception as _locale_err:
            sys.exit(f'Check pybabel options: {_locale_err}')

    def i18n_init(self):
        """Init i18n static folder."""
        i18n_dir = fn.i18n_static_path()
        if i18n_dir.exists():
            sys.exit('i18n directory already exist')

        mkdir(i18n_dir.as_posix())
        msg_options = {
            'Project-Id-Version': '1.0',
            'Report-Msgid-Bugs-To': 'pbilet@team.com',
            'POT-Creation-Date': '2022-05-12 05:53+0300',
            'PO-Revision-Date': '2022-05-12 05:53+0300',
            'Last-Translator': 'FULL NAME <bilet@team.com>',
            'Language': 'en_US',
            'Plural-Forms': 'nplurals=2; plural=(n != 1);',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
            'Generated-By': 'Babel 2.10.1',
        }

        with open(Path(i18n_dir / 'messages.pot'), 'w') as i18n_pot:
            i18n_pot.write('msgid ""\n')
            i18n_pot.write('msgstr ""\n')
            for opt_name, opt_val in msg_options.items():
                i18n_pot.write(f'"{opt_name}: {opt_val}"\n')

    def migrate(self):
        """Alembic migrate."""
        subprocess.call(['python', '-m', 'alembic', 'upgrade', 'head'])

    def make_migration(self, name: str):
        """Alembic make migration."""
        subprocess.call(['python', '-m', 'alembic', 'revision', '-m', 'name'])

    def rollback(self, rev: str):
        """Alembic rollback to exact revision."""
        subprocess.call(['python', '-m', 'alembic', 'downgrade', rev])


Fire(Service)
