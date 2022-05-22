import os
import sys
from importlib.resources import path as rpath
from typing import Union
from configparser import ConfigParser
from logging import Logger, getLogger, DEBUG

from .utils import create_dir, copy_file, get_expanded_path
from .arg_parser import get_parsed_arguments
from .configuration import get_parsed_config, DEFAULT_CONFIG_PATH, VERSION
from .database import Database
from .builder import Builder

log: Logger = getLogger(__name__)


def main() -> None:
    args: dict[str, Union[str, bool]] = vars(get_parsed_arguments())

    if args['debug']:
        # need to modify the root logger specifically,
        #   as it is the one that holds the config
        #   (__name__ happens to resolve to pyssg in __init__)
        root_logger: Logger = getLogger('pyssg')
        root_logger.setLevel(DEBUG)
        for handler in root_logger.handlers:
            handler.setLevel(DEBUG)
        log.debug('changed logging level to DEBUG')

    if not len(sys.argv) > 1 or (len(sys.argv) == 2 and args['debug']):
        log.info('pyssg v%s - no arguments passed, --help for more', VERSION)
        sys.exit(0)

    if args['version']:
        log.info('pyssg v%s', VERSION)
        sys.exit(0)

    config_path: str = args['config'] if args['config'] else DEFAULT_CONFIG_PATH
    config_path = get_expanded_path(config_path)
    config_dir, _ = os.path.split(config_path)
    log.debug('checked config file path, final config path "%s"', config_path)

    if args['copy_default_config']:
        log.info('copying default config file')
        create_dir(config_dir)
        with rpath('pyssg.plt', 'default.ini') as p:
            copy_file(p, config_path)
        sys.exit(0)

    if not os.path.exists(config_path):
        log.error('config file does\'t exist in path "%s"; make sure'
                  ' the path is correct; use --copy-default-config if it\'s the'
                  ' first time if you haven\'t already', config_path)
        sys.exit(1)

    config: ConfigParser = get_parsed_config(config_path)
    config.set('info', 'debug', str(args['debug']))

    if args['init']:
        log.info('initializing the directory structure and copying over templates')
        create_dir(config.get('path', 'src'))
        create_dir(os.path.join(config.get('path', 'dst'), 'tag'), True)
        create_dir(config.get('path', 'plt'))
        files: list[str] = ('index.html',
                            'page.html',
                            'tag.html',
                            'rss.xml',
                            'sitemap.xml')
        log.debug('list of files to copy over: (%s)', ', '.join(files))
        for f in files:
            plt_file: str = os.path.join(config.get('path', 'plt'), f)
            with rpath('pyssg.plt', f) as p:
                copy_file(p, plt_file)
        sys.exit(0)

    if args['add_checksum_to_db']:
        log.info('adding checksum column to existing db')
        db_path: str = os.path.join(config.get('path', 'src'), '.files')
        db: Database = Database(db_path, config)
        # needs to be read_old instead of read
        db.read_old()
        db.write()

        sys.exit(0)

    if args['build']:
        log.info('building the html files')
        db_path: str = os.path.join(config.get('path', 'src'), '.files')
        db: Database = Database(db_path, config)
        db.read()

        builder: Builder = Builder(config, db)
        builder.build()

        db.write()
        sys.exit(0)
