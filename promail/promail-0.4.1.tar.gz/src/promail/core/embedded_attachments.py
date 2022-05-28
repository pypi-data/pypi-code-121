"""EmbeddedAttachments."""

from email.utils import make_msgid


class EmbeddedAttachments:
    """EmbeddedAttachments in Email.

    EmbeddedAttachments are used to include your local files
    in the body of an email.
    """

    def __init__(self, filepath):
        """Initializes EmbeddedAttachments."""
        self.filepath = filepath
        self._cid = make_msgid(domain="promail")

    @property
    def cid(self):
        """Returns unique identifier for reference in email."""
        return self._cid

    def __str__(self):
        """Returns CID stripped of brackets to be used as  src={cid}."""
        return self._cid[1:-1]

    def read(self):
        """Returns Byte info of file."""
        with open(self.filepath, "rb") as file:
            return file.read()
