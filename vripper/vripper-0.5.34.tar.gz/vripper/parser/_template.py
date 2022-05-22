from vripper.parser._common import parse
from vripper.parser._def import parser


# @parser("")
def p(url, timeout):
    return parse(url, timeout, "//img")
