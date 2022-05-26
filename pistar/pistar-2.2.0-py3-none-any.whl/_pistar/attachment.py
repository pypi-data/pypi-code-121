import inspect
from pathlib import Path
from types import FrameType
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from _pistar import BaseTestCase
from _pistar.pistar_pytest.models import Attachment
from _pistar.pistar_pytest.models import AttachmentType


def _possible_class(frame: FrameType) -> Tuple[Optional[BaseTestCase], FrameType]:
    """
    Get possible test case class and its frame.

    Return possible class and its frame.Class may be None if there is no frame
    contains a BaseTestCase parameter,which means the attach function was not
    called inside the teststep.
    """
    while frame:
        local = list(frame.f_locals.keys())
        if local:
            attr = frame.f_locals.get("self", None)
            if isinstance(attr, BaseTestCase):
                return attr, frame
        frame = frame.f_back

    return None, frame


def _attach(clazz: BaseTestCase, name: str) -> List[Attachment]:
    attaches: Dict[str, List[Attachment]] = getattr(clazz, "_attaches", None)
    empty: List[Attachment] = []
    if attaches is None:
        setattr(clazz, "_attaches", {name: empty})
        return empty

    possible_list = attaches.get(name)

    if possible_list:
        return possible_list

    attaches.setdefault(name, empty)

    return empty


class Attach:
    """
    Attach a user-defined file/table to a testcase's result information.

    The file/table will be collected by CloudTest or local report as supplements
    to describe the test step additionally.Make sure the file exist or readable.

    Use attach in test step (including setup,teardown,failure) only.For example:

    @teststep
    def foo(self):
        self.assert_that(1).is_equal_to(1)

        pistar.attach.file(source="foo.py",name="foo")

    """
    clazz = None

    def file(
        self,
        source: Union[str, Path],
        attachment_type: AttachmentType,
        name: Optional[str] = None,
    ):

        # ignore current frame
        last_frame = inspect.currentframe().f_back

        self.clazz, frame = _possible_class(last_frame)

        if self.clazz is None:
            raise Exception(
                "Attachment misused;\n"
                "Use pistar.attach.file in test step (or setup,teardown,failure)."
            )

        path = Path(source).resolve().absolute()
        if not path.exists():
            raise Exception("File not Found!")

        if not isinstance(attachment_type, AttachmentType):
            raise TypeError("except type of argument attachment_type is AttachmentType,"
                            f" not {attachment_type.__class__.__name__}")

        if name is None:
            name = path.name

        if not isinstance(name, str):
            raise TypeError("except type of argument name is str,"
                            f" not {name.__class__.__name__}")

        att = Attachment(path=str(path), name=name, type=attachment_type.mime_type)
        attaches = _attach(self.clazz, frame.f_code.co_name)

        attaches.append(att)

    def get_files(self, step_name: str = None) -> Union[List, Dict]:
        attaches: Dict[str, List[Attachment]] = getattr(self.clazz, "_attaches", None)
        if step_name:
            return attaches.get(step_name, None)
        else:
            return attaches


attach = Attach()
