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

from collections.abc import Callable

from turberfield.dialogue.matcher import Matcher
from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.performer import Performer
from turberfield.utils.logger import LogManager


def run_through(script, ensemble, roles=1, strict=False):
    """
    :py:class:`turberfield.dialogue.model.SceneScript`.
    """
    with script as dialogue:
        selection = dialogue.select(ensemble, roles=roles)
        if not any(selection.values()) or strict and not all(selection.values()):
            return

        try:
            model = dialogue.cast(selection).run()
        except (AttributeError, ValueError) as e:
            log_manager = LogManager()
            log = log_manager.clone(
                log_manager.get_logger("main"), "turberfield.dialogue.player.run_through"
            )
            log.warning(". ".join(getattr(e, "args", e) or e))
            return
        else:
            yield from model

def rehearse(
    folders, references, handler,
    repeat=0, roles=1, strict=False,
    loop=None
):
    """Cast a set of objects into a sequence of scene scripts. Deliver the performance.

    :param folders: A sequence of
        :py:class:`turberfield.dialogue.model.SceneScript.Folder` objects.
    :param references: A sequence of Python objects.
    :param handler: A callable object. This will be invoked with every event from the
                    performance.
    :param int repeat: Extra repetitions of each folder.
    :param int roles: Maximum number of roles permitted each character.
    :param bool strict: Only fully-cast scripts to be performed.

    This function is a generator. It yields events from the performance.

    """
    if isinstance(folders, SceneScript.Folder):
        folders = [folders]

    yield from handler(references, loop=loop)

    matcher = Matcher(folders)
    performer = Performer(folders, references)
    while True:
        folder, index, script, selection, interlude = performer.next(
            folders, references, strict=strict, roles=roles
        )
        yield from handler(script, loop=loop)

        for item in performer.run(react=False, strict=strict, roles=roles):
            yield from handler(item, loop=loop)

        if isinstance(interlude, Callable):
            metadata = next(handler(
                interlude, folder, index, references, loop=loop
            ), None)
            yield metadata
            if metadata is None:
                return

            branch = next(matcher.options(metadata))
            if branch != folder:
                performer = Performer([branch], references)

        if not repeat:
            break
        else:
            repeat -= 1
