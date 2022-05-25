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


class FinancingAnalyzer(BaseAnalyzer):
    """
    理财年化日均及中收分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "retail.non_interest.financing.enabled"
        self._key_business_type = "retail.non_interest.financing.business_type"
        self._key_export_column_list = "retail.non_interest.financing.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        # 生成的目标Excel文件存放路径
        self._target_directory = config.get("retail.target_directory")
        # 目标文件名称
        self._target_filename = config.get("retail.target_filename")
        self._src_filepath = config.get("retail.non_interest.financing.source_file_path")
        # 中收的比例
        self._sales_income_percentage = config.get("retail.non_interest.financing.sales_income_percentage")
        self._header_row = config.get("retail.non_interest.financing.sheet_config.header_row")
        # 推荐人工号列索引
        self._id_column = config.get("retail.non_interest.financing.sheet_config.id_column")
        # 年化日均列索引
        self._annualized_daily_average_column = config.get(
            "retail.non_interest.financing.sheet_config.annualized_daily_average_column")
        # 时点余额列索引
        self._point_balance_column = config.get(
            "retail.non_interest.financing.sheet_config.point_balance_column")
        # 生成的Excel中中收的列名
        self._target_sales_income_column_name = config.get(
            "retail.non_interest.financing.sheet_config.target_sales_income_column_name")
        # 生成的Excel中时点余额的列名
        self._target_point_balance_column_name = config.get(
            "retail.non_interest.financing.sheet_config.target_point_balance_column_name")
        # 生成的Excel中年化日均的列名
        self._target_annualized_daily_column_name = config.get(
            "retail.non_interest.financing.sheet_config.target_annualized_daily_column_name")
        # 广州分行公共名称
        self._gz_common_account = config.get("branch.gz_common_account")

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        df = pd.read_csv(self._src_filepath, header=self._header_row)
        self._id_column_name = df.columns[self._id_column]
        self._name_column_name = "推荐人姓名"
        self._annualized_daily_average_column_name = df.columns[self._annualized_daily_average_column]
        self._point_balance_column_name = df.columns[self._point_balance_column]
        return df

    def _add_export_column_manifest_branch(self, origin_data: pd.DataFrame):
        if origin_data is None or origin_data.empty:
            return origin_data
        data = self._process_manager_name(data=origin_data)
        data = data.merge(
            ManifestUtils.get_name_branch_data_frame(),
            how="left",
            left_on=[self._name_column_name],
            right_on=[ManifestUtils.get_name_column_name()]
        )
        return data.drop(columns=[self._name_column_name])

    def _rename_target_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        df = data.rename(columns={
            self._annualized_daily_average_column_name: self._target_annualized_daily_column_name,
            self._point_balance_column_name: self._target_point_balance_column_name,
        })
        return df

    def _process_manager_name(self, *, data: pd.DataFrame) -> pd.DataFrame:
        manifest_df = ManifestUtils.get_manifest_df()
        # （非息）离职人员归属机构表
        employee_mapping = ManifestUtils.get_non_interest_leave_employee_branch_mapping()
        # 添加推荐人姓名一列
        data[self._name_column_name] = ""
        data[self._id_column_name].fillna(0, inplace=True)
        for row_i, row in data.iterrows():
            id_value = row[self._id_column_name]
            if id_value == 0:
                data.at[row_i, self._name_column_name] = self._gz_common_account
                continue
            try:
                id_value = int(id_value)
            except:
                # 不能转换为整形数字，工号不合法，算为广州分行公共
                data.at[row_i, self._id_column_name] = 0
                data.at[row_i, self._name_column_name] = self._gz_common_account
                continue
            # 花名册查找姓名
            name = manifest_df.loc[
                manifest_df[ManifestUtils.get_id_column_name()] == id_value,
                ManifestUtils.get_name_column_name()
            ]
            # 工号不为0，并且姓名不在花名册，则统计为广州分行公共
            if name.empty:
                data.at[row_i, self._id_column_name] = 0
                branch_name = self._gz_common_account
                # 如果是离职人员，则归属到配置的离职人员机构中去
                if str(id_value) in employee_mapping.keys():
                    branch_name = employee_mapping.get(str(id_value)).get("branch")
                data.at[row_i, self._name_column_name] = branch_name
            else:
                real_name = name.values[0]
                data.at[row_i, self._name_column_name] = real_name
        return data

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = self._process_manager_name(data=data)
        # 添加中收一列
        data[self._target_sales_income_column_name] = \
            data[self._target_annualized_daily_column_name] * self._sales_income_percentage
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("按{} {}透视数据项：{}, {}".format(
            self._id_column_name,
            self._name_column_name,
            self._target_annualized_daily_column_name,
            self._target_point_balance_column_name,
            self._target_sales_income_column_name,
        ))
        index_columns = [self._id_column_name, self._name_column_name]
        value_columns = [
            self._target_annualized_daily_column_name,
            self._target_point_balance_column_name,
            self._target_sales_income_column_name,
        ]
        if data.empty:
            return pd.DataFrame(columns=index_columns + value_columns)
        table = pd.pivot_table(
            data,
            values=value_columns,
            index=index_columns,
            aggfunc=np.sum, fill_value=0
        )
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data.reset_index(inplace=True)
        data[self._id_column_name] = data[self._id_column_name].astype("int64")
        return data

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与花名册合并...")
        merge_result = ManifestUtils.merge_with_manifest(
            manifest_data=manifest_data,
            data=data,
            id_column_name=self._id_column_name,
            name_column_name=self._name_column_name
        )
        return merge_result

    def _drop_duplicated_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=[self._id_column_name, self._name_column_name])

    def _add_target_columns(self) -> None:
        self._add_target_column(self._target_annualized_daily_column_name)
        self._add_target_column(self._target_point_balance_column_name)
        self._add_target_column(self._target_sales_income_column_name)
