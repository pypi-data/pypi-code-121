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

from collections import defaultdict
from diapyr.util import innerclass
import ast, logging

log = logging.getLogger(__name__)

class Interpreter:

    @innerclass
    class Transform(ast.NodeTransformer):

        def __init__(self):
            self.lazycounts = defaultdict(lambda: 0)

        def visit_ClassDef(self, node):
            node.body[:] = (self.visit(statement) for statement in node.body)
            return node

        def visit_Name(self, node):
            if not isinstance(node.ctx, ast.Load):
                return node
            name = node.id
            if name not in self.globalsdict:
                return node
            self.lazycounts[name] += 1
            return ast.Call(ast.Name(self.lazyname, ast.Load()), [ast.Call(ast.Name('globals', ast.Load()), [], []), ast.Str(name)], [])

        def report(self):
            if self.lazycounts:
                log.debug("Lazy: %s", ', '.join(f"""{n}{f"*{c}" if 1 != c else ''}""" for n, c in self.lazycounts.items()))

    def __init__(self, lazyname, globalsdict):
        self.lazyname = lazyname
        self.globalsdict = globalsdict

    def __call__(self, text):
        transform = self.Transform()
        for statement in ast.parse(text).body:
            self.justexec(ast.fix_missing_locations(ast.Module([transform.visit(statement)]))) # XXX: Are locations accurate?
        transform.report()

    def justexec(self, textorast):
        exec(compile(textorast, '<text>', 'exec'), self.globalsdict)
