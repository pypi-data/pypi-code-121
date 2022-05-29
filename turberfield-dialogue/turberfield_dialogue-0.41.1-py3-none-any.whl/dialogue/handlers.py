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

import asyncio
from collections.abc import Callable
from collections.abc import MutableSequence
import logging
import sys
import textwrap
import time
import wave

import pkg_resources
try:
    import simpleaudio
except ImportError:
    simpleaudio = None

import turberfield.dialogue.cli
from turberfield.dialogue.model import Model
from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.schema import SchemaBase
from turberfield.utils.assembly import Assembly
from turberfield.utils.db import Connection
from turberfield.utils.db import Creation
from turberfield.utils.logger import LogManager


class TerminalHandler:
    """
    The default handler for events from scene script files.
    It generates output for a console terminal.

    The class is written to be a callable, stateful object.
    Its `__call__` method delegates to handlers specific to each type of event.
    You can subclass it and override those methods to suit your own application.

    :param terminal: A stream object.
    :param str dbPath: An optional URL to the internal database.
    :param float pause: The time in seconds to pause on a line of dialogue.
    :param float dwell: The time in seconds to dwell on a word of dialogue.
    :param log: An optional log object.

    """
    pause = turberfield.dialogue.cli.DEFAULT_PAUSE_SECS
    dwell = turberfield.dialogue.cli.DEFAULT_DWELL_SECS

    @staticmethod
    def handle_audio(obj, wait=False):
        """Handle an audio event.

        This function plays an audio file.
        Currently only `.wav` format is supported.

        :param obj: An :py:class:`~turberfield.dialogue.model.Model.Audio`
            object.
        :param bool wait: Force a blocking wait until playback is complete.
        :return: The supplied object.

        """
        if not simpleaudio:
            return obj

        fp = pkg_resources.resource_filename(obj.package, obj.resource)
        data = wave.open(fp, "rb")
        nChannels = data.getnchannels()
        bytesPerSample = data.getsampwidth()
        sampleRate = data.getframerate()
        nFrames = data.getnframes()
        framesPerMilliSecond = nChannels * sampleRate // 1000

        offset = framesPerMilliSecond * obj.offset
        duration = nFrames - offset
        duration = min(
            duration,
            framesPerMilliSecond * obj.duration if obj.duration is not None else duration
        )

        data.readframes(offset)
        frames = data.readframes(duration)
        for i in range(obj.loop):
            waveObj = simpleaudio.WaveObject(frames, nChannels, bytesPerSample, sampleRate)
            playObj = waveObj.play()
            if obj.loop > 1 or wait:
                playObj.wait_done()
        return obj

    def handle_interlude(
        self, obj, folder, index, ensemble,
        loop=None, **kwargs
    ):
        """Handle an interlude event.

        Interlude functions permit branching. They return a folder which the
        application can choose to adopt as the next supplier of dialogue.

        This handler calls the interlude with the supplied arguments and
        returns the result.

        :param obj: A callable object.
        :param folder: A
            :py:class:`~turberfield.dialogue.model.SceneScript.Folder` object.
        :param int index: Indicates which scene script in the folder
            is being processed.
        :param ensemble: A sequence of Python objects.
        :param branches: A sequence of
            :py:class:`~turberfield.dialogue.model.SceneScript.Folder` objects.
            from which to pick a branch in the action.
        :return: A :py:class:`~turberfield.dialogue.model.SceneScript.Folder`
            object.

        """
        if obj is None:
            return folder.metadata
        else:
            return obj(folder, index, ensemble, loop=loop, **kwargs)

    def handle_line(self, obj):
        """Handle a line event.

        This function displays a line of dialogue. It generates a blocking wait
        for a period of time calculated from the length of the line.

        :param obj: A :py:class:`~turberfield.dialogue.model.Model.Line` object.
        :return: The supplied object.

        """
        if obj.persona is None:
            return obj

        name = getattr(obj.persona, "_name", "")
        print(
            textwrap.indent(
                "{t.normal}{name}".format(name=name, t=self.terminal),
                " " * 2
            ),
            end="\n",
            file=self.terminal.stream
        )
        print(
            textwrap.indent(
                "{t.normal}{obj.text}".format(
                    obj=obj, t=self.terminal
                ),
                " " * 10
            ),
            end="\n" * 2,
            file=self.terminal.stream
        )
        interval = self.pause + self.dwell * obj.text.count(" ")
        time.sleep(interval)
        return obj

    def handle_memory(self, obj):
        """Handle a memory event.

        This function accesses the internal database. It writes a record
        containing state information and an optional note.

        :param obj: A :py:class:`~turberfield.dialogue.model.Model.Memory`
            object.
        :return: The supplied object.

        """
        if obj.subject is not None:
            with self.con as db:
                SchemaBase.note(
                    db,
                    obj.subject,
                    obj.state,
                    obj.object,
                    text=obj.text,
                    html=obj.html,
                )
        return obj

    def handle_property(self, obj):
        """Handle a property event.

        This function will set an attribute on an object if the event requires
        it.

        :param obj: A :py:class:`~turberfield.dialogue.model.Model.Property`
            object.
        :return: The supplied object.

        """
        if obj.object is not None:
            try:
                setattr(obj.object, obj.attr, obj.val)
            except AttributeError as e:
                self.log.error(". ".join(getattr(e, "args", e) or e))
            try:
                print(
                    "{t.dim}{obj.object._name}.{obj.attr} = {obj.val!s}{t.normal}".format(
                        obj=obj, t=self.terminal
                    ),
                    end="\n" * 2,
                    file=self.terminal.stream
                )
            except AttributeError as e:
                self.log.error(". ".join(getattr(e, "args", e) or e))
        return obj

    def handle_scene(self, obj):
        """Handle a scene event.

        This function applies a blocking wait at the start of a scene.

        :param obj: A :py:class:`~turberfield.dialogue.model.Model.Shot`
            object.
        :return: The supplied object.

        """
        print(
            "{t.dim}{scene}{t.normal}".format(
                scene=obj.scene.capitalize(), t=self.terminal
            ),
            end="\n" * 3,
            file=self.terminal.stream
        )
        time.sleep(self.pause)
        return obj

    def handle_scenescript(self, obj):
        """Handle a scene script event.

        :param obj: A :py:class:`~turberfield.dialogue.model.SceneScript.Folder`
            object.
        :return: The supplied object.

        """
        self.log.debug(obj.fP)
        return obj

    def handle_shot(self, obj):
        """Handle a shot event.

        :param obj: A :py:class:`~turberfield.dialogue.model.Model.Shot` object.
        :return: The supplied object.

        """
        print(
            "{t.dim}{shot}{t.normal}".format(
                shot=obj.name.capitalize(), t=self.terminal
            ),
            end="\n" * 3,
            file=self.terminal.stream
        )
        return obj

    def handle_creation(self):
        with self.con as db:
            rv = Creation(
                *SchemaBase.tables.values()
            ).run(db)
            db.commit()
            self.log.info("Created {0} tables in {1}.".format(len(rv), self.dbPath))
            return rv

    def handle_references(self, obj):
        with self.con as db:
            rv = SchemaBase.populate(db, obj)
            self.log.info("Populated {0} rows.".format(rv))
            return rv

    def __init__(
        self, terminal, dbPath=None,
        pause=pause, dwell=dwell, log=None
    ):
        self.terminal = terminal
        self.dbPath = dbPath
        self.pause = pause
        self.dwell = dwell

        self.log_manager = LogManager()
        self.log = log or self.log_manager.clone(
            self.log_manager.get_logger("main"), "turberfield.dialogue.handle"
        )

        self.shot = None
        self.con = Connection(**Connection.options(paths=[dbPath] if dbPath else []))
        self.handle_creation()

    def __call__(self, obj, *args, loop, **kwargs):
        if isinstance(obj, Model.Line):
            try:
                yield self.handle_line(obj)
            except AttributeError:
                pass
        elif isinstance(obj, Model.Audio):
            yield self.handle_audio(obj)
        elif isinstance(obj, Model.Memory):
            yield self.handle_memory(obj)
        elif isinstance(obj, Model.Property):
            yield self.handle_property(obj)
        elif isinstance(obj, Model.Shot):
            if self.shot is None or obj.scene != self.shot.scene:
                yield self.handle_scene(obj)
            if self.shot is None or obj.name != self.shot.name:
                yield self.handle_shot(obj)
            else:
                yield obj
            self.shot = obj
        elif isinstance(obj, SceneScript):
            yield self.handle_scenescript(obj)
        elif asyncio.iscoroutinefunction(obj):
            raise NotImplementedError
        elif isinstance(obj, MutableSequence):
            yield self.handle_references(obj)
        elif (obj is None or isinstance(obj, Callable)) and len(args) == 3:
            yield self.handle_interlude(obj, *args, loop=loop, **kwargs)
        else:
            yield obj

class CGIHandler(TerminalHandler):

    def handle_audio(self, obj):
        path = pkg_resources.resource_filename(obj.package, obj.resource)
        pos = path.find("lib", len(sys.prefix))
        if pos != -1:
            print(
                "event: audio",
                "data: ../{0}\n".format(path[pos:]),
                sep="\n",
                end="\n",
                file=self.terminal.stream
            )
            self.terminal.stream.flush()
        return obj

    def handle_line(self, obj):
        if obj.persona is None:
            return obj

        print(
            "event: line",
            "data: {0}\n".format(Assembly.dumps(obj)),
            sep="\n",
            end="\n",
            file=self.terminal.stream
        )
        self.terminal.stream.flush()
        interval = self.pause + self.dwell * obj.text.count(" ")
        time.sleep(interval)
        return obj

    def handle_property(self, obj):
        self.log_manager = LogManager()
        self.log = self.log_manager.get_logger("turberfield")
        self.log.info(obj)
        if obj.object is not None:
            try:
                setattr(obj.object, obj.attr, obj.val)
            except AttributeError as e:
                self.log.error(". ".join(getattr(e, "args", e) or e))

            print(
                "event: property",
                "data: {0}\n".format(Assembly.dumps(obj)),
                sep="\n",
                end="\n",
                file=self.terminal.stream
            )
            self.terminal.stream.flush()
        time.sleep(self.pause)
        return obj

    def handle_scene(self, obj):
        time.sleep(self.pause)
        return obj

    def handle_scenescript(self, obj):
        return obj

    def handle_shot(self, obj):
        return obj
