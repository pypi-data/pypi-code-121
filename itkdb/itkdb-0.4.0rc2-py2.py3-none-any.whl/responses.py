import json
import logging

log = logging.getLogger(__name__)


class PagedResponse(object):
    def __init__(self, session, response, limit=-1, key="pageItemList"):
        self._pages = []
        self._session = session
        self._load(response)
        self.yielded = 0
        self.limit = limit if limit and limit > 0 else self.total
        self.key = key

    @property
    def pages(self):
        return self._pages

    @property
    def last_page(self):
        return self.pages[-1]

    @property
    def data(self):
        return self.last_page.get(self.key)

    def _load(self, response):
        self._response = response
        self._pages.append(response.json())
        self.error = self.last_page.get("uuAppErrorMap")
        self.page_info = self.last_page.get("pageInfo", {})
        self.page_index = self.page_info.get("pageIndex")
        self.page_size = self.page_info.get("pageSize")
        self.total = self.page_info.get("total")
        # nb: list_index is only for the last page
        self._list_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.limit is not None:
            if self.yielded >= self.limit:
                raise StopIteration()
            if self._list_index >= len(self.data):
                self._next_page()

        self._list_index += 1
        self.yielded += 1
        return self.data[self._list_index - 1]

    def __bool__(self):
        return bool(self.total)

    # python2 compatibility
    def __nonzero__(self):
        return self.__bool__()

    # python2 compatibility
    def next(self):
        return self.__next__()

    def _next_page(self):
        body = json.loads(self._response.request.body)
        body.update(
            {"pageInfo": {"pageIndex": self.page_index + 1, "pageSize": self.page_size}}
        )
        self._response.request.prepare_body(data=None, files=None, json=body)
        response = self._session.send(self._response.request)
        self._load(response)
