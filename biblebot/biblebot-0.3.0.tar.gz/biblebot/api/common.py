import re
from typing import List, Mapping, Dict, Tuple
import urllib.parse
import datetime

from bs4 import BeautifulSoup
import bs4.element

from ..exceptions import ParsingError
from ..reqeust import Response


__all__ = (
    "httpdate_to_unixtime",
    "extract_alerts",
    "extract_hidden_tags",
    "urlencode",
    "remove_unexpected_char",
    "SemesterConverter",
    "parse_table",
)

_ALERT_PATTERN = re.compile(r"[^a-zA-Z0-9_]*?alert\s*\((.+?)\)")


def httpdate_to_unixtime(date: str) -> int:
    return int(
        (
            datetime.datetime.strptime(date.strip(), "%a, %d %b %Y %H:%M:%S GMT")
            - datetime.datetime(1970, 1, 1)
        ).total_seconds()
    )


def _replace_alert_message(message: str):
    message = message.strip()
    f, e = message[0], message[-1]
    if f == e and (f == "'" or f == '"'):
        return message.strip(f)


def extract_alerts(soup: BeautifulSoup) -> List[str]:
    script_elements = soup.find_all("script")

    result = []
    for each in script_elements:
        each = each.text if each.text else str(each.string)

        for message in _ALERT_PATTERN.findall(each):
            alert = _replace_alert_message(message)
            if alert:
                result.append(alert)
    return result


def extract_hidden_tags(soup: BeautifulSoup) -> Dict[str, str]:
    hidden_tags = soup.find_all("input", type="hidden")
    return {tag.get("name"): tag.get("value", "") for tag in hidden_tags}


def urlencode(queries: Mapping[str, str], encoding: str = "utf-8") -> str:
    return urllib.parse.urlencode(queries, encoding=encoding)


def remove_unexpected_char(text: str) -> str:
    return (
        text.strip()
        .replace("\t", "")
        .replace("\n", "")
        .replace("\r", "")
        .replace(u"\xa0", u"")
    )


class SemesterConverter:
    SEMESTER: Tuple[Tuple[str, str]] = (
        ("1", "10"),  # 1학기
        ("2", "20"),  # 2학기
        ("3", "11"),  # 여름 계절학기
        ("4", "21"),  # 겨울 계절학기
    )
    INTRANET_STYLE: int = 0
    LMS_STYLE: int = 1

    @classmethod
    def _convert_semester(cls, semester: str, style: int) -> str:
        for each in cls.SEMESTER:
            if semester == each[style]:
                return each[(style + 1) % 2]

    @classmethod
    def intranet_to_lms(cls, semester: str) -> Dict[str, str]:
        year = semester[:4]
        semester = cls._convert_semester(semester[4], cls.INTRANET_STYLE)

        return {"year": year, "semester": semester}

    @classmethod
    def lms_to_intranet(cls, year: str, semester: str) -> str:
        semester = cls._convert_semester(semester, cls.LMS_STYLE)

        return year + semester


def parse_table(
    response: Response, thead: bs4.element.Tag, tbody: bs4.element.Tag,
) -> Tuple[List[str], List[List[str]]]:
    if not thead:
        raise ParsingError("테이블 헤드가 존재하지 않습니다.", response)
    if not tbody:
        raise ParsingError("테이블 바디가 존재하지 않습니다.", response)

    head: List[str] = [th.get_text(strip=True) for th in thead.find_all("th")]
    body: List[List[str]] = [
        [td.get_text(strip=True) for td in tr.find_all("td")]
        for tr in tbody.find_all("tr")
    ]
    return head, body
