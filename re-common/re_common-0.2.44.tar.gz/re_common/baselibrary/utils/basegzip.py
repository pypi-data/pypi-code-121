import gzip

from re_common.baselibrary.utils.basefile import BaseFile


class BaseGzip(object):

    def __init__(self, bufsize, fin=None, fout=None):
        self.bufsize = bufsize
        self.fin = fin
        self.fout = fout

    def compress(self, src, dst):
        """
        压缩文件
        :param src:
        :param dst:
        :return:
        """
        self.fin = open(src, 'rb')
        self.fout = gzip.open(dst, 'wb')

        self.__in2out()

    def decompress(self, gzFile, dst):
        """
        解压文件
        :param gzFile:
        :param dst:
        :return:
        """
        self.fin = gzip.open(gzFile, 'rb')
        self.fout = open(dst, 'wb')

        self.__in2out()

    def __in2out(self):
        while True:
            buf = self.fin.read(self.bufsize)
            if len(buf) < 1:
                break
            self.fout.write(buf)

        self.fin.close()
        self.fout.close()

    def read_gz_file(self, file):
        with gzip.open(file, 'r') as f:
            for lineb in f:
                line = lineb.decode()
                yield line.strip()

    @classmethod
    def get_gz_line_num(self, file):
        i = 0
        if BaseFile.is_file_exists(file):
            with gzip.open(file, 'rb') as f:
                for i, l in enumerate(f):
                    pass
        return i
