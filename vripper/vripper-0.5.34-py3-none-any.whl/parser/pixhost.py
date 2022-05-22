from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("pixhost.to")
def p(url, timeout):
    return parse(url, timeout, "//img[@id='image']", unavailable_phrase="Picture doesn't exist")
