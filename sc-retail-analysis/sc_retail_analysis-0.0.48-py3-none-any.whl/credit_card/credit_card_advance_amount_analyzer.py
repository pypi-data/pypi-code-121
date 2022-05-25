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


class CreditCardAdvanceAmountAnalyzer(BaseAnalyzer):
    """
    分支行信用卡垫款余额
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "retail.credit_card.advance_amount_balance.enabled"
        self._key_business_type = "retail.credit_card.advance_amount_balance.business_type"
        self._key_export_column_list = "retail.credit_card.advance_amount_balance.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        # 信用卡收入报表文件路径
        self._src_filepath = config.get("retail.credit_card.advance_amount_balance.source_file_path")
        # Sheet名称
        self._sheet_name = config.get("retail.credit_card.advance_amount_balance.sheet_name")
        # 表头行索引
        self._header_row = config.get("retail.credit_card.advance_amount_balance.sheet_config.header_row")
        # 员工工号列索引
        self._id_column = config.get("retail.credit_card.advance_amount_balance.sheet_config.id_column")
        # 员工姓名列索引
        self._name_column = config.get("retail.credit_card.advance_amount_balance.sheet_config.name_column")
        # 广州分行公共名称
        self._gz_common_account = config.get("branch.gz_common_account")
        # 需要统计的列的索引与输出列名对
        key = "retail.credit_card.advance_amount_balance.sheet_config.value_column_pairs"
        self._init_value_column_config(config, key)

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        data = pd.read_excel(self._src_filepath, sheet_name=self._sheet_name, header=self._header_row)
        # 解决工号、姓名没有列名的问题
        data = data.rename(columns={
            data.columns[self._id_column]: ManifestUtils.get_id_column_name(),
            data.columns[self._name_column]: ManifestUtils.get_name_column_name(),
        })
        self._id_column_name = data.columns[self._id_column]
        self._name_column_name = data.columns[self._name_column]
        self._init_value_column_pairs(data)
        if not data.empty:
            if len(self._value_column_pairs) > 0:
                for key in self._value_column_pairs.keys():
                    # 筛选不为0的记录
                    criterion = data[key].map(lambda x: x != 0)
                    data = data[criterion].copy()
            # 工号前面的列可能包括合计，去除合计行
            for index in range(self._id_column):
                # 过滤合计行
                if not data.empty:
                    criterion = data[data.columns[index]].map(lambda x: x != '合计')
                    data = data[criterion].copy()
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
        all_names = ManifestUtils.get_all_names_in_manifest()
        data[self._id_column_name].fillna(0, inplace=True)
        data[self._name_column_name].fillna("", inplace=True)
        for row_i, row in data.iterrows():
            id_value = row[self._id_column_name]
            name = row[self._name_column_name]
            # 如果工号为0，姓名为空，则统计为广州分行公共
            if id_value == 0 and name == "":
                data.at[row_i, self._name_column_name] = self._gz_common_account
                continue
            # 工号不为0，并且姓名不在花名册，则统计为广州分行公共
            if id_value != 0 and name not in all_names:
                data.at[row_i, self._name_column_name] = self._gz_common_account
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
        table = pd.pivot_table(data, values=value_columns,
                               index=index_columns,
                               aggfunc=np.sum, fill_value=0)
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.reset_index()

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与花名册合并...")
        merge_result = ManifestUtils.merge_with_manifest(manifest_data=manifest_data, data=data,
                                                         name_column_name=self._name_column_name)
        return merge_result

    def _add_target_columns(self) -> None:
        self._add_value_pair_target_columns()
