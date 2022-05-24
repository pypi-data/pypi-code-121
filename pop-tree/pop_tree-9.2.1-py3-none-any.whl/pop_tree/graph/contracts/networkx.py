# These are just for fun when viewing the graph


def pre(hub, ctx):
    ...


def pre_show(hub, ctx):
    ...


def call(hub, ctx):
    return ctx.func(*ctx.args, **ctx.kwargs)


def call_show(hub, ctx):
    return ctx.func(*ctx.args, **ctx.kwargs)


def post(hub, ctx):
    return ctx.ret


def post_show(hub, ctx):
    return ctx.ret
