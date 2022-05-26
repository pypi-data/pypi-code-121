from typing import TypedDict


class ApiUrls(TypedDict):
    corp_code: str
    '''고유번호'''
    corp_overview: str
    '''기업개황'''
    stock_total_quantity: str
    '''주식의 총수 현황'''

API_URLS: ApiUrls = {
    'corp_code': 'https://opendart.fss.or.kr/api/corpCode.xml',
    'corp_overview': 'https://opendart.fss.or.kr/api/company.json',
    'stock_total_quantity': 'https://opendart.fss.or.kr/api/stockTotqySttus.json',
}
'''API URL 목록'''
