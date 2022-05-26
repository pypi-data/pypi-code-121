'''(비동기) 공시정보 APIs

See Also
--------
- https://opendart.fss.or.kr/guide/main.do?apiGrpCd=DS001
'''

from typing import TYPE_CHECKING, List

import aiohttp
from opendart.async_apis.common import fetch
from opendart.config import API_URLS, DART_API_KEY

if TYPE_CHECKING:
    from opendart.models.public_notice import CorpCodeParams, Corporation, CorpOverviewParams, CorpOverview


async def fetch_all_corp() -> List['Corporation']:
    '''(비동기) 고유번호 조회

    - API URL: `https://opendart.fss.or.kr/api/corpCode.xml`
    - API Params: `{ crtfc_key: API_KEY }`

    공시대상회사 목록을 조회합니다.

    WARNING
    -------
    다른 API와는 다르게 xml 방식만 지원합니다.
    하지만 실제 반환값(출력포맷)은 Zip file이기 때문에,
    압축을 풀고 xml을 json으로 변환하는 작업이 수행됩니다.

    시간이 걸리는 API이므로 매번 호출하지 않고,
    조회 결과 리스트를 별도 파일로 저장하거나 DB와 연동하여 관리하는 것을 권장합니다.
    '''

    url = API_URLS['corp_code']
    params: 'CorpCodeParams' = { 'crtfc_key': DART_API_KEY }

    async with aiohttp.ClientSession() as session:
        result = await fetch(session, url, params)
        return result['result']['list']


async def fetch_all_listed_corp() -> List['Corporation']:
    '''(비동기) 상장회사 목록 조회

    공시대상회사 목록 중 상장사 목록을 조회합니다.

    WARNING
    -------
    약 9만 개 공시대상회사 목록 중 상장회사 목록을 조회합니다.
    고유번호 조회 후 필터링하기 때문에 시간이 다소 걸릴 수 있습니다.
    따라서 매번 호출하지 않고 별도 파일로 저장하거나 DB를 연동해서 관리하는 것을 권장합니다.

    또한, 이 API는 Dart에서 직접 제공하지 않아 편의를 위해 만들었습니다.
    단순히 고유번호 조회 API에서 종목코드를 보유한 회사 목록으로 걸러냈습니다.
    회사 고유번호를 별도로 관리하고 있다면 직접 개발하는 것을 권장합니다.

    See also :func:`api.public_notice.fetch_all_corp()`
    '''
    return list(filter(lambda c: c['stock_code'], await fetch_all_corp()))


async def fetch_corp_overview_by_corp_code(corp_code: str) -> 'CorpOverview':
    '''(비동기) 기업개황 조회

    - API URL: `https://opendart.fss.or.kr/api/company.json`
    - API Params `{
        crtfc_key: API_KEY,
        corp_code: 고유번호
    }`

    고유번호를 통해 해당하는 기업의 개황정보를 조회합니다.
    '''
    url = API_URLS['corp_overview']
    params: 'CorpOverviewParams' = {
        'crtfc_key': DART_API_KEY,
        'corp_code': corp_code
    }

    async with aiohttp.ClientSession() as session:
        return await fetch(session, url, params)
