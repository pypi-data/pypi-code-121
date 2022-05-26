from typing import TypedDict

from opendart.models.common import ApiParams


class Corporation(TypedDict):
    '''고유번호 DTO'''
    corp_code: str
    '''고유번호 - 공시대상회사의 고유번호(8자리)'''
    corp_name: str
    '''정식명칭 - 정식회사명칭'''
    stock_code: str
    '''종목코드 - 상장회사인 경우 주식의 종목코드(6자리)'''
    modify_date: str
    '''최종변경일자 - 기업개황정보 최종변경일자(YYYYMMDD)'''

class CorpOverview(TypedDict):
    '''기업개황 DTO'''
    corp_name: str
    '''정식명칭 - 정식회사명칭'''
    corp_name_eng: str
    '''영문명칭 - 영문정식회사명칭'''
    stock_name: str
    '''종목명(상장사) 또는 약식명칭(기타법인) - '''
    stock_code: str
    '''상장회사인 경우 주식의 종목코드(6자리)'''
    ceo_nm: str
    '''대표자명'''
    corp_cls: str
    '''법인구분 - Y(유가), K(코스닥), N(코넥스), E(기타)'''
    jurir_no: str
    '''법인등록번호'''
    bizr_no: str
    '''사업자등록번호'''
    adres: str
    '''주소'''
    hm_url: str
    '''홈페이지'''
    ir_url: str
    '''IR홈페이지'''
    phn_no: str
    '''전화번호'''
    fax_no: str
    '''팩스번호'''
    induty_code: str
    '''업종코드'''
    est_dt: str
    '''설립일(YYYYMMDD)'''
    acc_mt: str
    '''결산월(MM)'''


class CorpCodeParams(ApiParams):
    '''고유번호 Params'''

class CorpOverviewParams(ApiParams):
    '''기업개황 Params'''
    corp_code: str
    '''고유번호 - 공시대상회사의 고유번호(8자리)'''
