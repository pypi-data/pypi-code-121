from properties_loader import PropertiesImpl
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from properties_loader.interfaces import Properties
from postgresql_db.inmutables import _Groups, _Properties, _Config, _DDLOptions

_properties: Properties = PropertiesImpl().__dict__

_db_properties: dict = _properties.get(_Groups.BD_CORE)

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
StandardSession: Session = sessionmaker(_engine, autocommit=False)
AutoCommitSession: Session = sessionmaker(_engine, autocommit=True)