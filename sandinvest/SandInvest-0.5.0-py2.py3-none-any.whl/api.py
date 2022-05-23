#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : SandQuant
# @Email: data@sandquant.com
import pandas as pd

from .client import SandInvestClient


def description(type_=str):
    type_ = str(type_)
    return SandInvestClient().index(**locals())


def my_account() -> dict:
    return SandInvestClient().my_account(**locals())


def get_calendar(start_date=None, end_date=None, date=None, offset=0, include=True, type_=None):
    type_ = str(type_)
    return SandInvestClient().get_calendar(**locals())


def is_trading(date=None) -> bool:
    result = get_calendar(date=date)
    if result.empty:
        return False
    else:
        return True


def is_break(date=None) -> bool:
    return not is_trading(date=date)


def get_summary(codes=None, start_date=None, end_date=None, date=None, list_date=None, delist_date=None,
                fields=None, include=True, delisted=False) -> pd.DataFrame:
    if isinstance(codes, (list, tuple)):
        codes = ','.join(codes)
    if isinstance(fields, (list, tuple)):
        fields = ','.join(fields)
    return SandInvestClient().get_summary(**locals())


def get_price(codes=None, start_date=None, end_date=None, date=None,
              offset=0, freq='D', include=True, fields=None, skip=False, fill=True, adj=0) -> pd.DataFrame:
    if isinstance(codes, (list, tuple)):
        codes = ','.join(codes)
    if isinstance(fields, (list, tuple)):
        fields = ','.join(fields)
    return SandInvestClient().get_price(**locals())


def get_shares(codes=None, start_date=None, end_date=None, date=None,
               offset=0, include=True, fields=None) -> pd.DataFrame:
    if isinstance(codes, (list, tuple)):
        codes = ','.join(codes)
    if isinstance(fields, (list, tuple)):
        fields = ','.join(fields)
    return SandInvestClient().get_shares(**locals())


def get_industry(codes=None, ind_codes=None, source=None, date=None, fields=None, type_=None):
    type_ = str(type_)
    if isinstance(codes, (list, tuple)):
        codes = ','.join(codes)
    if isinstance(ind_codes, (list, tuple)):
        ind_codes = ','.join(ind_codes)
    if isinstance(fields, (list, tuple)):
        fields = ','.join(fields)
    return SandInvestClient().get_industry(**locals())


def get_auction(codes=None, start_date=None, end_date=None, date=None,
                offset=0, include=True, fields=None, adj=0) -> pd.DataFrame:
    if isinstance(codes, (list, tuple)):
        codes = ','.join(codes)
    if isinstance(fields, (list, tuple)):
        fields = ','.join(fields)
    return SandInvestClient().get_auction(**locals())


def get_method(method, **params):
    return exec(f"SandInvestClient().{method}(**{params})")
