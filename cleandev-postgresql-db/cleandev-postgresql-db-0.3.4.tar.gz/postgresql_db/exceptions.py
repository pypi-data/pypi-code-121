# Excepciones
class DdlConfigError(Exception):
    def __init__(self, msg):
        super(DdlConfigError, self).__init__(msg)


class SqlError(Exception):
    def __init__(self):
        super(SqlError, self).__init__()
