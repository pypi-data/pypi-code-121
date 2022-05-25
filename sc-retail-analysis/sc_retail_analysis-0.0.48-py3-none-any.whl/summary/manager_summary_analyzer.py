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

import pandas as pd
from config42 import ConfigManager

from sc_retail_analysis.analyzer.base_analyzer import BaseAnalyzer


class ManagerSummaryAnalyzer(BaseAnalyzer):
    """
    按客户经理汇总分析
    """

    def __init__(self, *, config: ConfigManager, excel_writer: pd.ExcelWriter, target_column_list: list):
        super().__init__(config=config, excel_writer=excel_writer)
        self._target_column_list = list()
        self._target_column_list.extend(target_column_list)

    def _read_config(self, *, config: ConfigManager):
        # 经营、消费类汇总
        self._business_type_summary_dict = config.get("retail.branch_summary.business_type_summary")

    def analysis(self, *, manifest_data: pd.DataFrame, previous_data: pd.DataFrame) -> pd.DataFrame:
        # 读取业务类型
        self._business_type = "客户经理汇总"
        logging.getLogger(__name__).info("开始分析 {} 数据".format(self._business_type))
        old_columns = list(previous_data.columns.values)
        if len(self._target_column_list) > 0:
            # 添加个经小计、个消小计
            real_key_list = list()
            for sum_key, column_list in self._business_type_summary_dict.items():
                real_column_list = list()
                for column in column_list:
                    if column in self._target_column_list:
                        real_column_list.append(column)
                key = sum_key + "小计"
                real_key_list.append(key)
                if len(real_column_list) > 0:
                    previous_data[key] = previous_data[real_column_list].apply(lambda x: x.sum(), axis=1)
                else:
                    previous_data[key] = 0
                self._target_column_list.append(key)
            # 调整列的顺序，合计排两个小计的前面
            previous_data = previous_data[old_columns + real_key_list]
        logging.getLogger(__name__).info("完成分析 {} 数据".format(self._business_type))
        return previous_data

    def write_origin_data(self):
        # 汇总不输出明细数据，否则会将真正的汇总给覆盖掉
        pass
