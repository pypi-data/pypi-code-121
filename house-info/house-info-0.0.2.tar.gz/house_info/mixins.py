from typing import Tuple, List
from requests import Session
from concurrent.futures import ThreadPoolExecutor
from house_info.utils import PageList


class MultiThreadingRequestMixin:
    max_workers = 8
    executor = ThreadPoolExecutor(max_workers=8)

    def fetcher(self, params: Tuple[Session, str]):
        session = params[0]
        url = params[1]

        with session.get(url) as response:
            return response.text

    def get_pages_with_multi_threading(self, urls: List[str]) -> PageList:
        executor = ThreadPoolExecutor(max_workers=8)

        with Session() as session:
            params = [(session, url) for url in urls]
            pages = PageList(executor.map(self.fetcher, params))

        return pages

    @classmethod
    def change_max_workers(cls, num: int):
        cls.executor = ThreadPoolExecutor(max_workers=num)
