from typing import List, Final
from collections import defaultdict
import pandas as pd
from requests import Session, Response
from bs4 import BeautifulSoup, ResultSet
from house_info.utils import PageList, logger, DataFrame, SHColumn
from house_info.mixins import MultiThreadingRequestMixin


class SHRequest(MultiThreadingRequestMixin):
    URL: Final = "https://www.i-sh.co.kr/main/lay2/program/S1T294C297/www/brd/m_247/list.do?page="

    def __init__(self, page: int = 1, thread: bool = False) -> None:
        self.page: int = page
        self.__pages: List[int] = self.__get_page_numbers()
        self.thread: bool = thread

    def __get_page_numbers(self) -> List[int]:
        """
        page number 리스트 뽑기
        """
        page_numbers = [i for i in range(1, self.page + 1)]
        return page_numbers

    def __get_pages(self) -> PageList:
        urls = self.get_urls()
        pages = PageList([self.send_requests(url).text for url in urls])
        return pages

    def get_urls(self) -> List[str]:
        """
        page number list를 기준으로 page url list up 하기
        """
        urls = [SHRequest.URL + str(page) for page in self.__pages]
        return urls

    def send_requests(self, url: str) -> Response:
        """
        해당 url로 요청을 보내서 html 소스 가져오기
        """
        with Session() as s:
            response = s.get(url)
            return response

    def __call__(self) -> PageList:
        if self.thread:
            urls = self.get_urls()
            return self.get_pages_with_multi_threading(urls)
        return self.__get_pages()


class SHPagePreprocessorMixin:
    """
    Page Source 전처리 Mixin
    """

    def get_title(self, raw_html: ResultSet = None, index: int = 1) -> str:
        """
        '사이트 스타일이 바뀌면 코드를 다시 작성해야함'

        html에서 title 뽑아오기
        index[0] -> table column
        index[1] -> title
        """
        try:
            title = raw_html[index].find_all("a", attrs={"class": "ellipsis icon"})
            if title == []:
                title = raw_html[index].find_all("a", attrs={"class": "ellipsis"})
            title = title[0].get_text()
            title = title.rstrip().strip().split("\r")
            title = list(map(lambda x: x.strip().rstrip(), title))
            title = list(filter(lambda x: x != "", title))

            if len(title) == 2:
                _, title = title
            else:
                _, title = False, title.pop()
            return title

        except ValueError as e:
            logger.debug("글제목 없음")
            return title

    def get_index(self, raw_html: ResultSet = None, index: int = 1) -> int:
        """
        게시물 index 가져오기
        """
        index = raw_html[index].find("td")
        index = index.get_text()
        try:
            if index.isnumeric():
                return int(index)
        except ValueError as e:
            logger.debug("index가 number가 아님")
            return 9999999

    def get_department(self, raw_html: ResultSet = None, index: int = 1) -> str:
        """
        담당부서 가져오기
        """
        try:
            department = raw_html[index].find_all("td")[2].get_text()
            department = department.strip().rstrip()
            return department
        except ValueError as e:
            logger.debug("담당부서 없음")
            return "담당부서 없음"

    def get_registration_date(self, raw_html: ResultSet = None, index: int = 1) -> str:
        """
        등록일 가져오기
        """
        try:
            registration_date = (
                raw_html[index].find_all("td", attrs={"class": "num"})[0].get_text()
            )
            registration_date = registration_date.strip().rstrip()
            return registration_date
        except ValueError as e:
            logger.debug("등록 날짜 없음")
            return "2222-12-12"


class SHTable(SHPagePreprocessorMixin):
    """
    Pandas DataFrame 구조로 Table 객체 생성
    page_sources : SHRequest로 받아온 페이지 목록 리스트
    """

    def __init__(self, page_sources: PageList):
        assert page_sources.__class__ == PageList, "SHRequest로 받아온 Page Source만 전처리 가능"
        self.page_sources = [
            BeautifulSoup(page, "html.parser").find_all("tr") for page in page_sources
        ]

    def create_data_frame(self) -> DataFrame:
        """
        Dataframe 생성
        """
        data = self._get_data_dict(self.page_sources)
        data_frame = pd.DataFrame(data=data)
        return data_frame

    def _get_data_dict(self, pages) -> defaultdict:
        """
        page별로 전처리하여 data_dict 생성
        DataFrame의 column: 인덱스, 제목, 담당부서, 등록일자
        """
        data_dict = defaultdict(list)

        for page in pages:
            result = self._get_row_data(page)
            data_dict["인덱스"].extend(result[0])
            data_dict["제목"].extend(result[1])
            data_dict["담당부서"].extend(result[2])
            data_dict["등록일자"].extend(result[3])
        return data_dict

    def _get_row_data(self, page) -> SHColumn:
        """
        page에서 필요한 요소 추출
        """
        # post_length: page내 게시물 개수 -> 10개의 게시물이어야함
        # index 1 ~ 10
        post_length = 10

        index_list, title_list, department_list, registration_date_list = [], [], [], []
        for i in range(1, post_length + 1):
            index_list.append(self.get_index(page, i))
            title_list.append(self.get_title(page, i))
            department_list.append(self.get_department(page, i))
            registration_date_list.append(self.get_registration_date(page, i))
        result = (index_list, title_list, department_list, registration_date_list)
        return result


class SHDataManager:
    def __init__(self, page: int = 1, thread: bool = False) -> None:
        self.request = SHRequest(page, thread)

    def create_page_sources(self) -> ResultSet:
        page_sources = self.request()
        return page_sources

    def get_data_frame(self, page_sources) -> DataFrame:
        data_table = SHTable(page_sources)
        data_table = data_table.create_data_frame()
        return data_table

    def export_csv(self, path: str) -> None:
        page_sources = self.create_page_sources()
        data_table = self.get_data_frame(page_sources)

        data_table.to_csv(path, index=False)
