from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, List, Tuple
import re

from .base import (
    ILoginFetcher,
    IParser,
    APIResponseType,
    HTTPClient,
    ErrorData,
    ResourceData,
    SemesterData,
    IGeneralFetcher,
    ISemesterFetcher,
    ParserPrecondition,
)
from ..exceptions import ParsingError
from ..reqeust import Response
from .common import (
    httpdate_to_unixtime,
    extract_alerts,
    urlencode,
    SemesterConverter,
    parse_table,
)

__all__ = (
    "IParserPrecondition",
    "Login",
    "Profile",
    "CourseList",
    "Attendance",
)

DOMAIN_NAME: str = "https://lms.bible.ac.kr"  # with protocol


class IParserPrecondition(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def is_blocking(response: Response) -> Optional[ErrorData]:
        """ 진행할 수 없는 사전조건인 경우 ErrorData, 그렇지 않은 경우 None """
        pass


_ParserPrecondition = ParserPrecondition(IParserPrecondition)


class _SessionExpiredChecker(IParserPrecondition):
    @staticmethod
    def is_blocking(response: Response) -> Optional[ErrorData]:
        if "login" in response.headers.get("location", ""):
            return ErrorData(error={"title": "세션이 만료되었습니다."}, link=response.url,)

        return None


def _extract_semester(response: Response) -> SemesterData:
    soup = response.soup

    year_container = soup.find("select", attrs={"id": "year"})
    semester_container = soup.find("select", attrs={"id": "semester"})
    if not year_container:
        raise ParsingError("연도 셀렉트 태그를 불러올 수 없습니다.", response)
    elif not semester_container:
        raise ParsingError("학기 셀렉트 태그 불러올 수 없습니다.", response)

    try:
        year_selectables: List[str] = [
            opt.attrs["value"] for opt in year_container.find_all("option")
        ]
        year_selected: str = year_container.find("option", selected=True).attrs["value"]
        semester_selectables: List[str] = [
            opt.attrs["value"] for opt in semester_container.find_all_next("option")
        ]
        semester_selected: str = semester_container.find("option", selected=True).attrs[
            "value"
        ]

    except (KeyError, AttributeError) as e:
        raise ParsingError("학기 옵션 태그를 정상적으로 선택할 수 없습니다.", response) from e

    else:
        selected = SemesterConverter.lms_to_intranet(year_selected, semester_selected)
        selectable = [
            SemesterConverter.lms_to_intranet(year, semester)
            for year in year_selectables
            for semester in semester_selectables
        ]
    return SemesterData(selected=selected, selectable=selectable)


class Login(ILoginFetcher, IParser):
    URL: str = DOMAIN_NAME + "/login/index.php"
    LOGIN_ERROR = {
        "1": "현재, 브라우저의 쿠키가 작동하지 않습니다.",
        "2": "사용자 아이디: 이이디에는 영어소문자, 숫자, 밑줄( _ ), 하이폰( - ), 마침표( . ) 또는 @ 기호만을 쓸 수 있습니다.",
        "3": "아이디 또는 패스워드가 잘못 입력되었습니다.",
    }

    @classmethod
    async def fetch(
        cls,
        user_id: str,
        user_pw: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        form = {"username": user_id, "password": user_pw}
        return await HTTPClient.connector.post(
            cls.URL, headers=headers, body=form, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response) -> APIResponseType:
        # 로그인 실패
        if "location" not in response.headers:
            alerts = extract_alerts(response.soup)
            return ErrorData(
                error={"title": alerts[0], "alert_messages": alerts}, link=response.url,
            )
        m = re.search(r"errorcode=(\d+)", response.headers["location"])
        # 로그인 실패
        if m:
            error_code = m.group(1)
            return ErrorData(
                error={
                    "title": cls.LOGIN_ERROR.get(
                        error_code, f"login errorcode={error_code}"
                    ),
                    "code": error_code,
                },
                link=response.url,
            )
        # 로그인 성공
        else:
            iat = httpdate_to_unixtime(response.headers["date"])
            return ResourceData(
                data={"cookies": response.cookies, "iat": iat}, link=response.url
            )


class Profile(IGeneralFetcher, IParser):
    URL: str = DOMAIN_NAME + "/user/user_edit.php?lang=ko"

    @staticmethod
    def validate_name(name: str) -> bool:
        return bool(re.search(r"^[가-힣]{2,}$", name))

    @staticmethod
    def validate_sid(univ_id: str) -> bool:
        return bool(re.search(r"^[a-zA-Z]{,1}\d{3,9}$", univ_id))

    @staticmethod
    def validate_major(major: str) -> bool:
        return bool(re.search(r"^[가-힣]{3,17}$", major))

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            cls.URL, headers=headers, cookies=cookies, timeout=timeout, **kwargs
        )

    @classmethod
    def _parse_sid(cls, response: Response) -> str:
        soup = response.soup
        sid_container = soup.find("div", attrs={"id": "fitem_id_idnumber"})
        if not sid_container:
            raise ParsingError("학번 컨테이너를 찾을 수 없습니다.", response)

        sid_tag = sid_container.find("div", attrs={"class", "felement fstatic"})
        if not sid_tag:
            raise ParsingError("학번을 탐색할 수 없습니다.", response)

        sid: str = sid_tag.get_text(strip=True)
        if not cls.validate_sid(sid):
            raise ParsingError("올바르지 않은 학번입니다.", response)

        return sid

    @classmethod
    def _parse_name(cls, response: Response) -> str:
        soup = response.soup
        name_container = soup.find("div", attrs={"id": "fitem_id_firstname"})
        if not name_container:
            raise ParsingError("성명 컨테이너를 찾을 수 없습니다.", response)

        name_tag = name_container.find("input")
        if not name_tag:
            raise ParsingError("성명을 탐색할 수 없습니다.", response)

        name = name_tag.get("value", "").strip()
        if not cls.validate_name(name):
            raise ParsingError("올바르지 않은 이름입니다.", response)

        return name

    @classmethod
    def _parse_major(cls, response: Response) -> str:
        soup = response.soup
        major_container = soup.find("div", attrs={"id": "fitem_id_department"})
        if not major_container:
            raise ParsingError("전공 컨테이너를 찾을 수 없습니다.", soup.original_markup)

        major_tag = major_container.find("input")
        if not major_tag:
            raise ParsingError("전공을 탐색할 수 없습니다.", soup.original_markup)

        major = major_tag.get("value", "").strip()
        if not cls.validate_major(major):
            raise ParsingError("올바르지 않은 학과입니다.", response)

        return major

    @classmethod
    @_ParserPrecondition
    def parse_sid(cls, response: Response) -> APIResponseType:
        return ResourceData(data={"sid": cls._parse_sid(response)}, link=response.url)

    @classmethod
    @_ParserPrecondition
    def parse_name(cls, response: Response) -> APIResponseType:
        return ResourceData(data={"name": cls._parse_name(response)}, link=response.url)

    @classmethod
    @_ParserPrecondition
    def parse_major(cls, response: Response) -> APIResponseType:
        return ResourceData(
            data={"major": cls._parse_major(response)}, link=response.url
        )

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        sid = cls._parse_sid(response)
        name = cls._parse_name(response)
        major = cls._parse_major(response)
        return ResourceData(
            data={"sid": sid, "name": name, "major": major}, link=response.url
        )


class CourseList(ISemesterFetcher, IParser):
    URL: str = DOMAIN_NAME + "/local/ubion/user/index.php?lang=ko"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        semester: Optional[str] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        url = cls.URL

        if semester:
            query = SemesterConverter.intranet_to_lms(semester)
            query_string = urlencode(query)
            url = f"{url}&{query_string}"

        response = await HTTPClient.connector.get(
            url, headers=headers, cookies=cookies, timeout=timeout, **kwargs
        )
        response.etc["semester"] = semester
        return response

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        soup = response.soup

        courses: Dict[str, str] = {}
        for each in soup.find_all("a", attrs={"class": "coursefullname"}):
            course_code_matching = re.search(r"[?&]id=(\d+)", each["href"])
            if not course_code_matching:
                raise ParsingError("url에서 강좌 코드번호를 추출할 수 없습니다.", response)
            course_code = course_code_matching.group(1)
            lecture_name = re.sub(r"\[.*?\]", "", each.get_text(strip=True))
            courses[lecture_name] = course_code

        semester: SemesterData = _extract_semester(response)

        return ResourceData(
            data={"courses": courses},
            link=response.url,
            meta={"selected": semester.selected, "selectable": semester.selectable},
        )


class Attendance(IParser):
    URL: str = DOMAIN_NAME + "/local/ubattendance/my_status.php?lang=ko"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        course_code: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        query = {"id": course_code}
        query_string = urlencode(query)
        url = f"{cls.URL}&{query_string}"
        return await HTTPClient.connector.get(
            url, cookies=cookies, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def _parse_summary(cls, response: Response) -> Dict[str, str]:
        soup = response.soup
        summary_container = soup.find("div", attrs={"class": "course_info well"})
        if not summary_container:
            raise ParsingError("요약 정보를 찾을 수 없습니다.", response)

        result: Dict[str, str] = {
            each.contents[0]
            .get_text(strip=True): each.contents[1]
            .replace(":", "")
            .strip()
            for each in summary_container.find_all("li")
        }
        return result

    @classmethod
    def _parse_foot(cls, response: Response) -> Dict[str, str]:
        soup = response.soup
        tfoot = soup.find("tfoot")
        if not tfoot:
            raise ParsingError("테이블 foot이 존재하지 않습니다.", response)

        result = {}
        for each in tfoot.find_all("span"):
            key = each.contents[0].get_text(strip=True)
            value = re.search(r"\d+", each.contents[1])
            if not value:
                raise ParsingError("테이블 foot에서 수치를 발견할 수 없습니다.", response)
            result[key] = value.group()
        return result

    @classmethod
    def _parse_main_table(cls, response: Response) -> Tuple[List[str], List[List[str]]]:
        soup = response.soup

        table_container = soup.find(
            "table", attrs={"class": "attendance_my table table-bordered"}
        )
        if not table_container:
            raise ParsingError("메인 테이블을 찾을 수 없습니다.", response)

        thead = table_container.find("thead")
        tbody = table_container.find("tbody")
        return parse_table(response, thead, tbody)

    @classmethod
    def _precondidtion(cls, response: Response) -> Optional[ErrorData]:
        """
        응답 코드가 200인 경우 정상
        응답 코드가 303인 경우 수강 중이지 않은 강의
        응답 코드가 404인 경우 삭제된 강의
        """

        if response.status != 200:
            return ErrorData(
                error={"title": "출석 정보를 불러올 수 없는 강의입니다."}, link=response.url,
            )
        return None

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        precondition = cls._precondidtion(response)
        if precondition is not None:
            return precondition
        else:
            summary = cls._parse_summary(response)
            head, body = cls._parse_main_table(response)
            foot = cls._parse_foot(response)
            return ResourceData(
                data={"summary": summary, "head": head, "body": body, "foot": foot},
                link=response.url,
            )
