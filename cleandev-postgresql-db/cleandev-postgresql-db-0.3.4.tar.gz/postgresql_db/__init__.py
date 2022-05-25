from abc import ABC, abstractmethod

from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import MetaData
from sqlalchemy.orm import Session
from postgresql_db.configs import _config
from postgresql_db.configs import _engine
from sqlalchemy.orm import declarative_base
from postgresql_db.inmutables import _Config
from postgresql_db.inmutables import _Params
from postgresql_db.interfaces import BasicQuery
from postgresql_db.inmutables import _Properties
from postgresql_db.inmutables import _DDLOptions
from postgresql_db.configs import _db_properties
from postgresql_db.configs import _url_connection
from postgresql_db.inmutables import _NameClasses
from postgresql_db.interfaces import AdvanceQuery
from postgresql_db.interfaces import StandardQuery
from postgresql_db.interfaces import StandardQuery
from generic_utils import ReflectionClassUtilsImpl
from postgresql_db.configs import _ddl_auto_options
from postgresql_db.exceptions import DdlConfigError
from generic_utils.interfaces import ReflectionClassUtils

Base = declarative_base()
Base.metadata = MetaData(Base.metadata)
Rcu: ReflectionClassUtils = ReflectionClassUtilsImpl()


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


class _Querys(ABC):

    @abstractmethod
    def __init__(self, session):
        raise NotImplemented



class _AtributeLoader:

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
        ASC: str = str(_Properties.ASC)
        DESC: str = str(_Properties.DESC)
        if order_type == ASC or order_type == DESC:
            return True
        raise Exception


    @staticmethod
    def _load_order_colum(order_colum: str):
        if order_colum is None:
            raise Exception
        return True


class _Filter(_AtributeLoader):

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


class BasicQueryImpl(_AtributeLoader, _Querys, BasicQuery):

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


class StandardQueryImpl(_Filter, _Querys, StandardQuery):
    
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
        query.delete(synchronize_session=False)
        session.commit()

    def delete_like(self, class_name: str, query_dict: dict):
        session = self._session
        self._load_class_name_and_query_dict(class_name, query_dict)
        query = self._filter_like(class_name, query_dict)
        query.delete(synchronize_session=False)
        session.commit()


class AdvanceQuerysImpl(_Filter, _Querys, AdvanceQuery):

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
        ASC: str = str(_Properties.ASC)
        DESC: str = str(_Properties.DESC)
        _AtributeLoader._load_page(page)
        _AtributeLoader._load_query_dict(query_dict)
        _AtributeLoader._load_class_name(class_name)
        _AtributeLoader._load_row_for_page(row_for_page)
        _AtributeLoader._load_order_type(order_type)
        _AtributeLoader._load_order_colum(order_colum)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)

        if order_type == ASC:
            query = self._filter(class_name, query_dict).order_by(asc(getattr(class_, order_colum)))
        elif order_type == DESC:
            query = self._filter(class_name, query_dict).order_by(desc(getattr(class_, order_colum)))
        items: list = query.limit(row_for_page).offset(row_for_page * page).all()
        return items

    def find_by_filter_like_and_order_by(
            self, class_name: str,
            query_dict: dict,
            order_type: str,
            order_colum: str,
            page: int,
            row_for_page: int,
    ):
        ASC: str = str(_Properties.ASC)
        DESC: str = str(_Properties.DESC)
        _AtributeLoader._load_page(page)
        _AtributeLoader._load_query_dict(query_dict)
        _AtributeLoader._load_class_name(class_name)
        _AtributeLoader._load_row_for_page(row_for_page)
        _AtributeLoader._load_order_type(order_type)
        _AtributeLoader._load_order_colum(order_colum)
        class_ = Rcu.get_class_from_package(_db_properties.get(_Properties.PATH_MODULE_SCHEMA), class_name)

        if order_type == ASC:
            query = self._filter_like(class_name, query_dict).order_by(asc(getattr(class_, order_colum)))
        elif order_type == DESC:
            query = self._filter_like(class_name, query_dict).order_by(desc(getattr(class_, order_colum)))
        items: list = query.limit(row_for_page).offset(row_for_page * page).all()
        return items