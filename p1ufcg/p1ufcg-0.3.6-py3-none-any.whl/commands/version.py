from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import requests
import pkg_resources
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

from p1.utils import cprint
from p1.colors import *

def main():
    current = pkg_resources.get_distribution('p1ufcg').version
    if not sys.stdout.isatty():
        print(current)
        return

    cprint(WHITE, current, file=sys.stdout)
    try:
        s = requests.session()
        s = CacheControl(s, cache=FileCache(os.path.expanduser('~/.p1/cache')))
        response = s.get('https://pypi.org/pypi/p1ufcg/json', timeout=5)
        data = response.json()

        latest_version = data['info']['version']
        if current != latest_version:
            cprint(YELLOW, 'Última versão: %s' % latest_version, file=sys.stdout)
            cprint(RESET, '---\n'
                          'Use `pip install --upgrade p1ufcg` para instalar/atualizar')
    except requests.ConnectionError:
        cprint(LRED, 'Sem conexão para pypi.org')
