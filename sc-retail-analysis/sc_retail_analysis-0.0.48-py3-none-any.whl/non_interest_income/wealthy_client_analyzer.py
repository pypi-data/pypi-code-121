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
from sc_analyzer_base import BranchUtils, ManifestUtils

from sc_retail_analysis.analyzer.base_analyzer import BaseAnalyzer


class WealthyClientAnalyzer(BaseAnalyzer):
    """
    财富客户分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "retail.non_interest.wealthy_client.enabled"
        self._key_business_type = "retail.non_interest.wealthy_client.business_type"
        self._key_export_column_list = "retail.non_interest.wealthy_client.sheet_config.export_column_list"

    def _read_config(self, *, config: ConfigManager):
        # 财富客户数统计文件路径
        self._src_filepath = config.get("retail.non_interest.wealthy_client.source_file_path")
        # 管户机构对应配置
        self._manage_branch_mapping = dict()
        manage_branch_mapping = config.get("retail.non_interest.wealthy_client.manage_branch_mapping")
        if type(manage_branch_mapping) == dict:
            self._manage_branch_mapping.update(manage_branch_mapping)
        # Sheet名称
        self._sheet_name = config.get("retail.non_interest.wealthy_client.sheet_name")
        # 表头行索引
        self._header_row = config.get("retail.non_interest.wealthy_client.sheet_config.header_row")
        # 管户机构列索引
        self._manage_branch_column = config.get("retail.non_interest.wealthy_client.sheet_config.manage_branch_column")
        # 管户经理列索引
        self._manager_column = config.get("retail.non_interest.wealthy_client.sheet_config.manager_column")
        # ECIF客户号列索引
        self._ecif_id_column = config.get("retail.non_interest.wealthy_client.sheet_config.ecif_id_column")
        # 生成的Excel中财富客户数的列名
        self._target_client_count_column_name = config.get(
            "retail.non_interest.wealthy_client.sheet_config.target_client_count_column_name")
        # 业绩归属机构列名
        self._sales_performance_attribution_column_name = config.get("branch.sales_performance_attribution_column_name")

    def _read_src_file(self) -> pd.DataFrame:
        logging.getLogger(__name__).info("读取源文件：{}".format(self._src_filepath))
        df = pd.read_excel(self._src_filepath, sheet_name=self._sheet_name, header=self._header_row)
        self._manage_branch_column_name = df.columns[self._manage_branch_column]
        self._manager_column_name = df.columns[self._manager_column]
        self._ecif_id_column_name = df.columns[self._ecif_id_column]
        return df

    def _add_export_column_manifest_branch(self, origin_data: pd.DataFrame):
        if origin_data is None or origin_data.empty:
            return origin_data
        # 与花名册整合，添加花名册所在部门一列
        data = self._pre_pivot_table(data=origin_data)
        data.rename(columns={
            self._sales_performance_attribution_column_name: ManifestUtils.get_manifest_branch_column_name(),
        }, inplace=True)
        return data.drop(columns=[
            ManifestUtils.get_id_column_name(),
            ManifestUtils.get_name_column_name(),
            ManifestUtils.get_branch_column_name(),
        ])

    def _rename_target_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        df = data.rename(columns={
            self._ecif_id_column_name: self._target_client_count_column_name,
        })
        return df

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 替换管户机构名称
        mapping = BranchUtils.get_branch_name_mapping()
        # 处理管户机构名称
        data = data.replace({self._manage_branch_column_name: mapping})
        # 与花名册合并，获取所属机构，然后再处理成业绩归属机构
        manifest_df = ManifestUtils.get_manifest_df().copy()
        # 先删除业绩归属列
        manifest_df.drop(columns=[self._sales_performance_attribution_column_name], inplace=True)
        merged_data = data.merge(
            manifest_df,
            how="left",
            left_on=[self._manager_column_name],
            right_on=[ManifestUtils.get_name_column_name()],
        )
        # 业绩归属机构配置
        attribution_mapping = self._manage_branch_mapping
        # 添加业绩归属列
        merged_data[self._sales_performance_attribution_column_name] = data[self._manage_branch_column_name]
        for row_i, row in merged_data.iterrows():
            # 管户机构
            manage_branch = row[self._manage_branch_column_name]
            # 如果管户机构不是分行营业部，则保持原样，不处理
            if manage_branch not in attribution_mapping.values():
                continue
            # 如果管户机构是分行营业部
            # 客户经理所属机构
            branch = row[ManifestUtils.get_branch_column_name()]
            # 客户经理所在机构为空，归管护机构所有
            if branch is np.nan:
                continue
            # 如果客户经理机构不在归属到分营的机构，则归属到客户经理所在机构中去
            if branch in attribution_mapping.keys():
                merged_data.at[row_i, self._sales_performance_attribution_column_name] = branch

        return merged_data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("按 {} 透视数据项：{}".format(
            self._sales_performance_attribution_column_name,
            self._target_client_count_column_name,
        ))
        index_columns = [self._sales_performance_attribution_column_name]
        value_columns = [self._target_client_count_column_name]
        if data.empty:
            return pd.DataFrame(columns=index_columns + value_columns)
        table = pd.pivot_table(
            data,
            values=value_columns,
            index=index_columns,
            aggfunc='count', fill_value=0
        )
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = data.reset_index()
        return data

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与机构清单合并...")
        merge_result = manifest_data.merge(
            data,
            how="left",
            left_on=[ManifestUtils.get_branch_column_name()],
            right_on=[self._sales_performance_attribution_column_name],
        )
        return merge_result

    def _drop_duplicated_columns(self, *, data: pd.DataFrame) -> pd.DataFrame:
        return data.drop(columns=[self._sales_performance_attribution_column_name])

    def _merge_with_previous_result(self, data: pd.DataFrame, previous_data: pd.DataFrame) -> pd.DataFrame:
        if previous_data is None or previous_data.empty:
            return data
        result = previous_data.copy()
        # 在原有基础上增加财富客户一列
        result[self._target_client_count_column_name] = data[self._target_client_count_column_name]
        return result
