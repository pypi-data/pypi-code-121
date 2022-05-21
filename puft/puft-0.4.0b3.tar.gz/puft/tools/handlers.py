from puft.errors.error import Error


def handle_wildcard_error(err: Error):
    return err.expose()
