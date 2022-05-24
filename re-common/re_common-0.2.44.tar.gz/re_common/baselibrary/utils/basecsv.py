import csv


class BaseCsv(object):

    def __init__(self):
        pass

    def read_csv(self, filepath):
        """
        根据文件路径逐行读取csv文件
        :param filepath:csv文件路径
        :return:csv每行记录
        """
        # mac_roman 原因
        # https://stackoverflow.com/questions/21504319/python-3-csv-file-giving-unicodedecodeerror-utf-8-codec-cant-decode-byte-err
        with open(filepath, "r",encoding='mac_roman') as f:
            reader = csv.reader(f)
            for row in reader:
                yield row

    def read_all_csv(self, filepath):
        """
        根据文件路径读取csv文件所有行
        :param filepath:csv文件路径
        :return:csv所有行记录
        """
        with open(filepath, "r") as f:
            reader = csv.reader(f)
            result = list(reader)
            return result

