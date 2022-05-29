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

from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.types import Persona
from turberfield.dialogue.types import Stateful
from turberfield.utils.assembly import Assembly

__doc__ = """
A simple drama for demonstration.

"""


class Animal(Stateful, Persona):
    pass

class Tool(Stateful, Persona):
    pass

def ensemble():
    return [
        Animal(name="Itchy").set_state(1),
        Animal(name="Scratchy").set_state(1),
        Tool(name="Ol' Rusty Chopper").set_state(1),
    ]

references = ensemble()

folder = SceneScript.Folder(
    "turberfield.dialogue.sequences.battle",
    __doc__, None, ["combat.rst"], None
)

Assembly.register(Animal, Tool)
