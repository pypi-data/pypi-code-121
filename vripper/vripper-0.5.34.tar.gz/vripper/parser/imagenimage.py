from vripper.parser._common import parse
from vripper.parser._def import parser


@parser("imagenimage")
def p(url, timeout):
    return parse(url, timeout, "//img[contains(@class, 'img-responsive')]")
