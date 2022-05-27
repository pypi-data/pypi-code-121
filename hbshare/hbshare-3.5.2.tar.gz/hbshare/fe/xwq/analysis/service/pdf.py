# -*- coding: utf-8 -*-

# from io import StringIO
# from pdfminer.pdfinterp import PDFResourceManager
# from pdfminer.pdfinterp import process_pdf
# from pdfminer.converter import TextConverter
# from pdfminer.layout import LAParams
# import re

import pdfplumber

def read_from_pdfminer3k(file_path):
    """
    读取pdf文件
    """
    with open(file_path, 'rb') as file:
        resource_manager = PDFResourceManager()
        return_str = StringIO()
        lap_params = LAParams()
        device = TextConverter(resource_manager,return_str,laparams=lap_params)
        process_pdf(resource_manager,device,file)
        device.close()
        content = return_str.getvalue()
        return_str.close()
        return re.sub('\s+','',content)

def read_from_pdfplumber(file_path):
    """
    读取pdf文件
    """
    with pdfplumber.open(file_path) as file:
        total_pages = len(file.pages)
        content = ''
        for i in range(total_pages):
            content += file.pages[i].extract_text()
        return content

if __name__ == '__main__':
    file_name = '上海衍复投资管理有限公司_自定义报告_衍复臻选中证1000指数增强一号私募证券投资基金（20220201-20220228）.pdf'
    data_path = 'D:/Git/hbshare/hbshare/fe/xwq/data/pdf/'
    # file = read_from_pdf_pdfminer3k('{0}{1}'.format(data_path, file_name))
    file = read_from_pdfplumber('{0}{1}'.format(data_path, file_name))
    pass
