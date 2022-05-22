from vripper.parser._common import parse
from vripper.parser._def import parser


# imgflare uses google captcha
@parser("imgflare", is_deprecated=True)
def p(url, timeout):
    return parse(url, timeout, "//img[@id='source']")
