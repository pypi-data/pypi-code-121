from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("picstate")
def p(url, timeout):
    return parse(url, timeout, "//p[@id='image_container']//img")
