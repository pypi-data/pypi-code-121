from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("imgbox.com")
def p(url, timeout):
    return parse(
        url, timeout, "//img[@id='img']", unavailable_phrase="The image in question does not exist"
    )
