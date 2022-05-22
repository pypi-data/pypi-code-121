from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("imagezilla")
def p(url, timeout):
    return parse(url, timeout, "//img[@id='photo']", unavailable_phrase="The requested image does not exist")
