from commmons import get_host_url

from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("nlegs.com")
def nleg_parser(url, timeout):
    path = parse(url, timeout, "//img[@class='img-res']")
    return get_host_url(url) + path


@parser("uuleg.com")
def uuleg_parser(url, timeout):
    return nleg_parser(url, timeout)


@parser("honeyleg.com")
def honeyleg_parser(url, timeout):
    return nleg_parser(url, timeout)


@parser("legbabe.com")
def legbabe_parser(url, timeout):
    return nleg_parser(url, timeout)


@parser("leg.cx")
def legcx_parser(url, timeout):
    return nleg_parser(url, timeout)
