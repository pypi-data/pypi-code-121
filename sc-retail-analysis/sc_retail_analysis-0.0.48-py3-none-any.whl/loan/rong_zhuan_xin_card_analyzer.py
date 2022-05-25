#  The MIT License (MIT)
#
#  Copyright (c) 2022. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import logging

import numpy as np
import pandas as pd
from config42 import ConfigManager
from sc_analyzer_base import ManifestUtils

from sc_retail_analysis.analyzer.base_analyzer import BaseAnalyzer


class RongZhuanXinAnalyzer(BaseAnalyzer):
    """
    融意通、心意通、转账支付卡分析基础类
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        # 基于客户名称的原始数据
        self._client_origin_data = pd.DataFrame()
        # 基于客户名称统计的数据
        self._client_data = pd.DataFrame()

    def _read_config(self, *, config: ConfigManager):
        # 明细表文件路径
        self._src_filepath = None
        # Sheet名称
        self._sheet_name = None
        # 表头行索引
        self._header_row = None
        # 客户经理列索引
        self._name_column = None
        # 客户姓名列索引
        self._client_name_column = None
        # 客户联系方式列索引
        self._client_contact_info_column = None

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        data = pd.read_excel(self._src_filepath, sheet_name=self._sheet_name, header=self._header_row)
        self._name_column_name = data.columns[self._name_column]
        self._client_name_column_name = data.columns[self._client_name_column]
        self._client_contact_info_column_name = data.columns[self._client_contact_info_column]
        self._init_value_column_pairs(data)
        # if not data.empty:
        #     # 筛选余额不为0的记录
        #     criterion = data[self._advance_amount_column_name].map(lambda x: x != 0)
        #     data = data[criterion].copy()
        return data

    def _add_export_column_manifest_branch(self, origin_data: pd.DataFrame):
        if origin_data is None or origin_data.empty:
            return origin_data
        # 与花名册整合，添加花名册所在部门一列
        data = origin_data.merge(
            ManifestUtils.get_name_branch_data_frame(),
            how="left",
            left_on=[self._name_column_name],
            right_on=[ManifestUtils.get_name_column_name()]
        )
        return data

    def _rename_target_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        df = data.rename(columns=self._value_column_pairs)
        return df

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        self._client_origin_data = data.copy()
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        index_columns = [self._name_column_name]
        value_columns = self._get_value_columns()
        logging.getLogger(__name__).info("按{} 透视数据项：{}".format(
            index_columns,
            value_columns,
        ))
        if data.empty:
            return pd.DataFrame(columns=index_columns + value_columns)
        table = pd.pivot_table(
            data=data,
            values=value_columns,
            index=index_columns,
            aggfunc=np.sum,
            fill_value=0,
        )
        if self._client_origin_data is not None and (not self._client_origin_data.empty):
            index_columns = [
                self._client_name_column_name,
                self._client_contact_info_column_name,
                self._name_column_name,
            ]
            self._client_data = pd.pivot_table(
                data=self._client_origin_data,
                values=value_columns,
                index=index_columns,
                aggfunc=np.sum,
                fill_value=0,
            )
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        self._client_data = self._client_data.reset_index()
        return data.reset_index()

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与花名册合并...")
        merge_result = ManifestUtils.merge_with_manifest(
            manifest_data=manifest_data,
            data=data,
            name_column_name=self._name_column_name,
        )
        self._client_data = ManifestUtils.merge_with_manifest(
            manifest_data=manifest_data,
            data=self._client_data,
            name_column_name=self._name_column_name,
            how="right",
        )
        return merge_result

    def _drop_duplicated_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=[self._name_column_name])

    def _add_target_columns(self) -> None:
        self._add_value_pair_target_columns()

    def write_detail_report(self, data: pd.DataFrame):
        super().write_detail_report(data=data)
        # 如果未启用，则直接返回
        if not self._enabled():
            return
        # 没有数据
        if self._client_data is None or self._client_data.empty:
            return
        # 将按客户统计维度的数据输出
        self._client_data.to_excel(
            excel_writer=self._excel_writer,
            index=False,
            sheet_name=self._business_type + "-按客户统计",
        )
