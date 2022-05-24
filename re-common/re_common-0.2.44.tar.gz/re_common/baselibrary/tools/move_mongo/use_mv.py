import click

###########################################
# 同项目调用基础包
import datetime
import gzip
import json
import os
import sys
import time

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-5]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)
print(TopPath)
############################################


from re_common.baselibrary.tools.move_mongo.move_mongo_table import MoveMongodbColl, MoveMongodbThreadRun


class Configs(object):

    def __init__(self):
        self.db3_path = r"D:\config\mvmg\db3\test_images.db3"
        self.db3_encoding = "utf-8"
        self.mgdb_conn = "mongodb://192.168.31.30:32417/"
        self.mgdb_conn_motor = "mongodb://192.168.31.30:32417/htmljson.wanfang_ref?authSource=htmljson"
        self.mgdb_db = "htmljson"
        self.mgdb_col = "cx_journal_detail"

        self.mgdb_conn2_motor = "mongodb://cjrw:vipdatacenter@192.168.31.243:32920,192.168.31.206:32920,192.168.31.208:32920/?authSource=htmljson"
        self.mgdb_db2 = "htmljson"
        self.mgdb_col2 = "cx_journal_detail"

        self.mq_name = "mongodb.move.send"
        self.mq_name_work = "mongodb.move.worker"

        self.error_dir = r"D:\config\mvmg\log"


conf = Configs()


def one_init():
    # 第一步 初始化数据到db3文件
    MoveMongodbColl(conf).one_init()


# 第二步 开始转移 使用send_work_recv结构 共开三个进程

def send():
    MoveMongodbColl(conf).two_send()


def works():
    MoveMongodbThreadRun(1, conf).run()


def works_many():
    mmtr = MoveMongodbThreadRun(1, conf)
    mmtr.is_many_move = True
    mmtr.num_list = 1000
    mmtr.num_info_list = 10
    mmtr.run()


def recv():
    MoveMongodbColl(conf).two_recv()


@click.command()
@click.option('--name',
              help='func name')
def main(name):
    if name == "send":
        send()
    elif name == "one_init":
        one_init()
    elif name == "works":
        works()

    elif name == "works_many":
        works_many()

    elif name == "recv":
        recv()


if __name__ == '__main__':
    main()
