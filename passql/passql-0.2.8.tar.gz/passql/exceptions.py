__all__ = (
    'SqlException',
    'QueryException',
)


class SqlException(Exception):
    """ Sql building/parsing error. """
    __slots__ = ()

    def __init__(self, message: str):
        self.args = (message, )

    @property
    def message(self):
        return self.args[0]


class QueryException(Exception):
    """ Query to database error. """
    __slots__ = ()

    def __init__(self, sql: str, message: str):
        self.args = (message, sql)

    @property
    def message(self):
        return self.args[0]

    @property
    def sql(self):
        return self.args[1]
