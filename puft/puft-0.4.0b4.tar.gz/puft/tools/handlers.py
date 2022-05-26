from warepy import log
from puft.errors.error import Error


def handle_wildcard_error(err: Error):
    return err.expose(), err.status_code


def handle_wildcard_builtin_error(err: Exception):
    log.debug("Test!")
    return handle_wildcard_error(Error(' ; '.join(err.args), 400))
