from sqlalchemy import TypeDecorator
from sqlalchemy import cast
from sqlalchemy.sql.sqltypes import LargeBinary


class PeekLargeBinary(TypeDecorator):
    """Peek Large Binary"""

    impl = LargeBinary

    def bind_expression(self, bindvalue):
        return cast(bindvalue, LargeBinary)
