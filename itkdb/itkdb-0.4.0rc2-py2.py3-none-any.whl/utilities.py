import logging
import requests
from urllib.parse import urlencode, urlparse, parse_qs
import pylibmagic  # NOQA
import magic
import os


# The background is set with 40 plus the number of the color, and the foreground with 30
# These are the sequences need to get colored ouput
def _get_color_seq(i):
    COLOUR_SEQ = "\033[1;{0:d}m"
    return COLOUR_SEQ.format(30 + i)


# See: https://stackoverflow.com/questions/287871/print-in-terminal-with-colours
# For additional colours, see: https://stackoverflow.com/questions/15580303/python-output-complex-line-with-floats-coloured-by-value
class colours:
    RESET_SEQ = "\033[0m"
    BOLD_SEQ = "\033[1m"
    UNDERLINE_SEQ = "\033[4m"
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = list(
        map(_get_color_seq, range(8))
    )


BASE_FORMAT_STRING = "[$BOLD%(asctime)s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
FORMAT_STRING = BASE_FORMAT_STRING.replace("$RESET", "").replace("$BOLD", "")
COLOUR_FORMAT_STRING = BASE_FORMAT_STRING.replace("$RESET", colours.RESET_SEQ).replace(
    "$BOLD", colours.BOLD_SEQ
)


class colouredFormatter(logging.Formatter):
    LEVELS = {
        "WARNING": colours.YELLOW,
        "INFO": colours.WHITE,
        "DEBUG": colours.BLUE,
        "CRITICAL": colours.YELLOW,
        "ERROR": colours.RED,
    }

    def __init__(self, msg, use_colour=True):
        logging.Formatter.__init__(self, msg)
        self.use_colour = use_colour

    def format(self, record):
        levelname = record.levelname
        if self.use_colour and levelname in self.LEVELS:
            levelname_colour = self.LEVELS[levelname] + levelname + colours.RESET_SEQ
            record.levelname = levelname_colour
        return logging.Formatter.format(self, record)


# Custom logger class with multiple destinations
class colouredLogger(logging.Logger):
    def __init__(self, name, use_colour=True):
        logging.Logger.__init__(self, name, logging.WARNING)
        colour_formatter = colouredFormatter(
            COLOUR_FORMAT_STRING, use_colour=use_colour
        )
        console = logging.StreamHandler()
        console.setFormatter(colour_formatter)
        self.addHandler(console)
        return


def pretty_print(req):
    request = req.prepare() if isinstance(req, requests.Request) else req
    headers = "\r\n".join(
        "{}: {}".format(k, v if k != "Authorization" else "Bearer <TOKEN>")
        for k, v in request.headers.items()
    )
    try:
        body = (
            ""
            if request.body is None
            else request.body.decode()
            if isinstance(request.body, bytes)
            else request.body
        )
    except UnicodeDecodeError:
        body = "<Decoding error>"

    return "Host: {host}\r\n{method} {path_url} HTTP/1.1\r\n{headers}\r\n\r\n{body}".format(
        host=urlparse(request.url).netloc,
        method=request.method,
        path_url=request.path_url,
        headers=headers,
        body=body,
    )


def merge_url_query_params(url: str, additional_params: dict) -> str:
    """
    Merge a url with the specified query parameters.
    """
    url_components = urlparse(url)
    original_params = parse_qs(url_components.query)
    # Before Python 3.5 you could update original_params with
    # additional_params, but here all the variables are immutable.
    merged_params = {**original_params, **additional_params}
    updated_query = urlencode(merged_params, doseq=True)
    # _replace() is how you can create a new NamedTuple with a changed field
    return url_components._replace(query=updated_query).geturl()


def get_file_components(files):
    """
    Parse the files keyword argument from a requests object which can be one of the following:

        - {key: filepointer}
        - {key: (filename, filepointer)}
        - {key: (filename, filepointer, mimetype)}
        - {key: (filename, filepointer, mimetype, additional headers)}

    Only a single key is supported, so check if there's exactly one key or raise ValueError.
    """
    files_list = requests.utils.to_key_val_list(files)

    if len(files_list) != 1:
        raise ValueError(
            f"You're creating a single attachment but you specified {len(files_list)} files."
        )
    # now need to handle the user scenarios
    key, value = files_list[0]

    # identify:
    #   filename, filepointer, mimetype, additional headers
    fn, fp, ft, fh = (None,) * 4
    if isinstance(value, (tuple, list)):
        if len(value) == 2:
            fn, fp = value
        elif len(value) == 3:
            fn, fp, ft = value
        else:
            fn, fp, ft, fh = value
    else:
        fn = requests.utils.guess_filename(value) or key
        fp = value

    # handle cases where we didn't get ft/fh specified by user
    ft = ft or get_mimetype(fn, fp)
    fh = fh or {}

    return fn, fp, ft, fh


def is_image(fn, fp):
    return get_mimetype(fn, fp).startswith("image/")


def get_mimetype(fn, fp):
    try:
        ft = magic.from_file(str(fn), mime=True)
    except FileNotFoundError:
        ft = magic.from_buffer(fp.read(2048), mime=True)
        fp.seek(0)
    return ft


def get_filesize(fn, fp):
    try:
        size = os.path.getsize(fn)
    except FileNotFoundError:
        fp.seek(0, os.SEEK_END)
        size = fp.tell()
        fp.seek(0)

    return size
