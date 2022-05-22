from abc import ABC
from abc import abstractmethod


class AtributeLoaderInterface(ABC):

    @staticmethod
    @abstractmethod
    def _load_session(session):
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def _load_list_model(list_model: list):
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def _load_class_name(class_name: str):
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def _load_query_dict(query_dict: dict):
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def _load_update_data(query_dict: dict):
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def _load_class_name_and_query_dict(class_name: str, query_dict: dict):
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def _load_page(self, page: int):
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def _load_row_for_page(self, row_for_page: int):
        raise NotImplemented

    @staticmethod
    @abstractmethod
    def _load_order_type(order_type: str):
        raise NotImplemented


    @staticmethod
    @abstractmethod
    def _load_order_colum(order_colum: str):
        raise NotImplemented


class QuerysInterfaces(ABC):

    @abstractmethod
    def __init__(self, session):
        raise NotImplemented


class FilterInterface(ABC):

    @abstractmethod
    def _filter(self, class_name: str, query_dict: dict):
        raise NotImplemented

    @abstractmethod
    def _filter_like(self, class_name: str, query_dict: dict):
        raise NotImplemented


class BasicQuerysInterface(ABC):

    @abstractmethod
    def save(self, session=None, **kwargs):
        raise NotImplemented

    @abstractmethod
    def save_all(self):
        raise NotImplemented

    @abstractmethod
    def find_all(self):
        raise NotImplemented


class StandardQuerysInterface(ABC):

    @abstractmethod
    def find_by_filter(self, class_name: str, query_dict: dict):
        raise NotImplemented

    @abstractmethod
    def find_by_filter_like(self, class_name: str, query_dict: dict):
        raise NotImplemented

    @abstractmethod
    def get_one(self, class_name: str, query_dict: dict):
        raise NotImplemented

    @abstractmethod
    def get_first(self, class_name: str, query_dict: dict):
        raise NotImplemented

    @abstractmethod
    def get_first_like(self, class_name: str, query_dict: dict):
        raise NotImplemented

    @abstractmethod
    def update(self, class_name: str, query_dict: dict, update_data: dict):
        raise NotImplemented

    @abstractmethod
    def update_like(self, class_name: str, query_dict: dict, update_data: dict):
        raise NotImplemented

    @abstractmethod
    def number_rows(self, class_name: str, query_dict: dict) -> int:
        raise NotImplemented

    @abstractmethod
    def delete(self, class_name: str, query_dict: dict):
        raise NotImplemented

    @abstractmethod
    def delete_like(self, class_name: str, query_dict: dict):
        raise NotImplemented


class AdvanceQuerysInterface(ABC):

    @abstractmethod
    def find_all(self, class_name: str, page: int, row_for_page: int):
        raise NotImplemented

    @abstractmethod
    def find_by_filter(self, class_name: str, query_dict: dict, page: int, row_for_page: int):
        raise NotImplemented

    @abstractmethod
    def find_by_filter_like(self, class_name: str, query_dict: dict, page: int, row_for_page: int):
        raise NotImplemented

    @abstractmethod
    def find_by_filter_and_order_by(
            self, class_name: str,
            query_dict: dict,
            order_type: str,
            order_colum: str,
            page: int,
            row_for_page: int,
    ):
        raise NotImplemented

    @abstractmethod
    def find_by_filter_like_and_order_by(
            self, class_name: str,
            query_dict: dict,
            order_type: str,
            order_colum: str,
            page: int,
            row_for_page: int,
    ):
        raise NotImplemented
