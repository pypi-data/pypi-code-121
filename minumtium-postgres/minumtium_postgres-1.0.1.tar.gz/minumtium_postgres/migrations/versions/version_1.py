from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Unicode

from .. import MigrationVersion

USERS_TABLE_NAME = 'users'
POSTS_TABLE_NAME = 'posts'


class Version1(MigrationVersion):
    def get_version(self) -> int:
        return 1

    def do(self, engine, schema=None) -> None:
        meta = MetaData(schema=schema)

        Table(
            USERS_TABLE_NAME, meta,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('username', String(128), nullable=False),
            Column('encrypted_password', String(512), nullable=False)
        )

        Table(
            POSTS_TABLE_NAME, meta,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('title', String(256), nullable=False),
            Column('author', String(128), nullable=False),
            Column('body', Unicode()),
            Column('timestamp', DateTime())
        )

        meta.create_all(engine)

    def undo(self, engine, schema=None) -> None:
        meta = MetaData(schema=schema)
        meta.drop_all(bind=engine, tables=['users, posts'])
