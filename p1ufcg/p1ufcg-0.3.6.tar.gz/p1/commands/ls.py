from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import p1
import sys

from p1.colors import *
from p1.utils import cprint
from p1.jsonfile import JsonFile

def main():
    ls(sys.argv)


def ls(args):
    """list files in activity"""

    p1json = JsonFile('.p1/p1.json')
    files = p1json.setdefault('files', {})
    for fn in sorted(files.keys()):
        visibility = files[fn].get('category', 'private')
        print(fn, ("(%s)" % visibility if visibility == 'public' else ''))
