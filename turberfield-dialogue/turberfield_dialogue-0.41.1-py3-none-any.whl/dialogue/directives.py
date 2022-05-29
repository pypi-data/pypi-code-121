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


import importlib.util
import os.path
import sys

import docutils.nodes
from docutils.nodes import BackLinkable, Element, General, Inline
from docutils.nodes import Labeled, Targetable, TextElement
import docutils.parsers.rst


class Pathfinder:

    @staticmethod
    def string_import(arg, relative=False, sep=None):
        arg = arg.strip()
        if not arg:
            return None

        try:
            return int(arg)
        except ValueError:
            pass

        bits = arg.split(".")
        if sep is None:
            index = min(n for n, i in enumerate(bits) if i and i[0].isupper())
        elif sep != ".":
            index = min(n for n, i in enumerate(bits) if i and sep in i) + 1
            bits = arg.replace(sep, ".").split(".")
        else:
            index = -1

        start = 1 if relative else 0
        modName = ".".join(bits[start:index])
        try:
            # Try importing an installed module
            mod = importlib.import_module(modName)
        except ImportError:
            # Try importing a source file at this location
            mN = bits[index - 1]
            spec = importlib.util.spec_from_file_location(
                mN,
                os.path.abspath(modName.replace(".", os.sep)) + ".py"
            )
            if spec is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[mN] = mod

        obj = mod
        for name in bits[index:]:
            obj = getattr(obj, name)

        return obj

    @staticmethod
    def string_split(arg):
        return arg.split()


class Entity(docutils.parsers.rst.Directive):

    # See http://docutils.sourceforge.net/docutils/parsers/rst/directives/parts.py

    class Declaration(Pathfinder, General, BackLinkable, Element, Labeled, Targetable):
        pass

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "states": Declaration.string_split,
        "types": Declaration.string_split,
        "roles": Declaration.string_split,
    }
    has_content = True
    node_class = Declaration


    def run(self):
        kwargs = {
            i: getattr(self, i, None)
            for i in (
                "name", "arguments", "options", "content", "lineno", "content_offset",
                "block_text", "state", "state_machine"
            )
        }
        node = self.node_class(**kwargs)
        name = docutils.nodes.fully_normalize_name(self.arguments[0])
        node["names"] = list(set(node["names"]) | {name})
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]

class Property(docutils.parsers.rst.Directive):

    class Getter(Inline, TextElement, Pathfinder):
        pass

    class Setter(Element, Inline, Pathfinder):
        pass

    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}
    has_content = False

    def run(self):
        kwargs = {
            i: getattr(self, i, None)
            for i in (
                "name", "arguments", "options", "content", "lineno", "content_offset",
                "block_text", "state", "state_machine"
            )
        }
        if len(self.arguments) == 1:
            node = Property.Getter(**kwargs)
        else:
            node = Property.Setter(**kwargs)
        return [node]

class Condition(docutils.parsers.rst.Directive):

    class Evaluation(Element, Inline, Pathfinder):
        pass

    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = False

    def run(self):
        kwargs = {
            i: getattr(self, i, None)
            for i in (
                "name", "arguments", "options", "content", "lineno", "content_offset",
                "block_text", "state", "state_machine"
            )
        }
        node = Condition.Evaluation(**kwargs)
        return [node]

class FX(docutils.parsers.rst.Directive):

    class Cue(Element, Inline, Pathfinder):
        pass

    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "duration": int,
        "height": int,
        "label": str,
        "loop": int,
        "offset": int,
        "poster": str,
        "url": str,
        "width": int,
    }
    has_content = False

    def run(self):
        kwargs = {
            i: getattr(self, i, None)
            for i in (
                "name", "arguments", "options", "content", "lineno", "content_offset",
                "block_text", "state", "state_machine"
            )
        }
        node = FX.Cue(**kwargs)
        return [node]

class Memory(docutils.parsers.rst.Directive):

    class Definition(Inline, TextElement, Pathfinder):
        pass

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {"subject": str, "object": str}
    has_content = True

    def run(self):
        kwargs = {
            i: getattr(self, i, None)
            for i in (
                "name", "arguments", "options", "content", "lineno", "content_offset",
                "block_text", "state", "state_machine"
            )
        }
        node = Memory.Definition(**kwargs)
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
