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
import os

import numpy as np
import pandas as pd
from config42 import ConfigManager
from sc_analyzer_base import ManifestUtils

from sc_retail_analysis.analyzer.base_analyzer import BaseAnalyzer
from sc_retail_analysis.utils import MoneyUtils


class ConsumptionLoanProductivityAnalyzer(BaseAnalyzer):
    """
    分支行消费信贷产能表分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "retail.loan.consumption_loan_productivity.enabled"
        self._key_business_type = "retail.loan.consumption_loan_productivity.business_type"
        self._key_export_column_list = "retail.loan.consumption_loan_productivity.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        # 生成的目标Excel文件存放路径
        self._target_directory = config.get("retail.target_directory")
        self._target_report_filename = config.get("retail.target_report_filename")
        # 信用卡大额分期报表文件路径
        self._src_filepath = config.get("retail.loan.consumption_loan_productivity.source_file_path")
        # Sheet名称
        self._sheet_name = config.get("retail.loan.consumption_loan_productivity.sheet_name")
        # 过滤的机构名称
        self._filter_branch_name = config.get("retail.loan.consumption_loan_productivity.filter_branch_name")
        # 表头行索引
        self._header_row = config.get("retail.loan.consumption_loan_productivity.sheet_config.header_row")
        # 员工工号列索引
        self._id_column = config.get("retail.loan.consumption_loan_productivity.sheet_config.id_column")
        # 员工姓名列索引
        self._name_column = config.get("retail.loan.consumption_loan_productivity.sheet_config.name_column")
        # 分支行列索引
        self._branch_column = config.get("retail.loan.consumption_loan_productivity.sheet_config.branch_column")
        # 需要统计的列的索引与输出列名对
        key = "retail.loan.consumption_loan_productivity.sheet_config.value_column_pairs"
        self._init_value_column_config(config, key)
        # 需要统计的列的索引与输出列名对
        key = "retail.loan.consumption_loan_productivity.sheet_config.report_column_pairs"
        self._init_report_column_config(config, key)

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        data = pd.read_excel(self._src_filepath, sheet_name=self._sheet_name, header=self._header_row)
        self._id_column_name = data.columns[self._id_column]
        self._name_column_name = data.columns[self._name_column]
        self._branch_column_name = data.columns[self._branch_column]
        self._init_value_column_pairs(data)
        self._init_report_column_pairs(data)
        return data

    def _rename_target_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        df = data.rename(columns=self._value_column_pairs)
        return df

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 过滤机构
        criterion = data[self._branch_column_name].map(lambda x: x == self._filter_branch_name)
        data = data[criterion].copy()
        data[self._id_column_name] = data[self._id_column_name].astype("int64")
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        index_columns = [self._id_column_name, self._name_column_name]
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
        merge_result = ManifestUtils.merge_with_manifest(
            manifest_data=manifest_data,
            data=data,
            id_column_name=self._id_column_name,
            name_column_name=self._name_column_name,
        )
        return merge_result

    def write_detail_report(self, data: pd.DataFrame):
        super().write_detail_report(data)
        target_filename_full_path = os.path.join(self._target_directory, self._target_report_filename)
        logging.getLogger(__name__).info("输出播报文件：{} ".format(target_filename_full_path))
        # 如果文件已经存在，则采用追加的模式
        mode = 'a' if os.path.exists(target_filename_full_path) else 'w'
        # 如果Sheet已经存在则替换原有的Sheet
        replace_strategy = 'replace' if mode == 'a' else None
        with open(target_filename_full_path, mode=mode) as writer:
            for config_pairs in self._report_column_pairs.values():
                title = config_pairs['title']
                unit = config_pairs['unit']
                writer.write(title + "：\n")
                for row_i, row in data.iterrows():
                    value = row[title]
                    if np.isnan(value):
                        continue
                    if value <= 0:
                        continue
                    value = int(value)
                    divider = MoneyUtils.get_money_unit_divider(unit)
                    if divider != 1:
                        value = value / divider
                    name = row[ManifestUtils.get_name_column_name()]
                    branch = row[ManifestUtils.get_branch_column_name()]
                    writer.write(name + " 【" + branch + "】 " + str(value) + " " + unit + "\n")

    def _drop_duplicated_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=[self._id_column_name, self._name_column_name])

    def _add_target_columns(self) -> None:
        self._add_value_pair_target_columns()
