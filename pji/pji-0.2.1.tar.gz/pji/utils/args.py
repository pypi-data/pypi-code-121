import shlex


def args_split(args):
    """
    Split string args into list (just keep it when list)
    :param args: args
    :return: list args
    """
    if isinstance(args, str):
        return shlex.split(args)
    else:
        return args
