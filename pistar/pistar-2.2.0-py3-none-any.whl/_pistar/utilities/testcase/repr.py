from io import StringIO
from typing import Sequence

import attr

from _pistar.terminal import TerminalWriter


@attr.s(eq=False)
class BaseRepr:
    def __str__(self):
        io = StringIO()
        w = TerminalWriter(io)
        self.gen_repr(w)
        return io.getvalue()

    def gen_repr(self, writer: TerminalWriter):
        raise NotImplementedError()


@attr.s(eq=False, auto_attribs=True)
class ExceptionRepr(BaseRepr):
    reprs: "ItemRepr"
    location: "LocationRepr"
    parameter: "ParamRepr"

    def gen_repr(self, writer: TerminalWriter):
        self.location.gen_repr(writer)
        self.reprs.gen_repr(writer)
        self.parameter.gen_repr(writer)


@attr.s(eq=False)
class LocationRepr(BaseRepr):
    path = attr.ib(type=str, converter=str)
    lineno = attr.ib(type=int)
    exception = attr.ib(type=str)

    def gen_repr(self, writer: TerminalWriter):
        writer.line(f"{self.path}:{self.lineno} {self.exception}")


@attr.s(eq=False)
class ItemRepr(BaseRepr):
    lines = attr.ib(type=Sequence[str])
    errors = attr.ib(type=str)

    def gen_repr(self, writer: TerminalWriter):
        if not self.lines:
            return

        for line in self.lines:
            writer.line(line)
        if self.errors:
            writer.line(self.errors)


@attr.s(eq=False)
class ParamRepr(BaseRepr):
    parameters = attr.ib(type=str)
    cur_param = attr.ib(type=list)

    def gen_repr(self, writer: TerminalWriter):
        if self.cur_param:
            writer.line("")
            writer.line(f"{self.parameters}")


@attr.s(eq=False)
class TimeoutRepr(BaseRepr):
    timeout_info = attr.ib(type=str)

    def gen_repr(self, writer: TerminalWriter):
        writer.line("")
        writer.line(f"{self.timeout_info}")


@attr.s(eq=False)
class LinkRepr(BaseRepr):
    path = attr.ib(type=str)
    lineno = attr.ib(type=str)
    current_source = attr.ib(type=str)

    def gen_repr(self, writer: TerminalWriter):
        writer.line(f"{self.path}:{self.lineno}")
        if self.current_source:
            writer.line(self.current_source)


@attr.s(eq=False)
class AssertRepr(ItemRepr):
    def gen_repr(self, writer: TerminalWriter):
        pass
