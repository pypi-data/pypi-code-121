from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("damimage", is_deprecated=True)
def p(url, timeout):
    return parse(url, timeout, "//img[@class='centred']")
