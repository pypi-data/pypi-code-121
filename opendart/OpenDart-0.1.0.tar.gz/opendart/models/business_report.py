from typing import TypedDict


class StockQuantityStatus(TypedDict):
    rcept_no: str
    '''접수번호 - 접수번호(14자리)'''
    corp_cls: str
    '''법인구분 - Y(유가), K(코스닥), N(코넥스), E(기타)'''
    corp_code: str
    '''고유번호 - 공시대상회사의 고유번호(8자리)'''
    corp_name: str
    '''회사명 - 공시대상회사명'''
    se: str
    '''구분(증권의종류, 합계, 비고)'''
    isu_stock_totqy: str
    '''발행할 주식의 총수'''
    now_to_isu_stock_totqy: str
    '''현재까지 발행한 주식의 총수'''
    now_to_dcrs_stock_totqy: str
    '''현재까지 감소한 주식의 총수'''
    redc: str
    '''감자 - 현재까지 감소한 주식의 총수'''
    profit_incnr: str
    '''이익소각 - 현재까지 감소한 주식의 총수'''
    rdmstk_repy: str
    '''상환주식의 상환 - 현재까지 감소한 주식의 총수'''
    etc: str
    '''기타 - 현재까지 감소한 주식의 총수'''
    istc_totqy: str
    '''발행주식의 총수'''
    tesstk_co: str
    '''자기주식수'''
    distb_stock_co: str
    '''유통주식수'''
