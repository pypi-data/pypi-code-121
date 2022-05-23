from suanpan.app import app
from suanpan.node import node
from suanpan import g


def autoLoadSave(func):
    def main(context):
        context.args.update(app.load(node.inargs))
        if g.appType == "docker":
            context.args.update(app.handler.getArgsDictFromEnv())
        else:
            context.args.update(app._stream.getArgsDictFromEnv())
        result = func(context.args)
        app.send(result, args=node.outargs, message=context.message)

    return main


def autoLoadParam(func):
    def main(context):
        if g.appType == "docker":
            context.args.update(app.handler.getArgsDictFromEnv())
        else:
            context.args.update(app._stream.getArgsDictFromEnv())
        func(context.args)
    return main
