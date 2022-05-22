from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("imagetwist")
def p(url, timeout):
    return parse(
        url, timeout, xpath_expr="//img[contains(@class, 'img-responsive')]",
        unavailable_phrase="The image you were looking for could not be found"
    )
