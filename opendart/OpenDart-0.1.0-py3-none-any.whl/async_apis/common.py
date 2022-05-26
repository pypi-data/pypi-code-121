from typing import TYPE_CHECKING

from aiohttp import ClientSession, ClientResponse

from opendart.config import API_URLS

if TYPE_CHECKING:
    from opendart.models.common import ApiParams


def __check_status_code(response: ClientResponse):
    '''HTTP 통신 상태 확인'''
    if response.status != 200:
        raise Exception(response.status, response.reason)


def __check_status(result: dict):
    '''OPENDART로부터 받은 데이터가 정상인지 확인'''
    if result['status'] != '000':
        raise Exception(result['status'], result['message'])


def __is_binary(url: str) -> bool:
    return url in [
        API_URLS['corp_code']
    ]


async def __parse_xml_to_json(response: ClientResponse) -> dict:
    from io import BytesIO
    from json import loads, dumps
    from zipfile import ZipFile
    from xmltodict import parse

    _zip = ZipFile(BytesIO(await response.content.read()))
    _xml = parse(_zip.read('CORPCODE.xml').decode('utf-8'))
    return loads(dumps(_xml))


def __parse_json(result: dict) -> dict:
    __check_status(result)
    result.pop('status')
    result.pop('message')
    return result


async def fetch(session: ClientSession, url: str, params: 'ApiParams') -> dict:
    async with session.get(url, params=params) as response:

        __check_status_code(response)

        if __is_binary(url):
            return await __parse_xml_to_json(response)

        return __parse_json(await response.json())
