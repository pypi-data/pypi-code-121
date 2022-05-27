from io import BytesIO
import re
import logging

log = logging.getLogger(__name__)


class Image(BytesIO):
    def __init__(self, content=None, filename=None):
        self.filename = filename
        self.format = filename.split(".")[-1].lower()
        super(Image, self).__init__(content)

    def save(self, filename=None, mode="wb"):
        filename = filename or self.filename
        nbytes = len(self.getvalue())
        with open(filename, mode) as f:
            f.write(self.read())
        log.info("Written {0:d} bytes to {1:s}".format(len(self.getvalue()), filename))
        return nbytes

    def _repr_png_(self):
        if self.format == "png":
            return self.getvalue()

    def _repr_jpeg_(self):
        if self.format in ["jpeg", "jpg"]:
            return self.getvalue()

    def _repr_svg_(self):
        if self.format == "svg":
            return self.getvalue()

    @classmethod
    def from_response(cls, response):
        filename = re.findall(
            "filename=(.+)", response.headers.get("content-disposition")
        )[0]
        return cls(content=response.content, filename=filename)
