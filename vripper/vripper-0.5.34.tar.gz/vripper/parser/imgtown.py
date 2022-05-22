from vripper.parser._def import parser


@parser("imgtown", is_deprecated=True)
def p(url, timeout):
    """This website requires JS rendering"""
    raise NotImplementedError
