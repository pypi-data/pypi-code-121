from pathlib import Path
import logging

from .opr3 import Data
from .readquery import *

from .__version__ import __version__

__author__ = 'Shaun C Read'

try:
    from colored import fore, style
    from pkg_info import get_pkg_info
    from semver import compare
    import urllib
    import json
    from datetime import datetime
    from typing import Callable


    def parse_changes(description):
        log = description.split('machine-readable-change-log\n###########################\n')[-1]
        return log


    def get_other_descriptions(name, version):
        return json.loads(urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{version}/json', timeout=3).read())['info']['description']


    class UpdateNotify(object):
        def __init__(self, name: str, version: str):
            self.name: str = name
            self.version: str = version
            self.last_checked_path = Path(__file__).parent / '.last-checked'
            self.time_fmt = '%Y-%m-%dT%H:%M:%S'
            self._pkg = None
            self.freq = 1  # hours

        @property
        def pkg(self):
            if self._pkg is None:
                self._pkg = get_pkg_info(self.name)
            return self._pkg

        @property
        def latest(self):
            return self.pkg.version

        def last_checked(self):
            try:
                with open(str(self.last_checked_path), 'r') as f:
                    return datetime.strptime(f.read().strip(), self.time_fmt)
            except FileNotFoundError:
                return None

        def too_soon(self):
            lc = self.last_checked()
            if lc is None:
                return False
            seconds = (datetime.now() - lc).total_seconds()
            return (seconds / 60 / 60) < self.freq

        def update_last_checked(self):
            with open(str(self.last_checked_path), 'w') as f:
                f.write(datetime.now().strftime(self.time_fmt))

        def is_latest_version(self) -> bool:
            return True if compare(self.version, self.latest) >= 0 else False

        def render_changes(self):
            releases = [(k, datetime.strptime(v[0]['upload_time'], self.time_fmt)) for k, v in self.pkg.raw_data['releases'].items()]
            releases.sort(key=lambda x: x[1])
            release_names, _ = zip(*releases)
            release_names = release_names[release_names.index(self.version)+1:]
            changes = [parse_changes(get_other_descriptions(self.pkg.name, v)) for v in release_names]
            return changes[::-1]

        def notify(self) -> None:
            if self.too_soon():
                logging.info(f'Skipping version checking since its has not been {self.freq} hour since the last check.')
                return
            if self.is_latest_version():
                return
            action, arg = print, self.default_message()
            action(arg) if arg else action()
            self.update_last_checked()

        def default_message(self) -> str:
            changes = self.render_changes()
            version = fore.GREY_53 + self.version + style.RESET
            latest = fore.LIGHT_GREEN + self.latest + style.RESET
            command = fore.LIGHT_BLUE + 'pip3 install --user --upgrade ' + self.name + style.RESET
            nchanges = fore.LIGHT_GREEN + str(len(changes)) + style.RESET
            strings = [f'Update available {version} -> {latest} ({nchanges} new releases)' ,
                       f'Run {command} to update'] + [f'--- {c.strip()}' for c in changes]
            maxlen = max(map(len, strings))
            strings = list(map(lambda s: ' ' + s, strings))
            prefix = ' ' + '*' * (maxlen - 2)
            suffix = ' ' + '*' * (maxlen - 2)
            strings.insert(0, prefix)
            strings.append(suffix)
            return '\n'.join(strings)


    UpdateNotify('weaveio', __version__).notify()

except ImportError:
    from warnings import warn
    warn('Please run `pip install colored pkg_info semver` to alert you to updated versions of the weaveio library')
except Exception as e:
    logging.exception('There was a problem in alerting you to updated versions of the weaveio library...', exc_info=True)
