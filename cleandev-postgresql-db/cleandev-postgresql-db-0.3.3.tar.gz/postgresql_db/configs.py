from properties_loader import Properties
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from postgresql_db.inmutables import _Groups, _Properties, _Config, _DDLOptions

_db_properties: dict = Properties().__dict__.get(_Groups.BD_CORE)
_default_row_for_page: int = 25

_ddl_auto_options: list = [
    str(_DDLOptions.CREATE),
    str(_DDLOptions.DROP_CREATE),
    str(_DDLOptions.TEST)
]

_config: dict = {
    str(_Config.DDL_AUTO_VALUE): _db_properties.get(_Properties.DDL_AUTO),
    str(_Config.NAME_SHCEMA_MODULE): _db_properties.get(_Properties.PATH_MODULE_SCHEMA)
}



_url_connection: str = _db_properties.get(_Properties.URL_CONNECTION)
_engine = create_engine(_url_connection)

# Factoria de sessiones
StandartSession: Session = sessionmaker(_engine, autocommit=False)
AutoCommitSession: Session = sessionmaker(_engine, autocommit=True)