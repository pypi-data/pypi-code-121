# -*- coding: utf-8 -*-
import os

import chardet
from parse import parse

from docparser.core.document_parser_base import DocumentParserBase
import logging
log = logging.getLogger(__name__)

class TextDocumentParser(DocumentParserBase):
    """
    文本文件解析器
    """

    def __init__(self, file, configs):
        """
        初始化
        :param file:文件路径
        :param configs: 配置
        """
        self._file = file
        self._configs = configs

        if not os.path.exists(file):
            raise FileNotFoundError

        fi_encoding = self.get_encoding(file)
        with open(file, 'r', encoding=fi_encoding, errors='ignore') as f:
            self._data = f.readlines()

    def get_encoding(slef, file):
        """
        推断文件编码
        : return： 编码名称
        """
        f3 = open(file=file, mode='rb')  # 以二进制模式读取文件
        file_data = f3.read()  # 获取文件内容
        # print(file_data)
        f3.close()  # 关闭文件
        result = chardet.detect(file_data)
        encode = result['encoding']
        # gb2312的编码需要转成gbk或者gb18030处理
        if str(encode).upper() == 'GB2312':
            return 'gbk'
        return encode

    def parse(self):
        """
        根据配置抽取数据
        :return: 返回抽取的数据
        """

        data_bucket = {}
        results = []
        errors = {}
        for key in self._configs.keys():
            item_config = self._configs[key]
            self.fixed(item_config)
            for m in self._data:
                for m_parse in item_config['parse']:
                    try:
                        result = parse(m_parse.rstrip(), m)

                        if result is not None:
                            results.append(result)
                            log.debug(f'解析字符串{m} 结果：{result.named.items()}')
                            for kv, val in result.named.items():
                                data_bucket[kv] = str(val).strip()
                        else:
                            log.debug(f'解析字符串{m} 结果为None')
                    except Exception as ex:
                        errors['parse_error'].append(ex.args)
                    # print(m, m_parse, result)
        print(data_bucket)

        return [data_bucket], [errors]

    def fixed(self, item_config):
        """
        修正字符串中异常的字符
        """
        if item_config is None:
            return None
        fixed_dic = item_config.get('fixed', None)
        if fixed_dic is None:
            return None
        fixed_data = []
        for m in self._data:
            for k, v in fixed_dic.items():
                m = m.replace(k, v)
            fixed_data.append(m)
        self._data = fixed_data
        return self._data

if __name__ == '__main__':
    converter = TextDocumentParser(
        r"C:\Users\RobinJiang\Desktop\shz4950443-dec86f1d5d2304cee0530a008761e004.txt",
        {
            'standard': {
                'parse':
                    [r'Shipping Order No.:{so}Booking Date:Electronic Ref.: {bookDate} {electronicRef}',
                     r'Shipper / Forwarder:  {shipper}',
                     r'PIC: {pic}',
                     r'Deciding Party:  {deciding_party} SCAC Code :  {scac_code}',
                     r'B/L Number :  {billno}',
                     r'Vessel/Voyage:  {vessel_voyage}',
                     r'Place of Receipt: {place_of_receipt} Alternate Base Pool:{alternate_base_pool} Ramp Cut-Off Date/Time:{ramp_cutoff_datetime}',
                     r'Feeder Vessel/Voyage:{feeder_vessel_voyage} ETD: {first_etd}',
                     r'Port of Loading: {port_of_loading}  ETD: {second_etd}',
                     r'Loading Terminal:  {loading_terminal}  Cargo Receiving Date: {cargo_receiving_date}',
                     r'VGM Cut-Off Date/Time: {vgm_cutoff_datetime}',
                     r'Discharge Instruction:{discharge_instruction} Transhipment Port:{transhipment_port}  Port Cut-off Date/Time:{port_cutoff_datetime} SI Cut-off Date/Time: {si_cutoff_datetime} ',
                     r'Port of Discharge:  {port_of_discharge}  Booking Pty. Ref.: {booking_pty_ref}',
                     r'Place of Delivery: {place_of_delivery}',
                     r'ENS Clause: {ens_clause} ETA: {eta} SI Fax No.: {si_fax_no} SI Email: {si_email} Vessel Flag: {vessel} IMO: {imo} Country of Documentation: {doc} Operator: {operator}',
                     r'{container_type}GP WITHOUT VENTILATION HC X{container_num:d} {weight:f}']
            }
        })
    data = converter.parse()
    print(data)
