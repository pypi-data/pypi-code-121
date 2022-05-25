import collections
import re

import pandas as pd
import os
import sys,click
from xmindparser import xmind_to_dict

@click.command()
@click.option('-x', '--xmindpath', 'xmindpath', required=True, help='xmind file path')
@click.option('-e', '--excelpath', 'excelpath', required=True, help='excel file path')
@click.option('-i', '--ignorelayer', 'ignorelayer', required=False, default='0')
def convert(xmindpath, excelpath, ignorelayer):
    if ignorelayer == '0':
        ConvertXmindToExcel().convert(xmindpath, excelpath)
    else:
        ConvertXmindToExcel().convert(xmindpath, excelpath, ignorelayer)
    sys.exit()

class ConvertXmindToExcel:
    def __init__(self):
        self.markdown_dict = collections.defaultdict(list)
        self.index = 0
        self.ignore_layer_number = 0
        self.line_number = 0
        self.case_title = '用例标题'

    def convert(self, xmind_path, excel_path, ignore_layer_number='0'):
        if os.path.isfile(xmind_path):
            # 如果传递单个xmind文件，则直接转换
            self.convert_single_file(xmind_path, excel_path, ignore_layer_number)
        # 如果传递xmind文件夹的路径，则遍历文件夹中的xmind文件进行转换，放到指定的目录下面 或者 汇合到同一个Excel文件中
        elif os.path.isdir(xmind_path):
            # 如果Excel_path是指定的文件，则进行汇总
            if excel_path.endswith('.xlsx'):
                self.convert_multiple_file(xmind_path, excel_path, ignore_layer_number)
                return
            # 否则放到指定的目录下面
            if not os.path.exists(excel_path):
                os.makedirs(excel_path)
            xmind_dir = os.walk(xmind_path)
            for path, dir_list, file_list in xmind_dir:
                for file_name in file_list:
                    if not file_name.endswith('.xmind'):
                        continue
                    self.convert_single_file(os.path.join(path, file_name),
                                             os.path.join(excel_path, file_name.replace('.xmind', '.xlsx')),
                                             ignore_layer_number)

    def order_dict(self):
        result_dict = {}
        column_list = ['特性层级', '用例标题', '用例描述', '前置条件', '测试步骤', '预期结果', '国家标签',
                       'jira编号', '用例等级', '适用阶段', '用例类型', '用例负责人', '用例关键字', '备注', '标签']
        for column in column_list:
            result_dict[column] = self.markdown_dict[column]
            while len(result_dict[column]) < self.line_number:
                result_dict[column].append('')
        for key in self.markdown_dict:
            if key not in column_list:
                result_dict[key] = self.markdown_dict[key]
        return result_dict

    def convert_multiple_file(self, xmind_path, excel_file_path, ignore_layer_number):
        # 将多个xmind转换为单个excel文件
        xmind_dir = os.walk(xmind_path)
        for path, dir_list, file_list in xmind_dir:
            for file_name in file_list:
                if not file_name.endswith('.xmind'):
                    continue
                self.ignore_layer_number = int(ignore_layer_number)
                self.parseXmindToDict(os.path.join(path, file_name))
                self.index = 0
            df = pd.DataFrame(self.order_dict())
            writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='case_data', index=False)
            worksheet = writer.sheets['case_data']
            wrap_format = writer.book.add_format({'text_wrap': True})
            worksheet.set_column(df.columns.get_loc('特性层级'), df.columns.get_loc('特性层级'), 50)
            worksheet.set_column(df.columns.get_loc('用例标题'), df.columns.get_loc('用例标题'), 50)
            worksheet.set_column(df.columns.get_loc('用例标题'), df.columns.get_loc('用例标题'), 70, wrap_format)
            worksheet.set_column(df.columns.get_loc('测试步骤'), df.columns.get_loc('测试步骤'), 70, wrap_format)
            worksheet.set_column(df.columns.get_loc('预期结果'), df.columns.get_loc('预期结果'), 70, wrap_format)
            writer.save()

    # 将单个xmind转换为单个excel文件
    def convert_single_file(self, xmind_path, excel_path, ignore_layer_number):
        try:
            self.ignore_layer_number = int(ignore_layer_number)
            self.markdown_dict = collections.defaultdict(list)
            self.parseXmindToDict(xmind_path)
            df = pd.DataFrame(self.order_dict())
            writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='case_data', index=False)
            worksheet = writer.sheets['case_data']
            wrap_format = writer.book.add_format({'text_wrap': True})
            worksheet.set_column(df.columns.get_loc('特性层级'), df.columns.get_loc('特性层级'), 50)
            worksheet.set_column(df.columns.get_loc('用例标题'), df.columns.get_loc('用例标题'), 50)
            worksheet.set_column(df.columns.get_loc('用例标题'), df.columns.get_loc('用例标题'), 70, wrap_format)
            worksheet.set_column(df.columns.get_loc('测试步骤'), df.columns.get_loc('测试步骤'), 70, wrap_format)
            worksheet.set_column(df.columns.get_loc('预期结果'), df.columns.get_loc('预期结果'), 70, wrap_format)
            writer.save()
        finally:
            self.index = 0
            self.ignore_layer_number = 0
            self.line_number = 0
            self.case_title = '用例标题'

    def parseXmindToDict(self, xmind_file_path):
        content_dict = xmind_to_dict(xmind_file_path)
        object = content_dict[0]['topic']
        content_array = []
        for i in range(100):
            content_array.append(i)
        self.analyze(content_array, object)

    def analyze(self, content_array, topic_object):
        topic_labels = topic_object.setdefault('labels', None)
        if topic_labels and 'remove' in topic_labels:
            return
        content_array[self.index] = topic_object['title']
        if 'topics' not in topic_object.keys() or len(topic_object['topics']) == 0:
            # 碰到叶子节点，解析一行内容，行数加一
            self.line_number += 1
            self.generate(content_array)
            return
        self.index = self.index + 1
        for topic in topic_object['topics']:
            self.analyze(content_array, topic)
        self.index = self.index - 1

    def generate(self, content_array):
        title = ''
        for i in range(self.index + 1):
            content = content_array[i]
            content = content.replace('\b', '')
            if content is None:
                print(f'存在空节点，请检查{content_array}中是否存在空')
                raise Exception('存在空节点')
            is_prop, column_name, column_value = self.check_in_column(content)
            if is_prop:
                # 如果content以 "列名："的样式开开头，则进入对应的列名解析
                if len(self.markdown_dict[column_name]) >= self.line_number:
                    print(f'出现重复属性，contentArray:{content_array}')
                    continue
                # 在添加属性之前，必须确保之前的列全部被填满
                while len(self.markdown_dict[column_name]) < self.line_number-1:
                    self.markdown_dict[column_name].append('')
                self.markdown_dict[column_name].append(column_value.strip())
            else:
                # 否则则将其作为标题层级进行解析
                if i < self.ignore_layer_number:
                    continue
                title += '_' + content.strip()
        self.markdown_dict[self.case_title].append(title[1:].replace('\n', ''))
        # 将剩余没有被赋值的列，赋值为空字符串
        for key in self.markdown_dict:
            while len(self.markdown_dict[key]) < self.line_number:
                self.markdown_dict[key].append('')

    def check_in_column(self, content):
        regex = '\s*(\w+)[:|：]([\s\S]*)'
        content = content.lstrip()
        match_obj = re.match(regex, content)
        if not match_obj:
            return False, None, None
        return True, match_obj[1], match_obj[2]


