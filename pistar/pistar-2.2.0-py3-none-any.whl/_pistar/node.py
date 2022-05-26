import os
from pathlib import Path
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

from _pistar.config import Config
from _pistar.utilities.testcase.exception import ExcInfoFormatter
from _pistar.utilities.testcase.exception import ExceptionInfo
from _pistar.utilities.testcase.exception import TraceBack
from _pistar.utilities.testcase.repr import ExceptionRepr

if TYPE_CHECKING:
    from _pistar.main import Session

SEP = "/"


class BanInit(type):
    """
    A meta-class for Node.
    Forbid direct construct of the class with this meta-class.
    """

    def __call__(cls, *k, **kw):
        name = cls.__name__
        msg = (
            f"Can not construct class {name} directly"
            f"please use {name}.from_parent.\n"
        )

        raise Exception(msg)

    def _create(self, *k, **kw):
        return super().__call__(*k, **kw)


class Node(metaclass=BanInit):
    """
    Base class for all Collector and TestCase.

    The Node describes the collection thee of test cases.
    All Collectors have a children,TestCase is the leaf class.
    """

    __slots__ = (
        # the name for this node
        "name",
        # the parent node,can be None
        "parent",
        # the config object for this execution
        "config",
        # the file system path for collector
        "fspath",
        # the session object for this execution
        "session",
        # the id of nodes,like foo/bar.py::Test
        "_nodeid",
        # add __dict__ into __slots__ to make it available
        "__dict__",
    )

    def __init__(
        self,
        name: str,
        fspath: Optional[Path] = None,
        parent: Optional["Node"] = None,
        config: Optional["Config"] = None,
        session: Optional["Session"] = None,
        nodeid: Optional[str] = None,
    ) -> None:
        self.name = name

        self.parent = parent

        if config:
            self.config: Config = config
        else:
            if not parent:
                raise TypeError("config or parent must be provided at least one.")

            self.config: Config = parent.config

        if session:
            self.session = session

        else:
            if not parent:
                raise TypeError("session or parent must be provided at least one.")

            self.session = parent.session

        self.fspath = fspath or getattr(parent, "fspath", None)

        if nodeid is not None:
            self._nodeid = nodeid
        else:
            if not parent:
                raise TypeError("nodeid or parent must be provided at least one.")

            self._nodeid = f"{self.parent.nodeid}::{self.name}"

    @property
    def nodeid(self) -> str:
        return self._nodeid

    @classmethod
    def from_parent(cls, parent: "Node", **kwargs):

        return cls._create(parent=parent, **kwargs)


class Collector(Node):
    """
    This is the abstract class for Collector.

    Collector will collect and return its sub-collector.For example,
    Module collector collect Clazz collector.Clazz collector returns
    TestCase Finally.

    Some Error during collection are wrapped as CollectError which
    contains a custom message.
    """

    class CollectError(Exception):
        """An error during collection, contains a custom message."""

    def collect(self):
        raise NotImplementedError()

    def error_repr(
        self, exc_info: ExceptionInfo[BaseException]
    ) -> Union[str, ExceptionRepr]:
        """
        Get error message during the collection phase.
        """
        # only the last traceback can be formatted.
        if isinstance(exc_info.value, self.CollectError):
            exc = exc_info.value
            return str(exc.args[0])

        tb = TraceBack([exc_info.traceback[-1]])
        exc_info.traceback = tb
        fmt = ExcInfoFormatter(exc_info=exc_info, func=None)

        error_repr = fmt.repr_exception()

        return error_repr


class FileCollector(Collector):
    def __init__(
        self,
        fspath: Path,
        name: Optional[str] = None,
        parent: Optional["Node"] = None,
        config: Optional["Config"] = None,
        session: Optional["Session"] = None,
        nodeid: Optional[str] = None,
    ):
        if name is None:
            name = fspath.name

            if parent:
                try:
                    rel_path = fspath.relative_to(parent.fspath)
                except ValueError:
                    pass
                else:
                    name = str(rel_path)

                name = name.replace(os.sep, SEP)

        if session is None:
            session = parent.session

        if nodeid is None:
            try:
                nodeid = str(fspath.relative_to(session.config.rootpath))
            except ValueError:
                nodeid = ""
            if nodeid == ".":
                nodeid = ""
            if os.sep != SEP:
                nodeid = nodeid.replace(os.sep, SEP)

        super().__init__(
            name=name,
            fspath=fspath,
            parent=parent,
            config=config,
            session=session,
            nodeid=nodeid,
        )
