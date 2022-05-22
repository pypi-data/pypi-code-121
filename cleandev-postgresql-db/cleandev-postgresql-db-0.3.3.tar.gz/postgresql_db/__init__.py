from sqlalchemy.orm import Session
from postgresql_db.configs import _engine
from postgresql_db.configs import _config
from sqlalchemy import MetaData, asc, desc
from sqlalchemy.orm import declarative_base
from postgresql_db.inmutables import _Params
from postgresql_db.inmutables import _Config
from postgresql_db.configs import _db_properties
from postgresql_db.inmutables import _DDLOptions
from postgresql_db.inmutables import _Properties
from postgresql_db.inmutables import _NameClasses
from postgresql_db.configs import _url_connection
from postgresql_db.configs import StandartSession
from postgresql_db.configs import _ddl_auto_options
from postgresql_db.exceptions import DdlConfigError
from postgresql_db.interfaces import FilterInterface
from postgresql_db.interfaces import QuerysInterfaces
from postgresql_db.interfaces import BasicQuerysInterface
from postgresql_db.interfaces import AdvanceQuerysInterface
from generic_utils.utils import ReflectionClassUtils as Rcu
from postgresql_db.interfaces import AtributeLoaderInterface
from postgresql_db.interfaces import StandardQuerysInterface


Base = declarative_base()
Base.metadata = MetaData(Base.metadata)


# DDL Declarative
def load_declarative_models(ddl_auto: str = str(_DDLOptions.CREATE), **kwargs):
    kwargs: dict = {str(_Params.DDL_AUTO): ddl_auto} | kwargs
    list_of_class_db_model: list = Rcu.get_class_filter_parent(_config.get(_Config.NAME_SHCEMA_MODULE),
                                                               _NameClasses.BASE)
    for class_name in list_of_class_db_model:
        class_ = Rcu.get_class_from_package(_config.get(_Config.NAME_SHCEMA_MODULE), class_name)
        class_()

    metadata = Base.metadata

    ddl_auto_overwrite = kwargs.get(_Params.DDL_AUTO)

    if ddl_auto_overwrite is not None:
        if ddl_auto_overwrite not in _ddl_auto_options:
            raise DdlConfigError

    if _config.get(_Config.DDL_AUTO_VALUE) == _DDLOptions.CREATE or ddl_auto_overwrite == _DDLOptions.CREATE:
        metadata.create_all(_engine)

    if _config.get(_Config.DDL_AUTO_VALUE) == _DDLOptions.DROP_CREATE or ddl_auto_overwrite == _DDLOptions.DROP_CREATE:
        metadata.drop_all(_engine)
        metadata.create_all(_engine)


load_declarative_models()


class _AtributeLoader(AtributeLoaderInterface):

    @staticmethod
    def _load_session(session: Session):
        if session is None:
            raise Exception
        return True

    @staticmethod
    def _load_list_model(list_model: list):
        if list_model is None:
            raise Exception
        return True

    @staticmethod
    def _load_class_name(class_name: str):
        if class_name is None:
            raise Exception
        return True

    @staticmethod
    def _load_query_dict(query_dict: dict):
        if query_dict is None:
            raise Exception
        return True

    @staticmethod
    def _load_update_data(update_data: dict):
        if update_data is None:
            raise Exception
        return True

    @staticmethod
    def _load_class_name_and_query_dict(class_name: str, query_dict: dict):
        _AtributeLoader._load_class_name(class_name)
        _AtributeLoader._load_query_dict(query_dict)
        return True

    @staticmethod
    def _load_page(page: int):
        if page is None:
            raise Exception
        return True

    @staticmethod
    def _load_row_for_page(row_for_page: int):
        if row_for_page is None:
            raise Exception
        return True

    @staticmethod
    def _load_order_type(order_type: str):
        if order_type is None or order_type != 'asc' or order_type != 'desc':
            raise Exception
        return True

    @staticmethod
    def _load_order_colum(order_colum: str):
        if order_colum is None:
            raise Exception
        return True

class _Filter(_AtributeLoader, FilterInterface):

    def _filter(self, class_name: str, query_dict: dict):
        self._load_class_name_and_query_dict(class_name, query_dict)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)
        query = self._session.query(class_)
        for attr, value in query_dict.items():
            query = query.filter(getattr(class_, attr) == value)
        return query

    def _filter_like(self, class_name: str, query_dict: dict):
        self._load_class_name_and_query_dict(class_name, query_dict)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)
        query = self._session.query(class_)
        for attr, value in query_dict.items():
            query = query.filter(getattr(class_, attr).like("%%%s%%" % value))
        return query


class BasicQuery(_AtributeLoader, QuerysInterfaces, BasicQuerysInterface):

    def __init__(self, session=None):
        self._load_session(session)
        self._session = session

    def save(self, model: object):
        self._session.add(model)
        self._session.commit()

    def save_all(self, list_model: list):
        session: Session = self._session
        session.add_all(list_model)
        session.commit()

    def find_all(self, class_name):
        session = self._session
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)
        items: list = session.query(class_).all()
        if len(items) == 0:
            return []
        return items


class StandardQuerys(_Filter, QuerysInterfaces, StandardQuerysInterface):

    def __init__(self, session=None):
        self._load_session(session)
        self._session = session

    def find_by_filter(self, class_name: str, query_dict: dict):
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter(class_name, query_dict)
        items: list = query.all()
        if len(items) == 0:
            return []
        return items

    def find_by_filter_like(self, class_name: str, query_dict: dict):
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter_like(class_name, query_dict)
        items: list = query.all()
        if len(items) == 0:
            return []
        return items

    def get_one(self, class_name: str, query_dict: dict):
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter(class_name, query_dict)
        return query.one()

    def get_first(self, class_name: str, query_dict: dict):
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter(class_name, query_dict)
        return query.first()

    def get_first_like(self, class_name: str, query_dict: dict):
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter_like(class_name, query_dict)
        return query.first()

    def update(self, class_name: str, query_dict: dict, update_data: dict):
        session = self._session
        self._load_class_name_and_query_dict(class_name, query_dict)
        self._load_update_data(update_data)
        query = self._filter(class_name, query_dict)
        query.update(update_data)
        session.commit()

    def update_like(self, class_name: str, query_dict: dict, update_data: dict):
        session = self._session
        self._load_class_name_and_query_dict(class_name, query_dict)
        self._load_update_data(update_data)
        query = self._filter_like(class_name, query_dict)
        query.update(update_data)
        session.commit()

    def number_rows(self, class_name: str, query_dict: dict) -> int:
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter_like(class_name, query_dict)
        return query.count()

    def delete(self, class_name: str, query_dict: dict):
        session = self._session
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter(class_name, query_dict)
        session.commit()

    def delete_like(self, class_name: str, query_dict: dict):
        session = self._session
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter_like(class_name, query_dict)
        query.delete(synchronize_session=False)
        session.commit()


class AdvanceQuerys(_Filter, QuerysInterfaces, AdvanceQuerysInterface):

    def __init__(self, session=None):
        self._load_session(session)
        self._session = session

    def find_all(self, class_name: str, page: int, row_for_page):
        _AtributeLoader._load_class_name(class_name)
        _AtributeLoader._load_page(page)
        _AtributeLoader._load_row_for_page(row_for_page)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)
        items = self._session.query(class_).limit(row_for_page).offset(row_for_page * page).all()
        if len(items) == 0:
            return []
        return items

    def find_by_filter(self, class_name: str, query_dict: dict, page: int, row_for_page: int):
        _AtributeLoader._load_page(page)
        _AtributeLoader._load_query_dict(query_dict)
        _AtributeLoader._load_class_name(class_name)
        _AtributeLoader._load_row_for_page(row_for_page)
        query = self._filter(class_name, query_dict)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)
        items = query(class_).limit(row_for_page).offset(row_for_page * page).all()
        if len(items) == 0:
            return []
        return items

    def find_by_filter_like(self, class_name: str, query_dict: dict, page: int, row_for_page: int):
        _AtributeLoader._load_page(page)
        _AtributeLoader._load_query_dict(query_dict)
        _AtributeLoader._load_class_name(class_name)
        _AtributeLoader._load_row_for_page(row_for_page)
        query = self._filter_like(class_name, query_dict)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)
        items = query(class_).limit(row_for_page).offset(row_for_page * page).all()
        if len(items) == 0:
            return []
        return items

    def find_by_filter_and_order_by(
            self, class_name: str,
            query_dict: dict,
            order_type: str,
            order_colum: str,
            page: int,
            row_for_page: int,
    ):
        _AtributeLoader._load_page(page)
        _AtributeLoader._load_query_dict(query_dict)
        _AtributeLoader._load_class_name(class_name)
        _AtributeLoader._load_row_for_page(row_for_page)
        _AtributeLoader._load_order_type(order_type)
        _AtributeLoader._load_order_colum(order_colum)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)

        if order_type == 'asc':
            query = self._filter(class_name, query_dict).order_by(asc(getattr(class_, order_colum)))

        elif order_type == 'desc':
            query = self._filter(class_name, query_dict).order_by(desc(getattr(class_, order_colum)))

        items: list = query(class_).limit(row_for_page).offset(row_for_page * page).all()
        return items

    def find_by_filter_like_and_order_by(
            self, class_name: str,
            query_dict: dict,
            order_type: str,
            order_colum: str,
            page: int,
            row_for_page: int,
    ):
        _AtributeLoader._load_page(page)
        _AtributeLoader._load_query_dict(query_dict)
        _AtributeLoader._load_class_name(class_name)
        _AtributeLoader._load_row_for_page(row_for_page)
        _AtributeLoader._load_order_type(order_type)
        _AtributeLoader._load_order_colum(order_colum)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)

        if order_type == 'asc':
            query = self._filter_like(class_name, query_dict).order_by(asc(getattr(class_, order_colum)))

        elif order_type == 'desc':
            query = self._filter_like(class_name, query_dict).order_by(desc(getattr(class_, order_colum)))

        items: list = query(class_).limit(row_for_page).offset(row_for_page * page).all()
        return items

