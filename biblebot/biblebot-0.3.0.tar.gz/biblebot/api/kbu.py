from dataclasses import dataclass
from typing import Optional, Dict, Union
import datetime
import unicodedata

from ..exceptions import ParsingError
from ..reqeust import Response
from .base import IParser, HTTPClient, APIResponseType, ResourceData
from .common import urlencode


__all__ = (
    "NoticeData",
    "NoticeArticle",
    "NoticeList",
    "MainNotice",
    "ScholarshipNotice",
    "IllipNotice",
)

DOMAIN_NAME: str = "https://www.bible.ac.kr"


@dataclass
class NoticeData:
    title: str
    author: str
    date: datetime.datetime
    content: str
    url: str


class NoticeArticle:
    @classmethod
    async def fetch(
        cls,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            url, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response) -> NoticeData:
        soup = response.soup

        header_container = soup.find("div", attrs={"class": "header"})
        if not header_container:
            raise ParsingError("공지사항 머리글 정보를 찾을 수 없습니다.", response)

        try:
            title = header_container.find("h5").get_text(strip=True)
            author = header_container.find("span", attrs={"rel": "author"}).get_text(
                strip=True
            )
            date = header_container.find("time").get_text(strip=True)
            content = soup.find("div", attrs={"class": "content"}).get_text(strip=True)

            converted_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            converted_content = unicodedata.normalize("NFKD", content).strip()
        except AttributeError as e:
            raise ParsingError("공지사항 컨텐츠 요소를 추출할 수 없습니다.", response) from e
        else:
            return NoticeData(
                title, author, converted_date, converted_content, response.url
            )


class NoticeList(IParser):
    """ 공지사항 리스트를 가져오는 클래스

    공지사항은 카테고리별로 여러 페이지로 나누어져 있지만, html 구성은 같기 때문에 본 클래스를 재사용할 수 있음
    상속받은 클래스에서 'URL' 클래스 변수 선언할 것
    """

    @classmethod
    async def fetch(
        cls,
        page: Union[int, str] = 1,
        search_keyword: Optional[str] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        page = int(page)
        url = cls.URL + str(page)
        if search_keyword:
            query = {"keyword": search_keyword}
            query_string = urlencode(query)
            url = f"{url}?{query_string}"
        response = await HTTPClient.connector.get(
            url, headers=headers, timeout=timeout, **kwargs
        )
        response.etc["notice"] = {"page": page, "keyword": search_keyword}
        return response

    @classmethod
    def parse(cls, response: Response) -> APIResponseType:
        soup = response.soup
        table_container = soup.find(
            "ul", attrs={"data-role": "table", "class": "black"}
        )
        if not table_container:
            raise ParsingError("공지사항 컨테이너가 존재하지 않습니다.", response)

        rows = []
        for each in table_container.find_all("li", attrs={"class": "tbody"}):
            row = dict(
                seq=each.find("span", attrs={"class": "loopnum"}).get_text(strip=True),
                title=each.find("span", attrs={"class": "title"}).get_text(strip=True),
                author=each.find("span", attrs={"class": "name"}).get_text(strip=True),
                date=each.find("span", attrs={"class": "reg_date"}).get_text(
                    strip=True
                ),
                url=DOMAIN_NAME + each.find("a", href=True).attrs["href"],
            )
            rows.append(row)

        return ResourceData(
            data={"notice": rows}, meta=response.etc["notice"], link=response.url
        )


class MainNotice(NoticeList):
    URL: str = DOMAIN_NAME + "/ko/life/notice/list/"


class ScholarshipNotice(NoticeList):
    URL: str = DOMAIN_NAME + "/ko/life/tuition_notice/list/"


class IllipNotice(NoticeList):
    URL: str = DOMAIN_NAME + "/ko/illip/notice/list/"
