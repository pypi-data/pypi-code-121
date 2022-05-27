from io import BytesIO
import re
import logging

log = logging.getLogger(__name__)


class Text(BytesIO):
    def __init__(self, content=None, filename=None):
        self.filename = filename
        self.format = filename.split(".")[-1].lower()
        super(Text, self).__init__(content)

    def save(self, filename=None, mode="wb"):
        filename = filename or self.filename
        nbytes = len(self.getvalue())
        with open(filename, mode) as f:
            f.write(self.read())
        log.info("Written {0:d} bytes to {1:s}".format(len(self.getvalue()), filename))
        return nbytes

    def _repr_html_(self):
        return (b"<pre>" + self.getvalue() + b"</pre>").decode("utf-8")

    @classmethod
    def from_response(cls, response):
        filename = re.findall(
            "filename=(.+)", response.headers.get("content-disposition")
        )[0]
        return cls(content=response.content, filename=filename)
