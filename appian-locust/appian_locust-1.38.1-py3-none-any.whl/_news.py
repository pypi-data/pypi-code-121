from typing import Any, Dict, Tuple

from appian_locust import logger
from appian_locust._base import _Base
from appian_locust._interactor import _Interactor
from appian_locust._locust_error_handler import log_locust_error

log = logger.getLogger(__name__)


class _News(_Base):
    def __init__(self, interactor: _Interactor) -> None:
        """
        News class wrapping list of possible activities can be performed with Appian-Tempo-News.

        Warnings: This class is internal and should not be accessed by tests directly. It can be accessed via the "appian" object

        Note: "appian" is created as part of ``AppianTaskSet``'s ``on_start`` function

        Args:
            session: Locust session/client object
            host (str): Host URL
        """
        self.interactor = interactor

        # When Get All functions called, these variables will be used to cache the values
        self._news: Dict[str, Any] = dict()
        self._errors: int = 0

    def get_all(self, search_string: str = None, locust_request_label: str = "") -> Dict[str, Any]:
        """
        Retrieves all the available "news" and assgit ociated metadata from "Appian-Tempo-News"

        Note: All the retrieved data about news is stored in the private variable self._news

        Args:
            search_string(str, optional): results will be filtered based on the search string.

        Returns (dict): List of news and associated metadata

        Examples:

            >>> self.appian.action.get_all()

        """
        if search_string:
            uri = "/suite/api/feed/tempo?q=" + search_string
            label = "News.Search." + search_string
        else:
            uri = "/suite/api/feed/tempo?t=e,x,b&m=menu-news&st=o"
            label = locust_request_label or "News.Feed"

        self._news = dict()
        error_key_string = "ERROR::"
        error_key_count = 0

        # request the list of feeds
        response = self.interactor.get_page(uri=uri, label=label)

        for current_item in response.json().get('feed', {}).get('entries', []):
            try:
                if isinstance(current_item, dict) and 'title' in current_item:
                    title = current_item['title'].strip()
                    news_id = current_item['id'].strip()
                    key = news_id + "::" + title
                    self._news[key] = current_item
            except Exception as e:
                error_key_count += 1
                self._news[error_key_string + str(error_key_count)] = {}
                log_locust_error(e, error_desc="Corrupt News Error", location=uri, raise_error=False)
        self._errors = error_key_count

        if len(self._news) == 0:
            log.warning(f"News search failed for keyword: '{search_string}'")
        return self._news

    def get_news(self, news_name: str, exact_match: bool = True, search_string: str = None) -> Dict[str, Any]:
        """
        Get the information about specific news by name.

        Args:
            news_name (str): name of the news entry
            exact_match (bool, optional): Should news name match exactly or to be partial match. Default : True
            search_string (str, optional): results will be filtered based on the search string.

        Returns: Specific News's info

        Raises: In case news is not found in the system, it throws an "Exception"

        Example:
            If full name of action is known,

            >>> self.appian.news.get("news_name")

            If only partial name is known,

            >>> self.appian.news.get("news_name", exact_match=False)

        """
        _, current_news = super().get(self._news, news_name,
                                      exact_match=exact_match, search_string=search_string)
        if not current_news:
            raise (Exception("There is no news with name {} in the system under test (Exact match = {})".format(
                news_name, exact_match)))
        return current_news

    def visit(self, news_name: str, exact_match: bool = True, search_string: str = None) -> None:
        """
        This function calls the nav API for the specific news item and its related records if any

        Args:
            news_name (str): Name of the news entry to be called
            exact_match (bool, optional): Should news name match exactly or to be partial match. Default : True
            search_string (str, optional): results will be filtered based on the search string.

        Returns: None

        Examples:

            If full name of news is known,

            >>> self.appian.news.visit("news_name")

            If only partial name is known,

            >>> self.appian.news.visit("news_name", exact_match=False)

        """
        current_news, headers = self._visit_internal(news_name, exact_match, search_string)
        for link in current_news['links']:
            if link['rel'] == "related-records-properties":
                if str(link['href']).strip() != "":
                    self.interactor.get_page(link['href'], headers, label="News.LoadEntry." + news_name)

    def visit_news_entry(self, news_name: str, exact_match: bool = True, search_string: str = None) -> Tuple:
        """
        This function simulates navigating to a single entry in the ui. There are two parts to navigating to a
        news entry: navigating to the view and getting the news entry's feed.

        Args:
            news_name (str): Name of the news entry to be called
            exact_match (bool, optional): Should news name match exactly or to be partial match. Default : True
            search_string (str, optional): results will be filtered based on the search string.

        Returns (Tuple): Response codes for the view navigation and getting the feed entry

        Examples:

            If full name of news is known,

            >>> self.appian.news.visit("news_name")

            If only partial name is known,

            >>> self.appian.news.visit("news_name", exact_match=False)
        """
        current_news, headers = self._visit_internal(news_name, exact_match, search_string)
        view_status_code = None
        feed_status_code = None
        for link in current_news['links']:
            if link['rel'] == 'share':
                if str(link['href']).strip() != "":
                    view_status_code = self.interactor.get_page(link['href'], headers).status_code
            elif link['rel'] == 'edit':
                if str(link['href']).strip() != "":
                    feed_status_code = self.interactor.get_page(link['href'], headers).status_code

        return (view_status_code, feed_status_code)

    def _visit_internal(self, news_name: str, exact_match: bool = True, search_string: str = None) -> Tuple:
        current_news = self.get_news(news_name, exact_match, search_string)
        headers = self.interactor.setup_request_headers()
        tempo_site_url_stub = "D6JMim"

        # Nav
        nav_uri = "/suite/rest/a/sites/latest/" + tempo_site_url_stub + "/page/news/nav"
        # navigation request before the search
        headers["Accept"] = "application/vnd.appian.tv.ui+json"
        self.interactor.get_page(uri=nav_uri, headers=headers, label="News.Nav")

        # Visiting related records
        headers["Accept"] = "application/atom+json,application/json"

        return (current_news, headers)

    def search(self, search_string: str = "*") -> Dict[str, Any]:
        return self.get_all(search_string)
