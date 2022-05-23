#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : SandQuant
# @Email: data@sandquant.com


suffix_SZ = ('SH', 'SZ')
suffix_SZSE = ('SSE', 'SZSE')
suffix_XSHE = ('XSHG', 'XSHE')


def code_suffix(codes, suffix):
    suffix = dict(zip(*suffix.keys(), *suffix.values()))
    if isinstance(codes, str):
        for _, __ in suffix.items():
            codes = codes.replace(_, __)
    if isinstance(codes, list):
        codes = [code_suffix(code, suffix) for code in codes]
    return codes
