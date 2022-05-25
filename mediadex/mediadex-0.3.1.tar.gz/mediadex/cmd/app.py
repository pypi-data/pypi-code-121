#!/usr/bin/python3

# Mediadex: Index media metadata into opensearch
# Copyright (C) 2019-2022  Joni Harker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import argparse
import datetime
import logging
import os

import yaml
from opensearch_dsl import connections

from mediadex.cmd.fileinfo import FileInfo
from mediadex.indexer import Indexer
from mediadex.indexer import IndexerException
from mediadex.purger import MoviePurger
from mediadex.purger import SongPurger


class App:
    def __init__(self):
        self.args = None
        self.dex = None
        self.log = None
        self.client = None

    def parse_args(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('-p', '--path',
                            dest='path',
                            action='append',
                            help='top directory to search for media')

        parser.add_argument('-v', '--verbose',
                            dest='verbose',
                            action='count',
                            help='output additional log messages')

        parser.add_argument('--purge',
                            dest='purge',
                            action='store_true',
                            help='Scan for deleted files and remove '
                            'their entries from opensearch')

        parser.add_argument('--today',
                            dest='today',
                            action='store_true',
                            help='only scan recent files')

        parser.add_argument('-H', '--opensearch-host',
                            dest='host',
                            action='store', default='localhost:9200',
                            help='opensearch host to connect to')

        parser.add_argument('--opensearch-user-pass',
                            dest='userpass',
                            action='store', default='admin:admin',
                            help='opensearch host to connect to')

        parser.add_argument('--insecure',
                            dest='insecure',
                            action='store_true',
                            help='ignore tls failures')

        parser.add_argument('-x', '--dry-run',
                            dest='dry_run',
                            action='store_true',
                            help='write to stdout as yaml instead of '
                            'indexing into opensearch')

        self.args = parser.parse_args()

    def setup_logging(self, level):
        root_log = logging.getLogger()
        root_log.setLevel(level)
        sh = logging.StreamHandler()
        sh.setLevel(level)
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        sh.setFormatter(logging.Formatter(fmt))
        root_log.addHandler(sh)

        for lib in ['opensearch', 'imdb', 'imdbpy', 'urllib3']:
            log = logging.getLogger(lib)
            log.setLevel(logging.WARNING)

        self.log = logging.getLogger('mediadex')
        self.log.setLevel(level)

    def index(self, fi):
        if self.args.dry_run:
            self.log.info(yaml.dump(fi))
        else:
            try:
                self.dex.index(fi)
            except IndexerException as exc:
                if self.log.isEnabledFor(logging.INFO):
                    self.log.exception(exc)
                else:
                    self.log.warn(str(exc))
                self.log.debug(yaml.dump(fi))
                return 1
        return 0

    def open_file(self, fp, bp):
        info = FileInfo(fp, bp)

        if self.args.today:
            _stat = os.stat(fp)
            mtime = datetime.datetime.fromtimestamp(_stat.st_mtime)
            diff = datetime.datetime.now() - mtime
            if diff > datetime.timedelta(days=1):
                self.log.debug('Skipping {} due to timestamp'.format(fp))
                return 0

        return self.index(info)

    def walk_paths(self):
        retval = 0
        for path in self.args.path:
            for (_top, _dirs, _files) in os.walk(path):
                for _file in _files:
                    fp = os.path.join(_top, _file)
                    try:
                        retval += self.open_file(fp, path)
                    except Exception as exc:
                        if self.log.isEnabledFor(logging.INFO):
                            self.log.exception(exc)
                        else:
                            self.log.warn(str(exc))
                        retval += 1
        return retval

    def purge(self):
        retval = 0
        try:
            sp = SongPurger()
            mp = MoviePurger()
            retval += sp.purge() + mp.purge()
        except Exception as exc:
            self.log.exception(exc)
            retval += 1
        return retval

    def run(self):
        self.parse_args()

        if self.args.verbose is None:
            self.setup_logging(level=logging.WARNING)
        elif self.args.verbose == 1:
            self.setup_logging(level=logging.INFO)
        else:
            self.setup_logging(level=logging.DEBUG)

        if not self.args.dry_run:
            host, port = self.args.host.split(':')
            user, pw = self.args.userpass.split(':')

            secure = True
            if self.args.insecure:
                import urllib3
                urllib3.disable_warnings()
                secure = False

            connections.create_connection(
              hosts=[{'host': host, 'port': port}],
              http_auth=(user, pw),
              use_ssl=True,
              verify_certs=secure,
              ssl_assert_hostname=secure,
            )

            self.dex = Indexer()
            if self.args.purge:
                return self.purge()

        return self.walk_paths()
