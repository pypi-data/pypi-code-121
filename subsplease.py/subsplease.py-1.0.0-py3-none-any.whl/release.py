class Release:
    """
    Represents a SubsPlease release.
    """
    __slots__ = (
        "title",
        "link",
        "guid",
        "release_date",
        "tags",
        "size",
        "raw"
    )

    def __init__(self, title: str, link: str, guid: str, release_date: str, tags: list, size: float, raw: dict) -> None:
        self.title = title 
        self.link = link 
        self.guid = guid 
        self.release_date = release_date
        self.tags = tags
        self.size = size
        self.raw = raw

    def __repr__(self) -> str:
        attrs = [
            ("title", self.title),
            ("link", self.link),
            ("guid", self.guid),
            ("release_date", self.release_date),
            ("tags", self.tags),
            ("size", self.size),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<{self.__class__.__name__} {joined}>"