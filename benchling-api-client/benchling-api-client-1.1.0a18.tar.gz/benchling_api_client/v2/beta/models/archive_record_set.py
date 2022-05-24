from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="ArchiveRecordSet")


@attr.s(auto_attribs=True, repr=False)
class ArchiveRecordSet:
    """ Currently, we only support setting a null value for archiveRecord, which unarchives the item """

    def __repr__(self):
        fields = []
        return "ArchiveRecordSet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        src_dict.copy()
        archive_record_set = cls()

        return archive_record_set
