"""
多文件合并到压缩文件
方法一：按行读取写入
方法二: 按块读取写入

"""

###########################################
# 同项目调用基础包
import os
import sys

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-4]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)

############################################

import time
import gzip

from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile


class MergeGzFile(object):
    def __init__(self):
        self.outPathFile = None
        self.a_num = 1000
        self.b_num = 20000

        self.a_size = 1024 * 1024 * 1024
        self.block_size = 2 * 1024 * 1024 * 1024


    def get_outpathfile(self,dst):
        BaseDir.create_dir(dst)
        now_time = time.strftime('%Y%m%d', time.localtime())
        self.filename = "{}.gz".format(now_time)
        self.outPathFile = BaseFile.get_new_path(dst,self.filename)
        return self.outPathFile


    def line_all_2_one_gz(self,src,dst,dst_size=None,a_num=None,b_num=None):
        """
        :param src: 输入路径
        :param dst: 输出路径
        :param dst_size:  指定输出文件的最大值
        :param a_num:  打印条数的取值（默认1000条输出一次信息）
        :param b_num:  打印路径的取值（默认20000条输出一次信息）
        :return:
        """
        # 程序开始时间
        StartTime = time.time()
        if a_num is None:
            a_num = self.a_num
        if b_num is None:
            b_num = self.b_num
        count_all = 0
        dst_count = 0
        src_file_num = 0
        src_file_location = 0
        if self.outPathFile is None:
            self.get_outpathfile(dst)

        f = gzip.open(self.outPathFile, "wb")

        for files in BaseDir.get_dir_all_files(src):
            src_file_num += 1

        for files in BaseDir.get_dir_all_files(src):
            # 处理每个文件的开始时间
            start_time = time.time()
            src_file_location += 1
            print("next source_path:"+files)

            count = 0
            for line in BaseFile.read_file_rb_mode_yield(files):
                count += 1
                count_all +=1
                dst_count +=1

                f.write(line)

                if count % a_num == 1:
                    print("process_src:%d/%d, Time total:%s, source_count: %d, dst_count: %d, allcount: %d" % (src_file_location, src_file_num, (repr(time.time() - start_time)), count, dst_count, count_all))
                if count % b_num == 1:
                    print("source_path: %s , dst_path:%s" % (files,self.outPathFile))
                if dst_size is not None:
                    if BaseFile.get_file_size(self.outPathFile) >= dst_size:
                        f.close()
                        print("cut dst file, now:source_count: %d,dst_count: %d, allcount: %d" % (count, dst_count, count_all))
                        dst_count = 0
                        self.outPathFile = BaseFile.change_file(self.outPathFile, size=dst_size,ending='gz')
                        # self.outPathFile = self.outPathFile.replace(".big_json",'.gz')
                        f = gzip.open(self.outPathFile, "wb")
                        print("new dst_path: %s" % self.outPathFile)

            print("finish one file;Time total:%s, process_src:%d/%d, source_count: %d, dst_count: %d, allcount: %d" % (repr(time.time() - start_time),src_file_location, src_file_num,count, dst_count, count_all))
        # 程序结束花费时间时间
        print('\nProce Over\nTime total:' + repr(time.time() - StartTime) + '\n')

    def block_all_2_one_gz(self,src,dst,dst_size=None,block_size=None,a_size=None):
        """
        按块读取小文件，并写入文件
        :param src: 输入路径
        :param dst: 输出路径
        :param source_size: 输入文件大于source_size，就直接复制过去
        :param dst_size: 指定输出文件的最大值（但是需要操作完一个输入文件后判断大小）
        :param block_size: 按块读取的值
        :param a_size: 打印路径的取值（默认1G大小输出一次信息）
        :return:
        """
        # 程序开始时间
        StartTime = time.time()
        src_file_num = 0
        src_all_size = 0
        src_file_location = 0
        if a_size is None:
            a_size = self.a_size
        if block_size is None:
            block_size = self.block_size

        if self.outPathFile is None:
            self.get_outpathfile(dst)

        f = gzip.open(self.outPathFile, "wb")

        for files in BaseDir.get_dir_all_files(src):
            src_file_num += 1
        for files in BaseDir.get_dir_all_files(src):
            # 处理每个文件的开始时间
            src_all_size += BaseFile.get_file_size(files)
            dst_file_size = 0
            start_time = time.time()
            src_file_location += 1
            print("next source_path:" + files)

            for block in BaseFile.read_file_rb_block(files,BLOCK_SIZE=block_size):
                f.write(block)

            if BaseFile.get_file_size(self.outPathFile) % a_size == 1:
                print("process_src:%d/%d, dst_size:%d, src_size:%d, src_all_size:%d, Time total:%.2f/%.2f" % (src_file_location, src_file_num, dst_file_size ,BaseFile.get_file_size(files), src_all_size, (time.time() - start_time),(time.time() - StartTime) ))
            dst_file_size = BaseFile.get_file_size(self.outPathFile)
            print("finish one file;process_src:%d/%d, dst_size:%d, src_size:%d, src_all_size:%d, Time total:%.2f/%.2f" % (src_file_location, src_file_num, dst_file_size ,BaseFile.get_file_size(files), src_all_size, (time.time() - start_time),(time.time() - StartTime) ))
            if dst_size is not None:
                if BaseFile.get_file_size(self.outPathFile) >= dst_size:
                    f.close()
                    self.outPathFile = BaseFile.change_file(self.outPathFile, size=dst_size,ending='gz')
                    f = gzip.open(self.outPathFile, "wb")
                    print("new dst_path: %s" % self.outPathFile)
                    dst_file_size = 0
            # 程序结束花费时间时间
        print('\nProce Over\nTime total:' + repr(time.time() - StartTime) + '\n')


if __name__ == '__main__':
    old_path = r'\\192.168.31.188\download\cnki_qk\download\get_ref\input'
    new_path = r'\\192.168.31.188\download\cnki_qk\download\get_ref\output'
    a = MergeGzFile()
    a.line_all_2_one_gz(old_path,new_path,dst_size=1024*1024*100)
    # a.block_all_2_one(old_path,new_path,dst_size=1024*1024*10)

