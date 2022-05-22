from vripper.parser._def import parser


@parser("photolot", is_deprecated=True)
def p(url, timeout):
    raise NotImplementedError
