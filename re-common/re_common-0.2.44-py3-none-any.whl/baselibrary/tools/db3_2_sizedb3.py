# -*- coding: utf-8 -*-
# @Time    : 2020/6/16 9:29
# @Author  : suhong
# @File    : db3_2_sizedb3.py
# @Software: PyCharm
"""
获取输入db3文件夹路径，获取db3表名、列名，创建一个db3
往新的db3写入select信息直到指定大小，切换
"""
import sqlite3
import sys

from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile


class UniformSizeDb3(object):
    def __init__(self):
        self.table_name = None
        self.column_name = list()
        self.info_list = list()
        self.all_num = 0

    def work(self, file_path=None, out_path=None,size=200 * 1024 * 1024):
        if file_path is None and out_path is None:
            print("path error")
            sys.exit(-1)
        for path in BaseDir.get_dir_all_files(file_path):
            count = 1
            print(path)
            # print(BaseFile.get_file_size(path)/1024/1024)
            conn = sqlite3.connect(path)
            cur = conn.cursor()
            # 获取表名和字段名称
            cur.execute("SELECT name FROM sqlite_master where type='table'")
            row1 = cur.fetchone()
            self.table_name = row1[0]
            cur.execute("PRAGMA table_info([{}])".format(self.table_name))
            row2 = cur.fetchall()
            for row in row2:
                self.column_name.append(row[1])
            column_name = tuple(self.column_name)
            self.column_name.clear()

            # 获取原始db3的创建table语句
            cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name = '{}'".format(self.table_name))
            create_table_sql = cur.fetchone()[0]
            insert_sql = "insert into {} {} values ({})".format(self.table_name, column_name, "?," * len(column_name))
            insert_sql = insert_sql.replace("'", "").replace("?,)", "?)")



            out_file = "{}/{}_{}.db3".format(out_path, BaseFile.get_filename_not_extsep(path), count)
            conn_2 = sqlite3.connect(out_file)
            cur_2 = conn_2.cursor()
            cur_2.execute("SELECT name FROM sqlite_master where type='table'")
            name_row = cur_2.fetchone()
            if name_row is None:
                cur_2.execute(create_table_sql)
                conn_2.commit()

            # 查询原表信息 并插入新表
            cur.execute("select * from {}".format(self.table_name))
            while True:
                rows = cur.fetchone()
                if rows:
                    self.info_list.append(rows)

                    if BaseFile.get_file_size(out_file) >= size:
                        count +=1
                        out_file = "{}/{}_{}.db3".format(out_path, BaseFile.get_filename_not_extsep(path), count)
                        conn_2 = sqlite3.connect(out_file)
                        cur_2 = conn_2.cursor()
                        cur_2.execute("SELECT name FROM sqlite_master where type='table'")
                        name_row = cur_2.fetchone()
                        if name_row is None:
                            cur_2.execute(create_table_sql)
                            conn_2.commit()
                        print("outfilepath:{}".format(out_file))

                    if len(self.info_list) >= 10000:
                        self.all_num += len(self.info_list)
                        cur_2.executemany(insert_sql, self.info_list)
                        conn_2.commit()
                        print("do all sql:{}".format(self.all_num))
                        self.info_list.clear()
                else:
                    break
            self.all_num += len(self.info_list)
            cur_2.executemany(insert_sql, self.info_list)
            conn_2.commit()
            cur_2.close()
            print("do all sql:{}".format(self.all_num))
            self.info_list.clear()
            self.all_num = 0


if __name__ == '__main__':
    file_path = r'E:\更新数据\adb3'
    out_path = r'E:\更新数据\test_db3'
    u = UniformSizeDb3()
    u.work(file_path, out_path)
