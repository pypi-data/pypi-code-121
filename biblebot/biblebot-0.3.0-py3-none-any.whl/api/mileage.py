from typing import Optional, Dict, List
from abc import ABCMeta, abstractmethod
from dataclasses import asdict

from ..reqeust import Response
from ..exceptions import ParsingError
from .base import (
    HTTPClient,
    IParser,
    ILoginFetcher,
    APIResponseType,
    ErrorData,
    ResourceData,
    ParserPrecondition,
)
from .common import extract_alerts, httpdate_to_unixtime
from ._mileage import (
    translate_mileage_req,
    translate_statement_type,
    SearchParamData,
    StatementParamData,
)

__all__ = (
    "Login",
    "Search",
    "Statement",
)

DOMAIN_NAME: str = "https://asp.netusys.com"


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
        message_tag = response.soup.find("message")
        if message_tag and "세션정보" in message_tag.get_text(strip=True):
            return ErrorData(error={"title": "마일리지 세션이 만료되었습니다."}, link=response.url)

        return None


class Login(ILoginFetcher, IParser):
    URL: str = DOMAIN_NAME + "/login/login_check.jsp"
    DEFAULT_HEADERS: Dict[str, str] = {
        "referer": "https://asp.netusys.com/mobile/login/login_form.jsp?logoutFg=Y"
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
        headers = headers or {}
        headers.update(cls.DEFAULT_HEADERS)
        form: Dict[str, str] = {
            "user_id": user_id,
            "user_pwd": user_pw,
            "mac_addr": "",
            "AutoFg": "M",
            "appfg": "web",
            "logoutFg": "Y",
            "login_auto_serial": "",
        }

        response = await HTTPClient.connector.post(
            cls.URL, headers=headers, body=form, timeout=timeout, verify=False, **kwargs
        )
        return response

    @classmethod
    def parse(cls, response: Response) -> APIResponseType:
        """
        성 공:          유효한 alert 없음, top.location.replace('/mobile/login/main.jsp?appfg=web&appYndHis=20200223201758');
        비밀번호 틀림:    유효한 alert 존재, top.location.replace('/mobile/login/login_form.jsp?logoutFg=Y');
        아이디가 틀림:    유효한 alert 존재, top.location.replace('/mobile/login/login_form.jsp?logoutFg=Y');
        """
        alerts = extract_alerts(response.soup)
        if alerts:
            return ErrorData(
                error={"title": alerts[0], "alert_messages": alerts}, link=response.url
            )
        iat = httpdate_to_unixtime(response.headers["date"])
        return ResourceData(
            data={"cookies": response.cookies, "iat": iat}, link=response.url
        )


def _parse_xml_data(response: Response) -> ResourceData:
    soup = response.soup

    data_container = soup.find("data")
    if not data_container:
        raise ParsingError("데이터를 찾을 수 없습니다.", response)

    total_rows_tag = soup.find("etc", attrs={"key": "total_rows"})
    if not total_rows_tag:
        raise ParsingError("전체 길이를 구할 수 없습니다.", response)

    total_row: str = total_rows_tag.get_text(strip=True)

    search_param = response.etc["req"]
    head: List[str] = translate_mileage_req(search_param.get_req())
    body: List[List[str]] = [
        [td.get_text(strip=True) for td in each.find_all("td")]
        for each in data_container.find_all("tr")
    ]
    page_num: str = search_param.get_page_num()

    if body:
        if len(head) != len(body[0]):
            raise ParsingError("데이터 헤드와 바디의 길이가 일치하지 않습니다.", response)

    return ResourceData(
        data={"head": head, "body": body},
        meta={"total_size": total_row, "current_size": len(body), "page_n": page_num,},
        link=response.url,
    )


class Search(IParser):
    URL: str = DOMAIN_NAME + "/ddd.sheetAction"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        search_param: Optional[SearchParamData] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        search_param = search_param or SearchParamData()
        response = await HTTPClient.connector.post(
            cls.URL,
            headers=headers,
            body=asdict(search_param),
            cookies=cookies,
            timeout=timeout,
            verify=False,
            **kwargs,
        )

        response.etc["req"]: SearchParamData = search_param

        return response

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        return _parse_xml_data(response)


class Statement(IParser):
    URL: str = DOMAIN_NAME + "/ddd.sheetAction"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        search_param: Optional[StatementParamData] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        search_param = search_param or StatementParamData()
        response = await HTTPClient.connector.post(
            cls.URL,
            headers=headers,
            body=asdict(search_param),
            cookies=cookies,
            timeout=timeout,
            verify=False,
            **kwargs,
        )

        response.etc["req"]: StatementParamData = search_param

        return response

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        result: ResourceData = _parse_xml_data(response)
        try:
            type_index = result.data["head"].index("구분")
        except ValueError:
            raise ParsingError("헤드에 마일리지변동 구분값이 존재하지 않습니다.", response)
        else:
            for each in result.data["body"]:
                each[type_index] = translate_statement_type(each[type_index])
        return result
