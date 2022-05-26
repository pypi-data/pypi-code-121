import inspect
from pathlib import Path
from typing import Iterator
from typing import Optional
from typing import TYPE_CHECKING

from _pistar.config import Config
from _pistar.filesystem import ImportMismatchError
from _pistar.filesystem import import_from_path
from _pistar.node import Collector
from _pistar.node import FileCollector
from _pistar.node import Node
from _pistar.utilities.testcase.case import TestCase
from _pistar.utilities.testcase.case import get_testcase_from_module
from _pistar.utilities.testcase.exception import ExceptionInfo
from _pistar.utilities.testcase.exception import filter_traceback

if TYPE_CHECKING:
    # Imported here due to circular import.
    from _pytest.main import Session


class Module(FileCollector):
    """
    Collector for Clazz collector.
    """

    @property
    def obj(self):
        obj = getattr(self, "_obj", None)

        if obj is None:
            obj = self._import_case_module()
            setattr(self, "_obj", obj)

        return obj

    def collect(self) -> Iterator[Collector]:
        # collect the class finally

        if self.obj is None:
            return []

        testcase = get_testcase_from_module(self.obj, str(self.fspath.absolute()))

        if not testcase:
            return []
        name = testcase.__name__
        return [Clazz.from_parent(self, name=name, obj=testcase)]

    def _import_case_module(self):
        """
        Import the module from given Path.

        We assume this function are called only once per module.
        Raised CollectorError with custom message if necessary.
        """
        try:
            module = import_from_path(self.fspath)
        except SyntaxError as e:
            raise self.CollectError(ExceptionInfo.from_current().exc_only()) from e

        except ImportMismatchError as e:

            raise self.CollectError(
                "import mismatch:\n"
                "Module %r has this __file__ attribute:\n"
                "  %s\n"
                "which is different to the file we want to collect:\n"
                "  %s\n"
                "NOTE: use a unique basename for your modules,\n"
                "or use package to organize your test structure." % e.args
            ) from e

        except ImportError as e:
            exc_info = ExceptionInfo.from_current()
            exc_info.traceback = exc_info.traceback.filter_from(filter_traceback)

            error_repr = self.error_repr(exc_info)
            msg = (
                f"ImportError when importing module: \n'{self.fspath}'.\n"
                f"Hint: make sure the module have valid Python names.\n"
                f"Details:\n{str(error_repr)} "
            )
            raise self.CollectError(msg) from e

        return module


def hasinit(obj: object) -> bool:
    init: object = getattr(obj, "__init__", None)
    return init != object.__init__


def hasnew(obj: object) -> bool:
    new: object = getattr(obj, "__new__", None)
    return new != object.__new__


def has_para_init(obj: object) -> bool:
    if hasinit(obj):
        new = getattr(obj, "__init__", None)
        sig = inspect.signature(new)
        return len(sig.parameters) > 1
    return False


class Clazz(Collector):
    """
    Clazz Collector for TestCase.

    The Collector collects the TestCase finally.
    """

    def __init__(
        self,
        name: str,
        fspath: Optional[Path] = None,
        obj=None,
        parent: Optional["Node"] = None,
        config: Optional["Config"] = None,
        session: Optional["Session"] = None,
    ) -> None:
        super().__init__(
            name=name,
            fspath=fspath,
            parent=parent,
            config=config,
            session=session,
        )

        self._obj = obj

    @property
    def obj(self):

        return self._obj

    @classmethod
    def from_parent(cls, parent: "Node", *, name, obj, **kwargs):
        return super().from_parent(parent=parent, name=name, obj=obj, **kwargs)

    def collect(self) -> Iterator[TestCase]:
        # collect the class finally

        if self.obj is None:
            return []

        if has_para_init(self.obj) or hasnew(self.obj):
            msg = (
                f"Warning: cannot collect case {self.name}\n"
                f"from {self.fspath},\n"
                f"which has a parameterized __init__ or __new__ constructor."
            )

            raise self.CollectError(msg)

        # notice TeatCase's parent is Module.
        return [TestCase.from_parent(self.parent, name=self.name, obj=self.obj)]
