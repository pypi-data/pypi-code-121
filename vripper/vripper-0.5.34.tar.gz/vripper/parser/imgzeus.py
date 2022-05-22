from vripper.parser._def import parser


@parser("imgzeus.com", is_deprecated=True)
def p():
    raise NotImplementedError
