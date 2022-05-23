"""
*
 *  Copyright ServerTribe HQ Pty Ltd 2021
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  ServerTribe HQ Pty Ltd
 *
"""
from pathlib import Path
from typing import Optional
from typing import Union

from vortex.Tuple import PolymorphicTupleTypeFieldArg
from vortex.Tuple import TupleField

from attune_project_api import ObjectStorageContext
from attune_project_api.ObjectStorageContext import ArchiveFileContent
from attune_project_api.ObjectStorageContext import ArchiveFileInfo
from attune_project_api.ObjectStorageContext import VersionedFileContent
from attune_project_api.ObjectStorageContext import VersionedFileInfo
from attune_project_api.StorageTuple import ItemStorageGroupEnum
from attune_project_api.StorageTuple import StorageTuple


@ObjectStorageContext.registerItemClass
class FileArchiveTuple(StorageTuple):
    """File Archive Tuple

    This is the base archive tuple.
    An archive (displayed as "Files" in the UI) is just that, an archive

    """

    __tupleArgs__ = (PolymorphicTupleTypeFieldArg("type"),)
    __group__ = ItemStorageGroupEnum.FileArchive

    key: str = TupleField()
    name: str = TupleField()
    type: str = TupleField()
    comment: Optional[str] = TupleField()

    #: This is for the user interface only
    uiData: Optional[dict] = TupleField({}, jsonExclude=True)

    @classmethod
    @property
    def niceName(cls) -> str:
        # This is meant to be an abstract method
        raise NotImplementedError()

    @property
    def listFiles(self) -> list[Union[ArchiveFileInfo, VersionedFileInfo]]:
        # This is meant to be an abstract method
        raise NotImplementedError()

    @property
    def getFileContent(
        self, path: Path
    ) -> Union[list[ArchiveFileContent], list[VersionedFileContent]]:
        # This is meant to be an abstract method
        raise NotImplementedError()

    def _makeFileName(self, formatKey: str) -> str:
        allowedLetters = {chr(i) for i in range(0x30, 0x39)}  # 0-9
        allowedLetters |= {chr(i) for i in range(0x41, 0x5A)}  # A-Z
        allowedLetters |= {chr(i) for i in range(0x61, 0x7A)}  # a-z
        allowedLetters.add("_")

        name = self.name.replace(" ", "_")
        name = "".join([c for c in name if c in allowedLetters])

        return f"{name}.{formatKey}"
