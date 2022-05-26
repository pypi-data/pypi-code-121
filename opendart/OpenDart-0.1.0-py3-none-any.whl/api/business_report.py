'''사업보고서 APIs

https://opendart.fss.or.kr/guide/main.do?apiGrpCd=DS002
'''

from typing import TYPE_CHECKING, List, Union

from opendart.api.common import fetch, parse_json
from opendart.config import API_URLS, DART_API_KEY

if TYPE_CHECKING:
    from opendart.models.business_report import StockQuantityStatus


def fetch_stock_total_quantity_status(
    corp_code: str,
    bsns_year: Union[str, int],
    reprt_code: Union[str, int] = 11011
) -> List['StockQuantityStatus']:
    '''주식의 총수 현황

    Parameters
    ----------
    corp_code: str
            고유번호(8자리)
    bsns_year: str or int
            사업연도(4자리) - 2015년도 이후 자료부터 제공
    reprt_code: str
            보고서 코드 - 1분기(11013), 반기(11012), 3분기(11014), 사업보고서(11011)
                default: 사업보고서(11011)

    - API URL: `https://opendart.fss.or.kr/api/stockTotqySttus.json`
    - API Params: `{
        crtfc_key: API_KEY,
        corp_code: 고유번호,
        bsns_year: 사업연도,
        reprt_code: 사업보고서(11011)
    }`
    '''

    url = API_URLS['stock_total_quantity']
    params = {
        'crtfc_key': DART_API_KEY,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code
    }
    return parse_json(fetch(url, params))['list']


def fetch_total_issued_stock_by_corp_code(
    corp_code: str,
    is_preferred_stock: bool = False
) -> int:
    '''발행 주식 총 수

    Dart에서 보통주인지 우선주인지에 따라 구분해야 하기 때문에
    우선주의 발행 주식 총 수를 구하려면 두 번째 인자에 명시해야 합니다.

    Parameters
    ----------
    corp_code: str
            고유번호(8자리)
    is_preferred_stock: bool
            우선주 여부
                default: False

    # TODO 사업계획서(11011) 기준이라 bsns_year 값을 작년으로 잡았는데, 이게 맞나?
    '''
    from datetime import date
    reports = fetch_stock_total_quantity_status(
        corp_code,
        date.today().year - 1
    )
    def compare(x: 'StockQuantityStatus') -> bool:
        return x['se'] == ('우선주' if is_preferred_stock else '보통주')
    total_issued_stock = list(filter(compare, reports)).pop()
    return int(total_issued_stock.get('distb_stock_co').replace(',',''))
