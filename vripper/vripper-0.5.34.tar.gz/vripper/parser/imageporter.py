from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("imageporter")
def p(url, timeout):
    return parse(url, timeout, "//img[@class='pic']", unavailable_phrase="No file")
