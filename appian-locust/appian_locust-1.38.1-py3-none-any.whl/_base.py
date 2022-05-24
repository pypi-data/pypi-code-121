from .helper import list_filter
from . import logger
from typing import Any


log = logger.getLogger(__name__)


class _Base():
    """
    Base class for classes ``_Actions``, ``_News``, ``_Records``, ``_Reports``, ``_Tasks``, ``Sites``
    """

    def get_all(self, search_string: str = None, locust_request_label: str = "") -> Any:
        """
        Common Get All function prototype that is overwritten by subclasses.
        Created only to conform to Mypy validation.
        """
        return None

    def get(self, items_in_dict: dict, item_name: str, exact_match: bool = True, ignore_retry: bool = False, search_string: str = None) -> tuple:
        """
        Common Get function to get the specific component from dictionary of items. If item is not found, it calls
        get_all function to update itself and retry.

        Warning: Internal function, should never be called directly.

        Args:
            items_in_dict (dict): Dictionary of component (for ex, dictionary of actions if called from actions class)
            item_name (str): Component name (for ex, action name if called from actions class)
            exact_match (bool, optional): Should item name match exactly or to be partial match. Default : True
            ignore_retry (bool, optional): Whether to retry or not if item is not found in first try.
            search_string (str, optional): String to filter the results of get_all function.
                                           Currently supported only for ``News``

        Returns: Tuple of item name and full properties of item If item found, otherwise tuple of Nones

        """
        current_item = list_filter(
            list(items_in_dict.keys()), item_name, exact_match)
        if len(current_item) == 0:
            if ignore_retry:
                return None, None
            else:
                if search_string:
                    items_in_dict = self.get_all(search_string)
                else:
                    items_in_dict = self.get_all()

        current_item = list_filter(
            list(items_in_dict.keys()), item_name, exact_match)
        if len(current_item) > 0:
            if len(current_item) > 1:
                log.warning(
                    "More than one item matches the given name, returning the first match")
            return current_item[0], items_in_dict[current_item[0]]
        else:
            return None, None
