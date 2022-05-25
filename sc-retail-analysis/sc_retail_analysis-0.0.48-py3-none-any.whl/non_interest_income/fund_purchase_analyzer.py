#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
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


class FundPurchaseAnalyzer(BaseAnalyzer):
    """
    基金认申购明细分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "retail.non_interest.fund_purchase.enabled"
        self._key_business_type = "retail.non_interest.fund_purchase.business_type"
        self._key_export_column_list = "retail.non_interest.fund_purchase.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        # 基金认申购明细表文件路径
        self._src_filepath = config.get("retail.non_interest.fund_purchase.source_file_path")
        # 中收比例
        self._sales_income_percentage = config.get("retail.non_interest.fund_purchase.sales_income_percentage")
        self._sheet_name = config.get("retail.non_interest.fund_purchase.sheet_name")
        self._header_row = config.get("retail.non_interest.fund_purchase.sheet_config.header_row")
        # 工号列索引
        self._id_column = config.get("retail.non_interest.fund_purchase.sheet_config.id_column")
        # 姓名列索引
        self._name_column = config.get("retail.non_interest.fund_purchase.sheet_config.name_column")
        # 持营基金销售业绩列索引
        self._holding_fund_amount_column = config.get(
            "retail.non_interest.fund_purchase.sheet_config.holding_fund_amount_column")
        # 持营基金中收列索引
        self._holding_fund_sales_income_column = config.get(
            "retail.non_interest.fund_purchase.sheet_config.holding_fund_sales_income_column")
        # 首发基金销售业绩列索引
        self._initial_fund_amount_column = config.get(
            "retail.non_interest.fund_purchase.sheet_config.initial_fund_amount_column")
        # 首发基金中收列索引
        self._initial_fund_sales_income_column = config.get(
            "retail.non_interest.fund_purchase.sheet_config.initial_fund_sales_income_column")
        # 生成的Excel中代销基金业绩的列名
        self._target_confirmed_amount_column_name = config.get(
            "retail.non_interest.fund_purchase.sheet_config.target_confirmed_amount_column_name")
        # 生成的Excel中代销基金中收的列名
        self._target_sales_income_column_name = config.get(
            "retail.non_interest.fund_purchase.sheet_config.target_sales_income_column_name")
        # 广州分行公共名称
        self._gz_common_account = config.get("branch.gz_common_account")

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        data = pd.read_excel(self._src_filepath, sheet_name=self._sheet_name, header=self._header_row)
        self._id_column_name = data.columns[self._id_column]
        self._name_column_name = data.columns[self._name_column]
        self._holding_fund_amount_column_name = data.columns[self._holding_fund_amount_column]
        self._holding_fund_sales_income_column_name = data.columns[self._holding_fund_sales_income_column]
        self._initial_fund_amount_column_name = data.columns[self._initial_fund_amount_column]
        self._initial_fund_sales_income_column_name = data.columns[self._initial_fund_sales_income_column]
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

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("解决姓名与工号不匹配的问题...")
        data = ManifestUtils.fix_name_error(data, self._id_column_name, self._name_column_name)

        # （非息）离职人员归属机构表
        employee_mapping = ManifestUtils.get_non_interest_leave_employee_branch_mapping()
        all_names = ManifestUtils.get_all_names_in_manifest()
        data[self._id_column_name].fillna(0, inplace=True)
        data[self._name_column_name].fillna("", inplace=True)
        for row_i, row in data.iterrows():
            # 处理广州分行公共数据
            id_value = row[self._id_column_name]
            try:
                id_value = int(id_value)
            except:
                pass
            name = row[self._name_column_name]
            # 工号不为0，并且姓名不在花名册，则统计为广州分行公共
            if id_value != 0 and name not in all_names:
                data.at[row_i, self._id_column_name] = 0
                branch_name = self._gz_common_account
                # 如果是离职人员，则归属到配置的离职人员机构中去
                if str(id_value) in employee_mapping.keys():
                    branch_name = employee_mapping.get(str(id_value)).get("branch")
                data.at[row_i, self._name_column_name] = branch_name
            # 工号为0，并且姓名不在花名册，则统计为广州分行公共
            if id_value == 0 and name not in all_names:
                branch_name = self._gz_common_account
                data.at[row_i, self._name_column_name] = branch_name

        # 添加业绩列
        data[self._target_confirmed_amount_column_name] = data[self._holding_fund_amount_column_name] + data[
            self._initial_fund_amount_column_name]
        # 添加中收列
        data[self._target_sales_income_column_name] = data[self._holding_fund_sales_income_column_name] + data[
            self._initial_fund_sales_income_column_name]
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        index_columns = [self._id_column_name, self._name_column_name]
        value_columns = [self._target_confirmed_amount_column_name, self._target_sales_income_column_name]
        if data.empty:
            return pd.DataFrame(columns=index_columns + value_columns)
        table = pd.pivot_table(data, values=value_columns,
                               index=index_columns,
                               aggfunc=np.sum, fill_value=0)
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data.reset_index(inplace=True)
        data[self._id_column_name] = data[self._id_column_name].astype("int64")
        return data

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与花名册合并...")
        merge_result = ManifestUtils.merge_with_manifest(manifest_data=manifest_data, data=data,
                                                         id_column_name=self._id_column_name,
                                                         name_column_name=self._name_column_name)
        return merge_result

    def _add_target_columns(self) -> None:
        self._add_target_column(self._target_confirmed_amount_column_name)
        self._add_target_column(self._target_sales_income_column_name)
