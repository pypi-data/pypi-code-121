import os
import posixpath
from urllib.parse import unquote, urlsplit


def filename_from_url(url):
    """Return basename corresponding to url.
    >>> print(url2filename('http://example.com/path/to/file%C3%80?opt=1'))
    fileÀ
    >>> print(url2filename('http://example.com/slash%2fname')) # '/' in name
    Traceback (most recent call last):
    ...
    ValueError
    """

    urlpath = urlsplit(url).path
    basename = posixpath.basename(unquote(urlpath))
    if (
        os.path.basename(basename) != basename
        or unquote(posixpath.basename(urlpath)) != basename
    ):
        raise ValueError  # reject '%2f' or 'dir%5Cbasename.ext' on Windows

    return basename


__all__ = ["filename_from_url"]
