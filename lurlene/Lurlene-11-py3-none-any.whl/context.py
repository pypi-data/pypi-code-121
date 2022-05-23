# Copyright 2019 Andrzej Cichocki

# This file is part of Lurlene.
#
# Lurlene is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lurlene is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lurlene.  If not, see <http://www.gnu.org/licenses/>.

from . import E
from .iface import Config
from .transform import Interpreter
from .util import Lazy
from .xtra import XTRA
from diapyr import types
import bisect, logging, numpy as np, threading

log = logging.getLogger(__name__)

class Context:

    lazyname = '_lazy' # XXX: More reliably avoid collision?
    deleted = object()

    @types(Config)
    def __init__(self, config, sections = [(E(XTRA, '11/1'),)]):
        self.fastglobals = self.slowglobals = dict(
            {self.lazyname: Lazy},
            __name__ = 'lurlene.context',
            tuning = config.tuning,
            mode = 1,
            speed = 16, # XXX: Needed when sections is empty?
            sections = sections,
        )
        self.snapshot = self.fastglobals.copy()
        self.fastupdates = self.slowupdates = {}
        self.cache = {}
        self.slowlock = threading.Lock()
        self.fastlock = threading.Lock()
        i = Interpreter(self.lazyname, self.slowglobals)
        self.interpreter = i if config.Lurlene.lazy else i.justexec

    def update(self, text):
        addupdate = []
        delete = []
        with self.slowlock:
            with self.fastlock:
                self.fastglobals = self.slowglobals.copy()
                self.fastupdates = self.slowupdates.copy()
            before = self.slowglobals.copy()
            self.interpreter(text) # XXX: Impact of modifying mutable objects?
            for name, value in self.slowglobals.items():
                if not (name in before and value is before[name]):
                    self.slowupdates[name] = value
                    addupdate.append(name)
            for name in before:
                if name not in self.slowglobals:
                    self.slowupdates[name] = self.deleted
                    delete.append(name)
            with self.fastlock:
                self.fastglobals = self.slowglobals
                self.fastupdates = self.slowupdates
        if addupdate:
            log.info("Add/update: %s", ', '.join(addupdate))
        if delete:
            log.info("Delete: %s", ', '.join(delete))
        if not (addupdate or delete):
            log.info('No change.')

    def flip(self):
        if self.slowlock.acquire(False):
            try:
                with self.fastlock:
                    self.snapshot = self.fastglobals.copy()
                    self.fastupdates.clear()
            finally:
                self.slowlock.release()

    class NoSuchGlobalException(Exception): pass

    def get(self, name):
        'Include changes made via global keyword.'
        with self.fastlock:
            # If the fastglobals value (or deleted) is due to update, return snapshot value (or deleted):
            value = self.fastglobals.get(name, self.deleted)
            if name in self.fastupdates and value is self.fastupdates[name]:
                try:
                    return self.snapshot[name]
                except KeyError:
                    raise self.NoSuchGlobalException(name) # TODO: Test this case.
            if value is self.deleted:
                raise self.NoSuchGlobalException(name)
            return value

    def _cachedproperty(f):
        name = f.__name__
        code = f.__code__
        params = code.co_varnames[1:code.co_argcount]
        def fget(self):
            args = [self.get(p) for p in params]
            try:
                cacheargs, value = self.cache[name]
                if all(x is y for x, y in zip(cacheargs, args)):
                    return value
            except KeyError:
                pass
            value = f(*[self] + args)
            self.cache[name] = args, value
            return value
        return property(fget)

    @_cachedproperty
    def sections(self, speed, sections):
        return Sections(speed, sections)

class Sections:

    def __init__(self, speed, sections):
        # FIXME: Recalculate sectionends when a lazy section is resized.
        self.sectionends = np.cumsum([speed * max(pattern.len for pattern in section) for section in sections])
        self.sections = sections

    @property
    def totalframecount(self):
        return self.sectionends[-1]

    def startframe(self, sectionindex):
        return self.sectionends[sectionindex - 1] if sectionindex else 0

    def sectionandframe(self, frameindex):
        localframe = frameindex % self.sectionends[-1]
        i = bisect.bisect(self.sectionends, localframe)
        return self.sections[i], localframe - self.startframe(i)
