import typing

import sqlalchemy as sa
from sqlalchemy.orm.decl_api import declared_attr
from sqlalchemy.sql.functions import current_timestamp

from .utils import pluralize


class SoftDeletable:
    """A soft-deletable model mixing.

    This adds a `is_deleted` column to mark the instances as deleted.

    >>> from sqlalchemy.orm.decl_api import declarative_base
    >>> from sqlalchemy import Column, Integer
    >>> Base = declarative_base()
    >>> class Item(SoftDeletable, Base):
    ...     __tablename__ = 'items'
    ...     id = Column(Integer, primary_key=True, autoincrement=True)
    ...
    >>> item = Item()
    >>> item.is_removed

    >>> item.mark_removed()

    >>> item.is_removed
    True
    >>> item.mark_removed()
    Traceback (most recent call last):
      ...
    AssertionError: ...
    >>> item.restore()

    >>> item.is_removed
    False
    >>> item.restore()
    Traceback (most recent call last):
      ...
    AssertionError: ...
    >>>
    """

    __abstract__ = True

    is_removed = sa.Column(
        sa.Boolean,
        index=True,
        nullable=False,
        server_default=sa.false(),
        comment="Soft deletion flag.",
    )

    def mark_removed(self):
        assert not self.is_removed, "Already marked."
        self.is_removed = True

    def restore(self):
        assert self.is_removed, "Not removed."
        self.is_removed = False


class Timestamps:
    """Adds timestamp fields.

    >>> from sqlalchemy import Column, Integer
    >>> from sqlalchemy.orm.decl_api import declarative_base
    >>> Base = declarative_base()
    >>> class Item(Timestamps, Base):
    ...     __tablename__ = 'items'
    ...     id = Column(Integer, primary_key=True, autoincrement=True)
    ...
    >>> item=Item()
    >>> item.created

    >>> item.updated

    >>>
    """

    __abstract__ = True

    created = sa.Column(
        sa.TIMESTAMP,
        default=current_timestamp(),
        nullable=False,
        comment="When a row were added.",
    )
    updated = sa.Column(
        sa.TIMESTAMP,
        onupdate=current_timestamp(),
        comment="Last row update date and time.",
    )

    def touch(self):
        """Update the `updated` timestamp.

        This just sets the `updated` field to the `current_timestamp` function.

        >>> from sqlalchemy import Column, Integer
        >>> from sqlalchemy.orm.decl_api import declarative_base
        >>> Base = declarative_base()
        >>> class Item(Timestamps, Base):
        ...     __tablename__ = 'items'
        ...     id = Column(Integer, primary_key=True, autoincrement=True)
        ...
        >>> item=Item()
        >>> item.touch()
        >>> item.updated
        <sqlalchemy.sql.functions.current_timestamp at ...>
        >>>
        """
        self.updated = current_timestamp()


class WithPK:
    """Adds a primary key.

    >>> from sqlalchemy.orm.decl_api import declarative_base

    >>> Base = declarative_base()

    >>> class SubWithPK(WithPK, Base):
    ...     __tablename__='subwithpk'
    ...
    >>> SubWithPK.id.name
    'id'
    >>>
    """

    __abstract__ = True

    type_: typing.ClassVar[sa.types.TypeEngine] = sa.Integer  # type: ignore
    autoincrement: bool = True

    @declared_attr
    def id(cls) -> sa.Column:
        return sa.Column(
            "id", cls.type_, primary_key=True, autoincrement=cls.autoincrement
        )


class Autonamed:
    """Auto-name table.

    >>> from sqlalchemy.orm.decl_api import declarative_base
    >>> Base = declarative_base()
    >>> class Prop(Autonamed, Base):
    ...     id=sa.Column(sa.Integer, primary_key=True)
    ...
    >>> Prop.__table__.name
    'props'
    >>>
    """

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return pluralize(cls.__name__)
