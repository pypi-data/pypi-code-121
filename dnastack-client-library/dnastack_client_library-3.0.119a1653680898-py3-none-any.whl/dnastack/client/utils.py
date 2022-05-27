from abc import ABC
from typing import Iterator
import requests
from requests import Response

from ..exceptions import PaginationError


class PaginatedResponse(Iterator, ABC):
    """
    An iterator for handling paginated responses

    :param response: The requests Response object returned by the server
    """

    def __init__(self, response: Response):
        self.response = response
        self.page = self.response.json()
        self.data = self.page.get("data")

        if "pagination" in self.page.keys():
            self.next_page_url = self.page["pagination"].get("next_page_url")
        else:
            self.next_page_url = None

    def __iter__(self):
        self.page = self.response.json()
        self.data = self.page.get("data")

        if "pagination" in self.page.keys():
            self.next_page_url = self.page["pagination"].get("next_page_url")
        else:
            self.next_page_url = None

        return self

    def __next__(self):
        """
        Get the next element in a paginated response

        :return:
        """
        if len(self.data) > 0:
            return self.data.pop(0)
        elif self.next_page_url:
            res = requests.get(self.next_page_url)

            if not res.ok:
                raise PaginationError(
                    response=self.response,
                    page_url=self.next_page_url,
                    msg=f"The server returned error code [{res.status_code}]",
                )

            self.page = res.json()
            self.data = self.page.get("data")

            if "pagination" in self.page.keys():
                self.next_page_url = self.page["pagination"].get("next_page_url")
            else:
                self.next_page_url = None

            if len(self.data) > 0:
                return self.data.pop(0)
            else:
                raise StopIteration
        else:
            raise StopIteration
