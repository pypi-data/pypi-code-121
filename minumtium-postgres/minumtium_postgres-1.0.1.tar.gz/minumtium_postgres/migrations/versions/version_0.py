from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy.orm import sessionmaker

from .. import MigrationVersion

MIGRATION_TABLE_NAME = 'minumtium_sqlalchemy_version'


class Version0(MigrationVersion):
    def get_version(self) -> int:
        return 0

    def do(self, engine, schema=None) -> None:
        meta = MetaData(schema=schema)
        table = Table(
            MIGRATION_TABLE_NAME, meta,
            Column('version', Integer)
        )
        meta.create_all(engine)

        session = sessionmaker(bind=engine)()
        session.execute(table.insert().values({'version': 0}))
        session.commit()

    def undo(self, engine, schema=None) -> None:
        meta = MetaData()
        meta.drop_all(bind=engine, tables=[MIGRATION_TABLE_NAME])
