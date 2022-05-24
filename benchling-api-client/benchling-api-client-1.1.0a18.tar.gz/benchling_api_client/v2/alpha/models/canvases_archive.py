from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.canvases_archive_reason import CanvasesArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="CanvasesArchive")


@attr.s(auto_attribs=True, repr=False)
class CanvasesArchive:
    """  """

    _canvas_ids: List[str]
    _reason: CanvasesArchiveReason

    def __repr__(self):
        fields = []
        fields.append("canvas_ids={}".format(repr(self._canvas_ids)))
        fields.append("reason={}".format(repr(self._reason)))
        return "CanvasesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        canvas_ids = self._canvas_ids

        reason = self._reason.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "canvasIds": canvas_ids,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_canvas_ids() -> List[str]:
            canvas_ids = cast(List[str], d.pop("canvasIds"))

            return canvas_ids

        canvas_ids = get_canvas_ids() if "canvasIds" in d else cast(List[str], UNSET)

        def get_reason() -> CanvasesArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = CanvasesArchiveReason(_reason)
            except ValueError:
                reason = CanvasesArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(CanvasesArchiveReason, UNSET)

        canvases_archive = cls(
            canvas_ids=canvas_ids,
            reason=reason,
        )

        return canvases_archive

    @property
    def canvas_ids(self) -> List[str]:
        """ Array of canvas IDs """
        if isinstance(self._canvas_ids, Unset):
            raise NotPresentError(self, "canvas_ids")
        return self._canvas_ids

    @canvas_ids.setter
    def canvas_ids(self, value: List[str]) -> None:
        self._canvas_ids = value

    @property
    def reason(self) -> CanvasesArchiveReason:
        """ Reason that apps are being archived. Actual reason enum varies by tenant. """
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: CanvasesArchiveReason) -> None:
        self._reason = value
