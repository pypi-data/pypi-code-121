from avro.datafile import DataFileReader
from avro.io import DatumReader

from re_common.baselibrary.utils.basedir import BaseDir


class BaseAvro(object):

    def read_line_yeild(self, dir):
        """
        逐行读取某个目录里avro文件
        :param dir:avro目录
        :return:单个avro单行记录
        """
        for file in BaseDir.get_dir_all_files(dir):
            reader = DataFileReader(open(file, "rb"), DatumReader())
            for line in reader:
                yield line

