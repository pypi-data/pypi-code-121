'''
Logging stuff.

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
import logging
import os
import re

import colorama


class NullIndenter(object):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False

# Regular expression used to detect color tags for colorize()
_REGEX_COLOR = re.compile(r'<(red|green|yellow|blue|magenta|cyan|white)>([^<]+)</\1>')

_COLORSTART='\033['
_COLOREND='m'

_COLORS={
    'red':     31,
    'green':   32,
    'yellow':  33,
    'blue':    34,
    'magenta': 35,
    'cyan':    36,
    'white':   37,
}

INDENT = 0

def encodeColor(colorID):
    return _COLORSTART+str(colorID)+_COLOREND

def _colorWrapper(m):
    colorName=m.group(1)
    text = m.group(2)
    colorID=_COLORS[colorName]
    return encodeColor(colorID)+text+encodeColor(0)

def colorize(text):
    return _REGEX_COLOR.sub(_colorWrapper,text)

class IndentLogger(object):
    '''
    Indents stuff.
    '''

    INDENT = 0

    def __init__(self, logger=None):
        self.log = logger
        self.useAnsiColors=False
        if isinstance(self.log, str):
            self.log = logging.getLogger(self.log)
        if self.log is None:
            self.log = logging.getLogger()

    def __enter__(self):
        self.INDENT += 1
        return self

    def __exit__(self, type, value, traceback):
        self.INDENT -= 1
        return False

    def enableANSIColors(self,on=True):
        self.useAnsiColors=on
        if self.useAnsiColors:
            colorama.init(convert=True)
        else:
            colorama.deinit()

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.log.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)
        return self

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        if self.log.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)
        return self

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        if self.log.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)
        return self

    warn = warning

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        if self.log.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)
        return self

    def exception(self, msg, *args, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        kwargs['exc_info'] = 1
        self.error(msg, *args, **kwargs)
        return self

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        if self.log.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, msg, args, **kwargs)
        return self

    def _log(self, level, msg, args, exc_info=None, extra=None):
        if self.useAnsiColors:
            msg=colorize(msg)
        if isinstance(msg, str):
            indent = self.INDENT * '  '
            self.log._log(level, indent + msg, args, exc_info, extra)
        else:
            self.log._log(level, msg, args, exc_info, extra)


logging.basicConfig(
    format='%(asctime)s [%(levelname)-8s]: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO)
    # filename='logs/main.log',
    # filemode='w')

def logToFile(logID, mode='w', level=logging.INFO, sub_dir=None, start_message='Logging started', announce_location=False, formatter=None):
    basedir = 'logs'
    if sub_dir is not None:
        basedir = os.path.join(basedir, sub_dir)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    logfile = os.path.join(basedir, logID + '.log')
    log = logging.getLogger(logID)
    logging.info('Opening %s log at %s (mode: %s)...',logID,logfile,mode)
    if len(log.handlers) == 0:
        # if os.path.isfile(logfile):
        #    os.remove(logfile)
        console = logging.FileHandler(logfile, mode=mode)
        console.setLevel(level)
        if formatter:
            console.setFormatter(formatter)
        log.addHandler(console)
    if start_message is not None:
        log.info(start_message)
    return log

# define a Handler which writes INFO messages or higher to the sys.stderr
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# logging.getLogger('').addHandler(console)

log = IndentLogger()
