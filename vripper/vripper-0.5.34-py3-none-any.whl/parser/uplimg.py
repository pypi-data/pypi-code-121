from vripper.parser._def import parser


@parser("uplimg", is_deprecated=True)
def p(url, timeout):
    raise NotImplementedError
