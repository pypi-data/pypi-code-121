from copy import deepcopy
from collections import namedtuple
import logging
import os
import os.path as ospath
import re
import yaml

from .errors import AutosplitError


DEFAULT_CONFIGFILE = ospath.join(
    ospath.expanduser("~"),
    '.endi_pdf_split_config.yaml')


_UNSET = object()
_FILENAMESRE = re.compile(
    r'(?P<DOCTYPE>[A-Za-z_-_]+)_(?P<YEAR>'
    r'[0-9]+)_(?P<MONTH>[^_]+)\.pdf',
    re.IGNORECASE
)


class Error(AutosplitError):
    def __init__(self, message):
        self.message = message


class Config(object):
    DEFAULTS = {
        'verbosity': 'INFO',
        'loglevel': 20,
        'use_syslog': False,
        'log_to_mail': False,
        'outline': {
            'no_entr_name': False
        },
        'preprocessor': 'endi-split-pdf-page2text',
        'restrict': 0,
        'mail': {'subject': '[%(hostname)s] Log of endi pdf splitter', },
        'pb_dir': os.path.join(os.environ['HOME'], 'problems'),
    }

    _INSTANCE = None

    @classmethod
    def getinstance(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = Config()
        return cls._INSTANCE

    def __init__(self):
        self.confvalues = {}
        self.parsed_args = None
        self.inputfiles = []

    def load_args(self, parsed_args):
        configstream = parsed_args.configfile
        self.confvalues = deepcopy(self.DEFAULTS)
        self.parsed_args = parsed_args

        if configstream:
            self.confvalues.update(yaml.safe_load(configstream))

        if parsed_args.debug:
            self.confvalues['log_to_mail'] = False
            self.confvalues['preprocessor'] = self.DEFAULTS['preprocessor']

        self._setverb()

        self.confvalues['restrict'] = self.parsed_args.restrict
        self.inputfiles = list(self._parse_inputfiles(parsed_args))

    def _parse_inputfiles(self, parsed_args):
        inputfile = namedtuple(
            'inputfile',
            ['doctype', 'year', 'month', 'filepath', 'filedescriptor']
        )

        for openfile in parsed_args.files:
            # argparse has already open the files
            bare_filename = os.path.split(openfile.name)[-1]
            parsed = _FILENAMESRE.match(bare_filename)

            if parsed is None:
                raise AutosplitError(
                    "Given filename '{}' doesn't match the regexp:\n{}"
                    .format(bare_filename, _FILENAMESRE.pattern)
                )

            yield inputfile(
                parsed.group('DOCTYPE'),
                parsed.group('YEAR'),
                parsed.group('MONTH'),
                openfile.name,
                openfile,
            )

    def _setverb(self):
        if self.parsed_args.verbose:
            self.confvalues['verbosity'] = 'DEBUG'

        str_verb = self.confvalues.get('verbosity')

        self.confvalues['loglevel'] = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }[str_verb]

    def save_defaults(self):
        """
        Only called programmatically, to make the example config file
        """
        with open("config.yaml", "w") as confstream:
            confstream.write(yaml.dump(self.confvalues))

    def getvalue(self, name, override=_UNSET, default=None):
        if override is not _UNSET:
            return override
        if isinstance(name, str):
            value = self.confvalues.get(name, _UNSET)
            if value is _UNSET:
                value = self.DEFAULTS[name]
            return value

        intermediate = self.confvalues
        for item in name:
            intermediate = intermediate.get(item)
            if intermediate is None:
                if default is not None:
                    intermediate = default
                    break
                else:
                    raise AutosplitError(
                        "Missing mandatory configuration parameter {0}".format(
                            name
                        )
                    )

        return intermediate
