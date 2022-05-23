from trame_markdown.widgets.markdown import *


def initialize(server):
    from trame_markdown import module

    server.enable_module(module)
