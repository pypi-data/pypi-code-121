from typing import Iterator, Callable, Iterable
from functools import wraps


class LimitOffsetPaginator:
    """Iterator class for Argus-API methods returning result sets.

    Meant for endpoints supporting limit/offset pagination, and to be
    instantiated via the :func:`offset_paginated` decorator.
    """

    def __init__(
        self, page: dict, fetcher: Callable, fetcher_args: Iterable, fetcher_kwargs: dict
    ):
        """Initialize an instance

        :param page: initial API response (i.e. the first "page")
        :param fetcher: argus_api method used to fetch data
        :param fetcher_args: positional arguments for the fetcher
        :param fetcher_kwargs: keyword arguments for the fetcher
        """
        self._first_page = self._current_page = page
        self.count = page["count"]
        self.size = page["size"]
        # getting limit and offset from the response rather than the "fetcher"
        # arguments allows us to cover cases when the defaults were used or
        # the API decided to not honor the parameters
        self.offset = page["offset"]
        self.limit = page["limit"]
        self.fetcher = fetcher
        self.fetcher_args = fetcher_args
        self.fetcher_kwargs = fetcher_kwargs

    def _switch_page(self, page: dict):
        """Set the current page and pagination info"""
        self._current_page = page
        self.size = page["size"]
        self.offset = page["offset"]

    @property
    def has_next(self) -> bool:
        """Indicate whether there is a next page to fetch"""
        if self.limit == 0:
            # limit=0 means everything is fetched as one page
            return False
        elif self.count == -1:
            # count=-1 means that the API won't count for us.
            # in that case, check if we received less than the limit.
            return self.size >= self.limit
        if self.count > self.size + self.offset:
            if self.size == 0:
                # handle the special case where the API returned no data and an
                # inaccurate nonzero count to prevent infinite looping.
                return False
            return True
        return False

    def __iter__(self):
        return self

    def __next__(self):
        # save a reference to the current page
        current = self._current_page
        if not current:
            raise StopIteration
        if self.has_next:
            _current = self._current_page
            # actually fetch the next page if there is one
            self.fetcher_kwargs.update(
                {"limit": self.limit, "offset": self.offset + self.size}
            )
            next_page = self.fetcher(*self.fetcher_args, **self.fetcher_kwargs)
            self._switch_page(next_page)
        else:
            # otherwise, next iteration will terminate
            self._current_page = None
        return current


def offset_paginated(func: Callable) -> Callable:
    """decorator that turns API functions returning result sets into iterators on pages.

    Uses the limit/offset pagination strategy.

    Meant to decorate an API method, as in :

    .. code-block:: python

       from argus_api.api.cases.v2.case import advanced_case_search
       for page in offset_paginated(advanced_case_search)(customer="mnemonic", limit=25):
           cases = page["data"]

    The decorated function will return a :class:`LimitOffsetPaginator` instance.
    """

    @wraps(func)
    def _paginated(*args, **kwargs) -> Iterator[dict]:
        first_page = func(*args, **kwargs)
        return LimitOffsetPaginator(first_page, func, args, kwargs)

    return _paginated
