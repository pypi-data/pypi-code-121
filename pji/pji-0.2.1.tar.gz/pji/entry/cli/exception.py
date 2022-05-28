import click


def _click_exception_with_exit_code(name: str, message: str, exitcode: int):
    """
    create an exception
    :param name: exception name
    :param message: exception message
    :param exitcode: exitcode
    :return: new exception object
    """

    class _ClickException(click.ClickException):
        exit_code = exitcode

    return type(name, (_ClickException,), {})(message)


def _raise_exception_with_exit_code(exitcode: int, message: str = None):
    """
    raise an exception with the exit code
    :param exitcode: exitcode
    :param message: exit message
    :return:
    """
    message = message or 'exited with code {code}'.format(code=repr(exitcode))
    name = 'ExitCode{code}Exception'.format(code=repr(exitcode))
    raise _click_exception_with_exit_code(name, message, exitcode)
