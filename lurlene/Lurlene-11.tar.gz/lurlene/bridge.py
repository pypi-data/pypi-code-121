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

from .context import Sections, Context
from .iface import Config
from .util import threadlocals, catch
from diapyr import types
from diapyr.util import innerclass, outerzip, singleton
from functools import partial
import logging, bisect, difflib

log = logging.getLogger(__name__)

class NoSuchSectionException(Exception): pass

class Channel:

    def __init__(self, index, nametoproxy):
        self.letter = chr(ord('A') + index)
        self.nametoproxy = nametoproxy

class LiveCodingBridge:

    bias = .5 # TODO: Make configurable for predictable swing in odd speed case.

    @types(Config, Context)
    def __init__(self, config, context):
        self.loop = not config.ignoreloop
        self.sectionname = config.section
        self.context = context

    @property
    def pianorollheight(self):
        return self.context.get('speed')

    @innerclass
    class Session:

        def __init__(self, chips):
            self.channels = [Channel(index, {name: proxy for name, proxy in zip(chips, proxies) if proxy is not None})
                    for index, proxies in enumerate(outerzip(*chips.values()))]

        def _quiet(self):
            for channel in self.channels:
                for proxy in channel.nametoproxy.values():
                    proxy.blank()

        def _step(self, speed, section, frame):
            self._quiet()
            for channel, pattern in zip(self.channels, section):
                with catch(channel, "Channel %s update failed:", channel.letter):
                    pattern.apply(speed, frame, channel.nametoproxy)

    def _initialframe(self):
        if self.sectionname is None:
            sectionindex = 0
        else:
            section = getattr(self.context, self.sectionname)
            try:
                sectionindex = self.context.get('sections').index(section)
            except ValueError:
                raise NoSuchSectionException(self.sectionname)
        return self.context.sections.startframe(sectionindex)

    def frames(self, chips):
        session = self.Session(chips)
        frameindex = self._initialframe() + self.bias
        with threadlocals(context = self.context):
            while self.loop or frameindex < self.context.sections.totalframecount:
                oldspeed = self.context.get('speed')
                oldsections = self.context.get('sections')
                frame = session._quiet
                if self.context.sections.totalframecount: # Otherwise freeze until there is something to play.
                    with catch(session, 'Failed to prepare a frame:'):
                        frame = partial(session._step, self.context.get('speed'), *self.context.sections.sectionandframe(frameindex))
                        frameindex += 1
                frame()
                yield
                self.context.flip()
                if oldspeed != self.context.get('speed'):
                    frameindex = (frameindex - self.bias) / oldspeed * self.context.get('speed') + self.bias
                if oldsections != self.context.get('sections'):
                    frameindex = self._adjustframeindex(Sections(self.context.get('speed'), oldsections), frameindex)

    def _adjustframeindex(self, oldsections, frameindex):
        baseframe = (frameindex // oldsections.totalframecount) * self.context.sections.totalframecount
        localframe = frameindex % oldsections.totalframecount
        oldsectionindex = bisect.bisect(oldsections.sectionends, localframe)
        sectionframe = localframe - oldsections.startframe(oldsectionindex)
        opcodes = difflib.SequenceMatcher(a = oldsections.sections, b = self.context.get('sections')).get_opcodes()
        @singleton
        def sectionindexandframe():
            for tag, i1, i2, j1, j2 in opcodes:
                if 'equal' == tag and i1 <= oldsectionindex and oldsectionindex < i2:
                    return j1 + oldsectionindex - i1, sectionframe
            oldsection = oldsections.sections[oldsectionindex]
            for tag, i1, i2, j1, j2 in opcodes:
                if 'insert' == tag and oldsection in self.context.get('sections')[j1:j2]:
                    return j1 + self.context.get('sections')[j1:j2].index(oldsection), sectionframe
            for tag, i1, i2, j1, j2 in opcodes:
                if tag in {'delete', 'replace'} and i1 <= oldsectionindex and oldsectionindex < i2:
                    return j1, self.bias
            return 0, self.bias # TODO: Test this case
        return baseframe + self.context.sections.startframe(sectionindexandframe[0]) + sectionindexandframe[1]
