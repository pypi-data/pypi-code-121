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
import os
import os.path
from datetime import datetime

import pandas as pd
from config42 import ConfigManager
from dateutil.relativedelta import relativedelta
from sc_analyzer_base import BranchUtils, ManifestUtils

from sc_retail_analysis.analyzer.base_analyzer import BaseAnalyzer


class HuNanClientAnalyzer(BaseAnalyzer):
    """
    湘籍客户分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter):
        super().__init__(config=config, excel_writer=excel_writer)
        self._key_enabled = "retail.hn_client.enabled"
        self._key_business_type = "retail.hn_client.business_type"

    def _get_analysis_date(self, date_format):
        """
        获取分析日期，以文件夹名称作为分析日期，如果文件夹日期不符合规范，则以昨日作为分析日期
        :return: 分析日期
        """
        # 当前路径
        path = os.getcwd()
        # 当前路径的文件夹名称
        basename = os.path.basename(path)
        try:
            analysis_date = datetime.strptime(basename, date_format)
            return analysis_date
        except ValueError:
            today = datetime.today()
            yesterday = today - relativedelta(days=1)
            # 报表分析日期，即昨天
            analysis_date = datetime(yesterday.year, yesterday.month, yesterday.day)
            return analysis_date

    def _read_config(self, *, config: ConfigManager):
        # 生成的Excel中湘籍客户数的列名
        self._target_hn_client_column_name = config.get("retail.hn_client.target_hn_client_column_name")
        # 生成的Excel中机构列的列名
        self._target_branch_column_name = config.get("retail.hn_client.target_branch_column_name")
        # 湘籍客户身份证前缀
        self._hn_client_id_prefix = config.get("retail.hn_client.hn_client_id_prefix")
        # 是不使用手工计算的数据
        self._is_using_manual_data = config.get("retail.hn_client.is_using_manual_data")
        # 日期格式
        self._date_format = config.get("retail.hn_client.date_format")

        # 此日期之前使用手工计算的结果
        manual_calculate_base_date_str = config.get("retail.hn_client.manual_calculate_base_date")
        self._manual_calculate_base_date = datetime.strptime(manual_calculate_base_date_str, self._date_format)
        # 此日期开始，使用报表分析的结果
        self._manual_calculate_start_date = self._manual_calculate_base_date + relativedelta(days=1)
        today = datetime.today()
        yesterday = today - relativedelta(days=1)
        # 报表分析日期，即昨天
        self._analysis_date = self._get_analysis_date(self._date_format)
        # 报表分析日期是否在手工计算日期之前
        # 如果使用手工数据，那么手工日期之前的数据以手工数据为准，之后的以报表数据分析为准
        self._is_analysis_date_before_manual_date = self._manual_calculate_base_date >= self._analysis_date

        # 湘籍客户-手工统计文件路径
        self._manual_src_filepath = config.get("retail.hn_client.manual.source_file_path")
        # 基数列名格式
        self._manual_base_month_format = config.get("retail.hn_client.manual.base_month_format")
        # Sheet名称
        self._manual_sheet_name = config.get("retail.hn_client.manual.sheet_name")
        # 表头行索引
        self._manual_header_row = config.get("retail.hn_client.manual.sheet_config.header_row")
        # 所属构列索引
        self._manual_branch_column = config.get("retail.hn_client.manual.sheet_config.branch_column")
        # 年初基数列索引
        self._manual_yearly_base_column = config.get("retail.hn_client.manual.sheet_config.yearly_base_column")

        # 湘籍客户文件路径
        self._personal_src_filepath = config.get("retail.hn_client.personal.source_file_path")
        # 表头行索引
        self._personal_header_row = config.get("retail.hn_client.personal.sheet_config.header_row")
        # 二级分支机构列索引
        self._personal_branch_column = config.get("retail.hn_client.personal.sheet_config.branch_column")
        # 客户姓名列索引
        self._personal_name_column = config.get("retail.hn_client.personal.sheet_config.name_column")
        # 客户身份证号码列索引
        self._personal_client_id_column = config.get("retail.hn_client.personal.sheet_config.client_id_column")
        # 开户日期列索引
        self._personal_account_open_date_column = config.get(
            "retail.hn_client.personal.sheet_config.account_open_date_column")

        # 湘籍企业客户清单文件路径
        self._corporate_src_filepath = config.get("retail.hn_client.corporate.source_file_path")
        # Sheet名称
        self._corporate_sheet_name = config.get("retail.hn_client.corporate.sheet_name")
        # 表头行索引
        self._corporate_header_row = config.get("retail.hn_client.corporate.sheet_config.header_row")
        # 户数列索引
        self._corporate_total_client_column = config.get("retail.hn_client.corporate.sheet_config.total_client_column")
        # 其中湘籍客户数列索引
        self._corporate_hn_client_column = config.get("retail.hn_client.corporate.sheet_config.hn_client_column")
        # 归属支行/团队列索引
        self._corporate_attribute_branch_column = config.get(
            "retail.hn_client.corporate.sheet_config.attribute_branch_column")
        # 上门网点列索引
        self._corporate_service_branch_column = config.get(
            "retail.hn_client.corporate.sheet_config.service_branch_column")
        # 是否湘籍客户列索引
        self._corporate_is_hn_client_column = config.get("retail.hn_client.corporate.sheet_config.is_hn_client_column")
        # 上门开户日期列索引
        self._corporate_account_open_date_column = config.get(
            "retail.hn_client.corporate.sheet_config.account_open_date_column")
        self._contains_data = False

    def _read_src_file(self) -> pd.DataFrame:
        if self._is_using_manual_data:
            logging.getLogger(__name__).info("读取湘籍手工文件：{}".format(self._manual_src_filepath))
            self._manual_data = pd.read_excel(
                self._manual_src_filepath,
                sheet_name=self._manual_sheet_name,
                header=self._manual_header_row
            )
            self._manual_branch_column_name = self._manual_data.columns[self._manual_branch_column]
            self._manual_yearly_base_column_name = self._manual_data.columns[self._manual_yearly_base_column]
            self._origin_manual_data = self._manual_data.copy()
            self._contains_data = True

        logging.getLogger(__name__).info("读取湘籍个人客户源文件：{}".format(self._personal_src_filepath))
        self._personal_data = pd.read_csv(
            self._personal_src_filepath,
            header=self._personal_header_row,
            dtype={'开户日期': "str"},
        )
        self._origin_personal_data = self._personal_data.copy()
        self._contains_data = True

        self._personal_branch_column_name = self._personal_data.columns[self._personal_branch_column]
        self._personal_name_column_name = self._personal_data.columns[self._personal_name_column]
        self._personal_client_id_column_name = self._personal_data.columns[self._personal_client_id_column]
        self._personal_account_open_date_column_name = self._personal_data.columns[
            self._personal_account_open_date_column]
        self._personal_data[self._personal_account_open_date_column_name] = pd.to_datetime(
            self._personal_data[self._personal_account_open_date_column_name]
        )
        # 过滤身份证为湖南的客户
        criterion = self._origin_personal_data[self._personal_client_id_column_name].map(
            lambda x: x.startswith(self._hn_client_id_prefix))
        self._origin_personal_data = self._origin_personal_data[criterion].copy()

        logging.getLogger(__name__).info("读取湘籍企业客户源文件：{}".format(self._corporate_src_filepath))
        self._corporate_data = pd.read_excel(
            self._corporate_src_filepath,
            sheet_name=self._corporate_sheet_name,
            header=self._corporate_header_row,
            dtype={'上门开户日期': "str"},
        )
        self._origin_corporate_data = self._corporate_data.copy()
        self._corporate_total_client_column_name = self._corporate_data.columns[self._corporate_total_client_column]
        self._corporate_hn_client_column_name = self._corporate_data.columns[self._corporate_hn_client_column]
        self._corporate_attribute_branch_column_name = self._corporate_data.columns[
            self._corporate_attribute_branch_column]
        self._corporate_service_branch_column_name = self._corporate_data.columns[self._corporate_service_branch_column]
        self._corporate_is_hn_client_column_name = self._corporate_data.columns[self._corporate_is_hn_client_column]
        self._corporate_account_open_date_column_name = self._corporate_data.columns[
            self._corporate_account_open_date_column]
        self._corporate_data[self._corporate_account_open_date_column_name] = pd.to_datetime(
            self._corporate_data[self._corporate_account_open_date_column_name]
        )
        self._contains_data = True
        return self._personal_data

    def _is_branch_valid(self, branch):
        mapping = BranchUtils.get_branch_name_mapping()
        return branch in mapping.values()

    def _get_manual_column_name(self, analysis_date: datetime) -> str:
        """
        通过分析日期获取基数列名
        :param analysis_date:
        :return:
        """
        columns_set = set()
        for column in self._manual_data.columns.values:
            try:
                # 只添加符合规则的列
                datetime.strptime(column, self._manual_base_month_format)
                columns_set.add(column)
            except:
                pass
        columns_list = sorted(columns_set, reverse=True)
        size = len(columns_list)

        for column in columns_list:
            date_month = analysis_date.strftime(self._manual_base_month_format)
            if date_month >= column:
                # 如果分析月分大于此列，则以此列为基数
                return column
        # 找不到返回最后一列作为基数
        return columns_list[size - 1]

    def _calculate_manual_base_data(self):
        """
        计算手工基础数据
        :return:
        """
        mapping = BranchUtils.get_branch_name_mapping()
        # 替换机构名称
        self._manual_data = self._manual_data.replace({self._manual_branch_column_name: mapping})

        # 过滤不存在的机构行（即总计行）
        criterion = self._manual_data[self._manual_branch_column_name].map(lambda x: self._is_branch_valid(x))
        self._manual_data = self._manual_data[criterion].copy()

        manual_column_name = self._get_manual_column_name(self._analysis_date)
        logging.getLogger(__name__).info(f"选择 {manual_column_name} 作为基数")
        # 如果找到相应的月份列，则以此列作为基数列
        self._manual_data.rename(columns={
            manual_column_name: self._target_hn_client_column_name,
        }, inplace=True)
        # 只筛选相关列：机构、相应的月份
        self._manual_data = self._manual_data[[
            self._manual_branch_column_name,
            self._target_hn_client_column_name,
        ]].copy()
        for branch_name in BranchUtils.get_all_business_branch_list():
            if branch_name not in self._manual_data[self._target_branch_column_name].values.tolist():
                self._manual_data = pd.concat(
                    [self._manual_data, pd.DataFrame(
                        {
                            self._manual_branch_column_name: branch_name,
                            self._target_hn_client_column_name: 0,
                        },
                        index=[1])  # 必须添加此index参数，否则会报错
                     ],
                    ignore_index=True,  # 忽略上一步添加的index，使用系统生成的index
                )

    def _date_within_analysis_range(self, data_date):
        return self._manual_calculate_start_date <= data_date <= self._analysis_date

    def _pre_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 处理手工基数
        if self._is_using_manual_data:
            self._calculate_manual_base_data()
        # 过滤身份证为湖南的客户
        criterion = data[self._personal_client_id_column_name].map(lambda x: x.startswith(self._hn_client_id_prefix))
        data = data[criterion].copy()

        if self._is_using_manual_data:
            # 筛选指定日期范围的数据
            if self._is_analysis_date_before_manual_date:
                # 如果分析日期在手动计算日期之前，则使用手动计算的基数，清空报表分析数据
                data = data.iloc[0:0]
            # else:
            #     # 筛选手动日期到分析日期之间的数据
            #     criterion = data[self._personal_account_open_date_column_name].map(
            #         lambda x: self._date_within_analysis_range(x)
            #     )
            #     data = data[criterion].copy()

        mapping = BranchUtils.get_branch_name_mapping()
        # 替换机构名称
        data = data.replace({self._personal_branch_column_name: mapping})

        if self._is_using_manual_data:
            # 筛选指定日期范围的数据
            if self._is_analysis_date_before_manual_date:
                # 如果分析日期在手动计算日期之前，则使用手动计算的基数，清空报表分析数据
                self._corporate_data = self._corporate_data.iloc[0:0]
            # else:
            #     # 筛选手动日期到分析日期之间的数据
            #     criterion = self._corporate_data[self._corporate_account_open_date_column_name].map(
            #         lambda x: self._date_within_analysis_range(x)
            #     )
            #     self._corporate_data = self._corporate_data[criterion].copy()
        # 替换机构名称
        self._corporate_data = self._corporate_data.replace({self._corporate_attribute_branch_column_name: mapping})
        # 替换机构名称
        self._corporate_data = self._corporate_data.replace({self._corporate_service_branch_column_name: mapping})
        return data

    def _add_up_with_manual_base_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        加上手工基数
        :param data:
        :return:
        """
        if data.empty:
            self._manual_data.set_index(self._manual_branch_column_name, inplace=True)
            return self._manual_data
        data.set_index(self._manual_branch_column_name, inplace=True)
        self._manual_data.set_index(self._manual_branch_column_name, inplace=True)
        data = self._manual_data + data
        data.reset_index(inplace=True)
        data.fillna(0)
        return data

    def _pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("按 {} 透视数据项：{}".format(
            self._personal_branch_column_name,
            self._personal_name_column_name,
        ))
        # 重命名列名
        data = data.rename(columns={
            self._personal_branch_column_name: self._target_branch_column_name,
            self._personal_name_column_name: self._target_hn_client_column_name,
        })
        # 对湘籍个人客户数进行统计
        table = pd.pivot_table(
            data,
            values=[self._target_hn_client_column_name],
            index=[self._target_branch_column_name],
            aggfunc='count', fill_value=0
        )
        table = table.reset_index()
        for branch_name in BranchUtils.get_all_business_branch_list():
            if branch_name not in table[self._target_branch_column_name].values.tolist():
                table = pd.concat(
                    [table, pd.DataFrame(
                        {
                            self._target_branch_column_name: branch_name,
                            self._target_hn_client_column_name: 0,
                        },
                        index=[1])  # 必须添加此index参数，否则会报错
                     ],
                    ignore_index=True,  # 忽略上一步添加的index，使用系统生成的index
                )
        if self._is_using_manual_data:
            if self._is_analysis_date_before_manual_date:
                # 如果分析日期在手动计算日期之前，则使用手动计算的基数
                table = self._add_up_with_manual_base_data(table)
        return table

    def _after_pivot_table(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # 筛选是湘籍企业的数据
        criterion = self._corporate_data[self._corporate_is_hn_client_column_name].map(lambda x: x == "是")
        hn_corporate_data = self._corporate_data[criterion].copy()
        # 解决手工文件中客户数量两个字段为空时统计错误的问题
        hn_corporate_data[self._corporate_total_client_column_name].fillna(0, inplace=True)
        hn_corporate_data[self._corporate_hn_client_column_name].fillna(0, inplace=True)

        # 加入湘籍企业客户的数量
        for row_i, row in hn_corporate_data.iterrows():
            total_client = row[self._corporate_total_client_column_name]
            hn_client = row[self._corporate_hn_client_column_name]
            attribute_branch = row[self._corporate_attribute_branch_column_name]
            service_branch = row[self._corporate_service_branch_column_name]
            if attribute_branch == service_branch:
                # 如果归属机构与上门机构相同，则全部归属到上门机构
                count = data.loc[
                    data[self._target_branch_column_name] == attribute_branch,
                    self._target_hn_client_column_name
                ]
                count = count + total_client - hn_client
                data.loc[
                    data[self._target_branch_column_name] == attribute_branch,
                    self._target_hn_client_column_name
                ] = count
            else:
                # 如果归属机构与上门机构相同，则全部归属到上门机构
                count_attribute = data.loc[
                    data[self._target_branch_column_name] == attribute_branch,
                    self._target_hn_client_column_name
                ]
                count_attribute = count_attribute + total_client
                data.loc[
                    data[self._target_branch_column_name] == attribute_branch,
                    self._target_hn_client_column_name
                ] = count_attribute
                count_service = data.loc[
                    data[self._target_branch_column_name] == service_branch,
                    self._target_hn_client_column_name
                ]
                count_service = count_service - hn_client
                data.loc[
                    data[self._target_branch_column_name] == service_branch,
                    self._target_hn_client_column_name
                ] = count_service
        return data

    def _merge_with_manifest(self, *, manifest_data: pd.DataFrame, data: pd.DataFrame) -> pd.DataFrame:
        logging.getLogger(__name__).info("与机构清单合并...")
        merge_result = manifest_data.merge(
            data,
            how="left",
            left_on=[ManifestUtils.get_branch_column_name()],
            right_on=[self._target_branch_column_name],
        )
        return merge_result

    def write_origin_data(self):
        # 如果未启用，则直接返回
        if not self._enabled():
            return
        if not self._contains_data:
            return
        if self._is_using_manual_data:
            self._origin_manual_data.to_excel(
                excel_writer=self._excel_writer,
                index=False,
                sheet_name="湘籍客户-手工统计-原始数据",
            )

        self._origin_personal_data.to_excel(
            excel_writer=self._excel_writer,
            index=False,
            sheet_name="湘籍客户交叉销售明细表-原始数据",
        )
        self._origin_corporate_data.to_excel(
            excel_writer=self._excel_writer,
            index=False,
            sheet_name="上门开户统计清单汇总-原始数据",
        )

    def _merge_with_previous_result(self, data: pd.DataFrame, previous_data: pd.DataFrame) -> pd.DataFrame:
        if previous_data is None or previous_data.empty:
            return data
        result = previous_data.copy()
        # 在原有基础上增加湘籍客户一列
        result[self._target_hn_client_column_name] = data[self._target_hn_client_column_name]
        return result
