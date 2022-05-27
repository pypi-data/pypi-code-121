from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import uuid
import re
import music_tag


@dataclass
class Track:
    id: str  # 32-character UUID
    path: Path
    title: Optional[str]
    artist: Optional[str]

    @classmethod
    def from_file(cls, file: Path):
        """
        Initialize a Track from a file. Adds a UUID to the file name if it doesn't already have one.
        """

        def add_uuid_to_file(id: str) -> Path:
            """Renames the file to include a UUID. Returns the new file path."""
            target = file.parent / f"{file.stem}-{id}{file.suffix}"
            file.rename(target)
            return target

        id = cls.file_uuid(file.name)
        if id is None:
            id = uuid.uuid4().hex
            file = add_uuid_to_file(id)

        tags = music_tag.load_file(file)
        return cls(
            id=id, path=file, title=str(tags["title"]), artist=str(tags["artist"])
        )

    @staticmethod
    def file_uuid(file_name: str) -> Optional[str]:
        """
        Check if filename is formatted as `.*-<uuid>.<ext>`
        uuid is a 32-character hexadecimal string
        """

        regex = re.compile(r"^.*-([0-9a-f]{32}).*$")
        match = regex.match(file_name)
        if match:
            return match.group(1)
        else:
            return None

    def update_metadata(self, metadata: dict):
        """
        Adds the track metadata with the given dictionary.
        """

        self.title = metadata.get("title") or self.title
        self.artist = metadata.get("artist") or self.artist

        tags = music_tag.load_file(self.path)
        tags["tracktitle"] = self.title
        tags["artist"] = self.artist
        tags.save()
