"""
对比两个db3的主键个数及内容是否相同
以及主键下所有信息的差异
输出对应关系不同的数据保存文件
如果两个db3全字段相同则不输出文件
"""
import sqlite3
import time

from re_common.baselibrary.utils.basedir import BaseDir


class Constrast(object):
    def __init__(self):
        self.curPath = BaseDir.get_file_dir_absolute(__file__)
        self.set_old = set()
        self.set_new = set()


    def read_primary_key(self):
        """
        取出主键，对照其内容，old参照new的rawid
        :return:
        """
        print("对照主键")
        old_path = r'\\192.168.31.177\down_data\cnkiwanfang\zt_wf_qk_20200323\db3\zt_wf_qk_20200323_0001.db3'
        new_path = r'E:\更新数据\db3\zt_wf_qk.20200331_000.db3'
        old = sqlite3.connect(old_path)
        new = sqlite3.connect(new_path)
        sql = "select rawid from modify_title_info_zt"
        old_cur = old.cursor()
        old_cur.execute(sql)
        for item in old_cur.fetchall():
            rawid = item[0]
            self.set_old.add(rawid)
        new_cur = new.cursor()
        new_cur.execute(sql)
        for item in new_cur.fetchall():
            rawid = item[0]
            self.set_new.add(rawid)
        print(len(self.set_new - self.set_old))


    def read_content(self):
        """
        判断主键相同的，内容是否相同，new参照old的内容
        输出content_contrast.txt
        :return:
        """
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        print("对照内容")
        old_path = r'\\192.168.31.177\down_data\cnkiwanfang\zt_wf_qk_20200323\db3\zt_wf_qk_20200323_0001.db3'
        new_path = r'E:\更新数据\db3\zt_wf_qk.20200331_000.db3'
        old = sqlite3.connect(old_path)
        old.row_factory = dict_factory
        new = sqlite3.connect(new_path)
        new.row_factory = dict_factory

        sql = "select rawid from modify_title_info_zt"
        old_cur = old.cursor()
        new_cur = new.cursor()
        old_cur.execute(sql)
        rawidlist = []

        for item in old_cur.fetchall():

            rawid = item['rawid']
            rawidlist.append(rawid)
            if len(rawidlist) <= 10000:
                continue
            sql = "select * from modify_title_info_zt where rawid in {}".format(tuple(rawidlist))
            # print(sql)
            old_cur.execute(sql)
            new_cur.execute(sql)
            old_message = old_cur.fetchall()
            new_mesaage = new_cur.fetchall()
            dicts_old ={}
            dicts_new = {}
            for itemss in old_message:
                dicts_old[itemss["rawid"]] = itemss
            for items in new_mesaage:
                dicts_new[items["rawid"]] = items

            for k,v in dicts_old.items():
                for kk,vv in v.items():
                    if kk != "batch" and kk != 'gch' and kk != 'subject_clc':
                        if vv != dicts_new[k][kk]:
                            print("rawid:{}".format(k))
                            print("字段名:{}".format(kk))
                            print("old_message:{}".format(vv))
                            print("new_message:{}".format(dicts_new[k][kk]))
                            time.sleep(100)
                    if kk == 'gch' or kk == 'subject_clc':
                        if vv != dicts_new[k][kk] and (vv == "" or dicts_new[k][kk]==""):
                            print("rawid:{}".format(k))
                            print("字段名:{}".format(kk))
                            print("old_message:{}".format(vv))
                            print("new_message:{}".format(dicts_new[k][kk]))
                            time.sleep(100)
            print("*************************************")
            rawidlist.clear()





    def run(self):
        """
        启动程序
        :return:
        """
        # self.read_primary_key()
        self.read_content()

if __name__ == '__main__':
    c = Constrast()
    c.run()

