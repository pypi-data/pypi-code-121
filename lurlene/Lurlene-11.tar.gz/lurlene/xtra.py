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

from . import V, D, _topitch, major
from .pitches import E4

class XTRA:

    degree = D('-') + D('- 5- 1 5,+').of(6)
    envflag = V('30x,1')
    mute = False

    def on(self, ym, frame):
        if self.mute:
            return
        envflag = self.envflag[frame]
        pitch = _topitch(major, 1, E4, self.degree[frame])
        for chan in range(min(3, len(ym._chanproxies))):
            ym[chan].toneflag = True
            ym[chan].level = 15
            ym[chan].envflag = envflag
            ym[chan].tonepitch = pitch
            ym[chan].toneperiod += chan * 2
        if envflag and not self.envflag[frame - 1]:
            ym.envshape = 0
        ym.envperiod = 30 << 8

    def off(self):
        type(self).mute = True
