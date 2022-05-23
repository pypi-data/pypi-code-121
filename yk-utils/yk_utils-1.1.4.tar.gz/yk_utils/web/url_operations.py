""" URL Operations Module """
from urllib.parse import urlparse, urljoin
from yk_utils.web.exceptions import BadUrl


def get_url_hostname(url: str) -> str:
    """
    Gets the hostname of the given url
    :param url: URL
    :return: URL hostname
    """
    return urlparse(url).hostname


def is_valid_url(url: str) -> bool:
    """
    Checks the format validity of the given url.
    :param url: url
    :return: True if valid. False otherwise.
    """
    result = urlparse(url)
    return all([result.scheme, result.netloc])


def build_url(base: str, relative: str = "") -> str:
    """
    Build both base and relative urls into one and checks for its validity.
    If not valid will raise BadUrl exception.
    :param base: base url path to be specified
    :param relative: relative path to be specified
    :return:
    """
    absolute = urljoin(base, relative)
    if is_valid_url(absolute):
        return absolute
    raise BadUrl(f"Bad URL '{absolute}'")
