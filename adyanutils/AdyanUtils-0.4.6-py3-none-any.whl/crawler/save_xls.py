#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/22 9:24
# @Author  : Adyan
# @File    : save_xls.py


import xlrd
import xlwt
from xlutils.copy import copy


class SaveXls:

    @staticmethod
    def write_excel_xls(path, sheet_name, value):
        index = len(value)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet(sheet_name)
        for i in range(0, index):
            for j in range(0, len(value[i])):
                sheet.write(i, j, value[i][j])
        workbook.save(path)

    @staticmethod
    def write_excel_xls_append(path, value):
        index = len(value)
        workbook = xlrd.open_workbook(path)
        sheets = workbook.sheet_names()
        worksheet = workbook.sheet_by_name(sheets[0])
        rows_old = worksheet.nrows
        new_workbook = copy(workbook)
        new_worksheet = new_workbook.get_sheet(0)
        for i in range(0, index):
            for j in range(0, len(value[i])):
                new_worksheet.write(i + rows_old, j, value[i][j])
        new_workbook.save(path)
        print("xls格式表格【追加】写入数据成功！")

    @staticmethod
    def read_excel_xls(path):
        workbook = xlrd.open_workbook(path)
        sheets = workbook.sheet_names()
        worksheet = workbook.sheet_by_name(sheets[0])
        for i in range(0, worksheet.nrows):
            for j in range(0, worksheet.ncols):
                print(worksheet.cell_value(i, j), "\t", end="")
