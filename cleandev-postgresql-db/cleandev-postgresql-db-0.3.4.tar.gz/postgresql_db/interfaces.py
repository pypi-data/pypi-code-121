from abc import ABC
from abc import abstractmethod




class BasicQuery(ABC):

    @abstractmethod
    def save(self, model):
        raise NotImplemented

    @abstractmethod
    def save_all(self, list_model: list):
        raise NotImplemented

    @abstractmethod
    def find_all(self, class_name):
        raise NotImplemented


class StandardQuery(ABC):

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


class AdvanceQuery(ABC):

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


