#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


from collections import deque
from collections import namedtuple
import decimal
from decimal import Decimal as Dl


__doc__ = """
The module defines functions for calculating motion using
:py:class:`Impulses <turberfield.utils.travel.Impulse>`.
"""

Impulse = namedtuple("Impulse", ["tBegin", "tEnd", "accn", "pos"])
Impulse.__doc__ = """`{}`

An Impulse object defines a change in motion over a short interval
of time.

    tBegin
        The start of the time interval.
    tEnd
        The end of the time interval.
    accn
        The second derivative of position over the time interval.
    pos
        The position at the start of the time interval.
""".format(Impulse.__doc__)


def time_correct_verlet(state, t, accn, mass=1):
    """
    This low-level function implements a single step of
    Time-corrected Verlet position integration. See Jonathan Dummer's
    `article on TCV`_ for a full description of the algorithm.

    :param state: a 2-tuple of
                :py:class:`Impulses <turberfield.utils.travel.Impulse>`
                . Element 0 is the most recent in time.
    :param t: a time quantity.
    :param accn: an acceleration quantity.
    :returns: a new state 2-tuple.
    :requires: `acceleration` type to support multiplication over
            `time` type.

    .. _article on TCV: http://lonesock.net/article/verlet.html
    """
    imp0, imp_1 = state
    dt0, dt_1 = (
        Dl(imp0.tBegin - imp0.tEnd),
        Dl(imp_1.tBegin - imp_1.tEnd)
    )
    leap = imp0.accn * dt0 * dt0
    try:
        pos = imp0.pos + (imp0.pos - imp_1.pos) * dt0 / dt_1 + leap
    except (ZeroDivisionError, decimal.InvalidOperation):
        pos = imp0.pos + (imp0.pos - imp_1.pos) + leap
    rv = Impulse(imp0.tEnd, t, accn, pos)
    return (rv, imp0)


def trajectory(limits=None):
    """
    A motion engine implemented as a Python generator. Like
    all generators you must prime it first by sending `None`.

    You operate it by repeatedly sending it
    :py:class:`Impulses <turberfield.utils.travel.Impulse>`. The first
    of these establishes the initial position of the body. The
    second is to initialise the movement of the body. Thereafter, the
    generator is self-sustaining and need only be fed from its own
    output to keep it going.

    The generator yields
    :py:class:`Impulse <turberfield.utils.travel.Impulse>` objects,
    from which all the instantaneous parameters of motion can be
    accessed or derived.

    Here is an example of simulating a fall under gravity in one
    dimension with an initial positive velocity::

        motion = trajectory()
        motion.send(None)

        zero = decimal.Decimal(0)
        dt = decimal.Decimal("0.5")
        v0 = decimal.Decimal("65.0")
        gravity = decimal.Decimal("-9.806")

        for n in itertools.count():
            if n == 0:
                imp = motion.send(Impulse(zero, dt, gravity, zero))
            elif n == 1:
                imp = motion.send(Impulse(
                    imp.tEnd, imp.tEnd + dt, gravity,
                    v0 * dt + 0.5 * gravity * dt * dt))
            else:
                imp = motion.send(Impulse(
                    imp.tEnd, imp.tEnd + dt, gravity, imp.pos))
    """
    state = deque([], maxlen=2)
    if len(state) == 0:
        imp = yield None
        state.appendleft(imp)
        imp = yield state[0]
        state.appendleft(imp)
        imp = yield state[0]
        state = time_correct_verlet(state, imp.tEnd, imp.accn)
        imp = yield state[0]
    while True:
        if imp.pos != state[0].pos:
            state = (imp, state[0])
        else:
            state = time_correct_verlet(state, imp.tEnd, imp.accn)
        imp = yield state[0]
