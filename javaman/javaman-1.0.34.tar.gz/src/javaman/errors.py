class JManError(Exception):
    pass


class JManErrorUnauthorized(JManError):
    pass


class JManErrorClient(JManError):
    pass


class JManErrorConnection(JManError):
    pass


class JManErrorApp(JManError):
    pass


class JManErrorNoContent(JManError):
    pass
