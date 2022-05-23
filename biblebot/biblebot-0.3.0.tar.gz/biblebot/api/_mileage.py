from dataclasses import dataclass
from typing import List, Tuple, Dict

__all__ = (
    "translate_mileage_req",
    "translate_statement_type",
    "SearchParamData",
    "StatementParamData",
)


_REQ_MEANINGS: Dict[str, str] = {
    "CST_NO": "회원번호",
    "CST_NM": "회원명",
    "CST_CARD_NO": "카드번호",
    "PROD_CD": "상품코드",
    "PROD_NM": "상품명",
    "dataSeq": "dataSeq",
    "SALE_QTY": "판매수량",
    "TOT_SALE_AMT": "총매출",
    "TOT_DC_AMT": "할인액",
    "DCM_SALE_AMT": "순매출",
    "SALE_DATE": "판매일자",
    "SALE_TIME": "판매시간",
    "SHOP_NM": "매장명",
    "CST_USE_POINT": "사용포인트",
    "CHG_DATE": "변경일자",
    "CHG_FG": "구분",
    "POINT": "포인트",
    "REMARK": "비고",
    "CST_CLS_NM": "회원등급",
    "BIRTH_DATE": "생일",
    "TEL_NO": "전화번호",
    "HP_NO": "휴대폰번호",
    "SMS_RECV_YN": "SMS수신여부",
    "HP_CHK": "HP_CHK",
    "SMS_REJECT_YN": "SMS_REJECT_YN",
    "USESHOP_ACC_POINT": "USESHOP_ACC_POINT",
    "USESHOP_USE_POINT": "USESHOP_USE_POINT",
    "USESHOP_ADJ_POINT": "USESHOP_ADJ_POINT",
    "USESHOP_ACC_SALE_CNT": "USESHOP_ACC_SALE_CNT",
    "USESHOP_ACC_SALE_AMT": "USESHOP_ACC_SALE_AMT",
    "USESHOP_F_SALE_DATE": "USESHOP_F_SALE_DATE",
    "USESHOP_L_SALE_DATE": "USESHOP_L_SALE_DATE",
    "ACC_POINT": "포인트적립",
    "USE_POINT": "포인트사용",
    "ADJ_POINT": "포인트조정",
    "AVL_POINT": "포인트가용",
    "ACC_SALE_CNT": "결제횟수",
    "ACC_SALE_AMT": "결제금액",
    "F_SALE_DATE": "최초방문일",
    "L_SALE_DATE": "최종방문일",
    "INS_DT": "가입일",
    "TERM_ACC_POINT": "TERM_ACC_POINT",
    "TERM_USE_POINT": "TERM_USE_POINT",
    "TERM_ADJ_POINT": "TERM_ADJ_POINT",
    "TERM_AVL_POINT": "TERM_AVL_POINT",
    "ADDR": "주소",
    "DM_RECV_YN": "DM수신여부",
    "CST_ID": "회원참조",
}

_STATEMENT_TYPES: Dict[str, str] = {
    "0": "신규",
    "1": "이관",
    "2": "조정",
    "3": "적립",
    "4": "적립취소",
    "5": "사용",
    "6": "사용취소",
}


def translate_mileage_req(request_information_str: str) -> List[str]:
    return [
        _REQ_MEANINGS.get(each, each) for each in request_information_str.split("|")
    ]


def translate_statement_type(statement_type: str) -> str:
    return _STATEMENT_TYPES.get(statement_type, statement_type)


@dataclass
class SearchParamData:
    birth_day: str = "01"
    birth_day2: str = "01"
    birth_month: str = "01"
    birth_month2: str = "01"
    cst_nos: str = ""
    date1_1: str = "2019-08-12"  # 과거 날짜여도 상관 없음
    date1_2: str = "2019-08-12"  # 과거 날짜여도 상관 없음
    date_period1: str = "366"
    list: str = ""
    mySheet1: str = ""
    page_no: str = "1"  # ✓
    page_size: str = "5000"  # ✓
    page_url: str = "/master/cust/cust020.jsp"
    r_ogn_cd: str = "HNON"
    r_ogn_fg: str = "C"
    row_cnt: str = ""
    CHG_SHOP_CD: str = ""
    CST_CARD_NO: str = ""  # ✓ 학번 검색
    CST_CARD_USE_FG: str = ""
    CST_CLS_CD: str = ""
    CST_ID: str = ""
    CST_NM: str = ""
    CST_NO: str = ""  # # ✓ 회원번호 검색
    DATE_FG: str = "A"
    DM_RECV_YN: str = ""
    EMAIL_ADDR: str = ""
    EMAIL_RECV_YN: str = ""
    EX_CST: str = ""
    EX_VISIT: str = ""
    HP_CARD1: str = ""
    HP_CARD2: str = ""
    HP_NO1: str = ""  # ✓ 010/011/016
    HP_NO2: str = ""  # ✓ aaaa/aaa
    HP_NO3: str = ""  # ✓ bbbb
    HP_SALE1: str = ""
    HP_SALE2: str = ""
    INS_SHOP_CD: str = ""
    MVIEW_YN: str = "N"
    ORDERYN: str = ""
    PNT_FG: str = "A"
    SALE_FG: str = "C"
    SEX_FG: str = "A"
    SHEETSEQ: str = "1"
    SMS_RECV_YN: str = ""
    S_CONTROLLER: str = "master.cust.cust020"
    S_CST_NM: str = ""
    S_FORWARD: str = ""
    S_METHOD: str = "search"
    S_SAVENAME: str = "CST_NO|CST_NM|CST_CLS_NM|CST_CARD_NO|ACC_POINT|USE_POINT|ADJ_POINT|AVL_POINT|ACC_SALE_CNT|ACC_SALE_AMT|INS_DT"
    S_TEL_NO: str = ""
    S_TREECOL: str = ""
    SaleYN: str = ""
    TEL_NO1: str = ""
    TEL_NO2: str = ""
    TEL_NO3: str = ""
    TERM_FG: str = "A"
    USE_YN: str = ""
    WEDDING_YN: str = "A"

    def get_req(self) -> str:
        return self.S_SAVENAME

    def set_req(self, req_info: str):
        self.S_SAVENAME = req_info
        return self

    def get_student_id(self) -> str:
        return self.CST_CARD_NO

    def set_student_id(self, student_id: str):
        self.CST_CARD_NO = student_id
        return self

    def get_customer_id(self) -> str:
        return self.CST_NO

    def set_customer_id(self, customer_id: str):
        self.CST_NO = customer_id
        return self

    def get_page_num(self) -> str:
        return self.page_no

    def set_page_num(self, num: str):
        self.page_no = num
        return self

    def get_page_size(self) -> str:
        return self.page_size

    def set_page_size(self, size: str):
        self.page_size = size
        return self

    def get_phone_number(self) -> Tuple[str, str, str]:
        return self.HP_NO1, self.HP_NO2, self.HP_NO3

    def set_phone_number(self, a: str, b: str, c: str):
        self.HP_NO1 = a
        self.HP_NO2 = b
        self.HP_NO3 = c
        return self


@dataclass
class StatementParamData:
    S_CONTROLLER: str = "master.cust.cust020_cst_info"
    S_METHOD: str = "search"
    S_SAVENAME: str = "CHG_DATE|SALE_DATE|CHG_FG|POINT|REMARK"
    SHEETSEQ: str = "2"
    CST_NO: str = ""  # ✓ 고객번호
    page_no: str = "1"
    page_no2: str = "1"
    page_size: str = "2000"
    page_size2: str = "2000"

    def get_req(self) -> str:
        return self.S_SAVENAME

    def set_req(self, req_info: str):
        self.S_SAVENAME = req_info
        return self

    def get_customer_id(self) -> str:
        return self.CST_NO

    def set_customer_id(self, customer_id: str):
        self.CST_NO = customer_id
        return self

    def get_page_num(self) -> str:
        return self.page_no

    def set_page_num(self, num: str):
        self.page_no = num
        return self

    def get_page_size(self) -> str:
        return self.page_size

    def set_page_size(self, size: str):
        self.page_size = size
        return self
