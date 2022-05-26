import json
import os.path as op
from .validation import validator
from .validation.utils import __md5__
import bbrc

__version__ = __md5__(op.abspath(validator.__file__))[:8]


def get_version_label(version):

    f = op.join(op.dirname(bbrc.__file__), 'data', 'versions.json')
    with open(f, 'r') as fp:
        versions = json.load(fp)

    if version in versions.keys() and 'label' in versions[version].keys():
        label = versions[version]['label']
    else:
        label = None

    return label
