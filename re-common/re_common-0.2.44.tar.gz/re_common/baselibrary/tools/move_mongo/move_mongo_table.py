import asyncio
import copy
import datetime
import json
import time

from pymongo.errors import DuplicateKeyError
import traceback

from re_common.baselibrary.mthread.MThreadingRun import MThreadingRun2
from re_common.baselibrary.mthread.mythreading import ThreadVal, ThreadInfo
from re_common.baselibrary.utils.basefile import BaseFile
from re_common.baselibrary.utils.basemotor import BaseMotor
from re_common.baselibrary.utils.basepymongo import BasePyMongo
from re_common.facade.sqlite3facade import Sqlite3Utiles
from re_common.facade.use.mq_use_facade import UseMq


class Configs(object):

    def __init__(self):
        self.db3_path = r"F:\fun2\test_images.db3"
        self.db3_encoding = "utf-8"
        self.mgdb_conn = "mongodb://192.168.31.30:32417/"
        self.mgdb_conn_motor = "mongodb://192.168.31.30:32417/htmljson.wanfang_ref?authSource=htmljson"
        self.mgdb_db = "htmljson"
        self.mgdb_col = "wanfang_ref"

        self.mgdb_conn2_motor = "mongodb://cjrw:vipdatacenter@192.168.31.243:32920,192.168.31.206:32920,192.168.31.208:32920/?authSource=htmljson"
        self.mgdb_db2 = "htmljson"
        self.mgdb_col2 = "wanfang_ref"

        self.mq_name = "mongodb.move.send"
        self.mq_name_work = "mongodb.move.worker"

        self.error_dir = r"F:\fun2\log"


class MoveMongodbColl(object):
    def __init__(self, conf):
        self.conf = conf
        self.first_id = ""
        self.id_list = []
        self.recv_list = []

    def init_conn_mongodb(self):
        self.basemongo = BasePyMongo(self.conf.mgdb_conn)
        self.basemongo.use_db(self.conf.mgdb_db)
        self.basemongo.create_col(self.conf.mgdb_col)

        self.bs = BaseMotor()
        self.bs.AsyncIOMotorClient(
            self.conf.mgdb_conn_motor,
            self.conf.mgdb_db)
        self.bs.get_col(self.conf.mgdb_col)

        self.bs2 = BaseMotor()
        self.bs2.AsyncIOMotorClient(
            self.conf.mgdb_conn2_motor,
            self.conf.mgdb_db2)
        self.bs2.get_col(self.conf.mgdb_col2)

    def create_db3_table(self):
        """
        创建表
        :return:
        """
        sql1 = "PRAGMA foreign_keys = false;"
        sql2 = 'DROP TABLE IF EXISTS "cxids";'
        sql3 = 'CREATE TABLE "cxids" ("ids" TEXT NOT NULL,"stat" integer NOT NULL DEFAULT 0,PRIMARY KEY ("ids"));'
        sql4 = 'PRAGMA foreign_keys = true;'
        self.db3.ExeSqlliteList([sql1, sql2, sql3, sql4])

    def init_db3(self):
        self.db3 = Sqlite3Utiles().Sqlite3DBConnectFromFilePath(self.conf.db3_path, encoding=self.conf.db3_encoding)

    def init_mq(self):
        self.use_send = UseMq(self.conf.mq_name)
        self.use_work = UseMq(self.conf.mq_name_work)

    def send_list(self):
        while True:
            if self.use_send.get_server_mq_num(10000):
                for i in self.id_list:
                    dict_info = {
                        '_id': i
                    }
                    info_str = json.dumps(dict_info)
                    print(info_str)
                    self.use_send.easy_send_mq(info_str)
                self.id_list.clear()
                break
            else:
                time.sleep(1)

    def send_db3(self):
        while True:
            sql = 'select * from cxids where stat=0 limit 20000'
            rows = self.db3.SelectFromSqlliteFetchall(sql)
            if len(rows) == 0:
                print('查询结束 0 状态结束 查询-1状态 time sleep 60s')
                time.sleep(60)
                sql = 'select * from cxids where stat=-1 limit 20000'
                rows = self.db3.SelectFromSqlliteFetchall(sql)
                if len(rows) == 0:
                    print('查询结束 -1 状态结束 结束发送')
                    break
            for row in rows:
                _id = row[0]
                self.id_list.append(_id)
                if len(self.id_list) >= 10000:
                    sql = "update cxids set stat = -1 where ids in {}".format(tuple(self.id_list))
                    self.db3.ExeSqlliteSql(sql)
                    self.send_list()

            if len(self.id_list) > 1:
                sql = "update cxids set stat = -1 where ids in {}".format(tuple(self.id_list))
                self.db3.ExeSqlliteSql(sql)
                self.send_list()

            if len(self.id_list) == 1:
                sql = "update cxids set stat = -1 where ids='{}'".format(self.id_list[0])
                self.db3.ExeSqlliteSql(sql)
                self.send_list()

    def callback2(self, ch, method, properties, body):
        json_data = json.loads(body)
        _id = json_data['_id']
        self.recv_list.append(_id)
        if len(self.recv_list) >= 500:
            sql = "update cxids set stat = 1 where ids in {}".format(tuple(self.recv_list))
            if self.db3.ExeSqlliteSql(sql):
                self.recv_list.clear()
        else:
            print('[{}]未更新stat条数{}'.format(datetime.datetime.now(), len(self.recv_list)))

    def recv(self, results=None, *args, **kwargs):
        self.use_work.callback2 = self.callback2
        self.use_work.get_mq()

    def get_first_mongo_id(self):
        for i in self.basemongo.find({"_id": {"$gt": self.first_id}}, {"_id": 1}).sort([("_id", 1)]).limit(1):
            self.first_id = i["_id"]
            print("first_id is:" + self.first_id)

    def init_data_db3(self):
        c = 0
        c1 = -1
        while True:
            lists = []
            for i in self.basemongo.find({"_id": {"$gte": self.first_id}}, {"_id": 1}).sort([("_id", 1)]).limit(
                    1000000):
                c = c + 1
                self.first_id = i["_id"]
                lists.append((i["_id"], 0))
                if c % 10000 == 1:
                    print(len(lists))

            sql = "insert or ignore into cxids(`ids`,`stat`) values (?,?)"
            self.db3.ExeSqlliteMany(sql, lists)
            print(c)
            if c1 == c:
                break
            if len(lists) == 1:
                break
            c1 = c
            lists.clear()

    def one_init(self):
        """
        第一步 初始化id数据到db3目录
        :return:
        """
        self.init_conn_mongodb()
        self.init_db3()
        self.create_db3_table()
        self.get_first_mongo_id()
        self.init_data_db3()

    def two_send(self):
        """
        分布式的send方法
        :return:
        """
        self.init_db3()
        self.init_mq()
        self.send_db3()

    def two_recv(self):
        self.init_db3()
        self.init_mq()
        self.recv()


class MoveMongodbThreadRun(MThreadingRun2):
    def __init__(self, num, conf):
        super(MoveMongodbThreadRun, self).__init__(num)
        self.thread_pool.work_queue.set_size(10)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.mvmc = MoveMongodbColl(conf)
        self.mvmc.init_mq()
        self.mvmc.init_conn_mongodb()
        self.mvmc.use_send.callback2 = self.callback2
        self.lists = []
        self.info_list = []
        self.is_many_move = False
        # 配置二维数组的每组数据数量，如果为批量转移 建议设置为10000
        self.num_list = 100
        self.num_info_list = 10

    def callback2(self, ch, method, properties, body):
        json_data = json.loads(body.decode())
        # self.add_job(self.func, dicts)
        self.lists.append((json_data))
        # 异步需要 10 * 100 的二维list
        if self.is_many_move:
            work_size = self.thread_pool.work_queue.get_size()
            if work_size >= 3:
                time.sleep(10)
        if len(self.lists) >= self.num_list:
            self.info_list.append(copy.deepcopy(self.lists))
            self.lists.clear()
            print(len(self.info_list))

        if len(self.info_list) >= self.num_info_list:
            self.add_job(self.func, copy.deepcopy(self.info_list))
            self.info_list.clear()

    def set_task(self, threadval: ThreadVal, *args, **kwargs):
        self.mvmc.use_send.get_mq()

    def deal_results(self, threadval: ThreadVal, *args, **kwargs):
        result_queue = threadval.get_result_queue()
        while True:
            while not result_queue.is_empty():
                result = result_queue.get()
                t_1, t_2 = result
                if t_1 == "err":
                    file_path = BaseFile.get_new_filename(self.mvmc.conf.error_dir, "err_parse_2.txt")
                    BaseFile.single_add_file(file_path, t_2 + '\n')
                if t_1 == "err_Exception":
                    file_path = BaseFile.get_new_filename(self.mvmc.conf.error_dir, "err_Exception_2.txt")
                    BaseFile.single_add_file(file_path, t_2 + '\n')
                if t_1 == 'right':
                    self.send_update_info(t_2)
                self.thread_pool.result_queue.task_done()
            time.sleep(1)

    def send_update_info(self, _id):
        dict_info = {
            "_id": _id,
        }
        info_str = json.dumps(dict_info)
        while True:
            if self.mvmc.use_work.send_mq(info_str, num=10000):
                break
            time.sleep(1)

    def setProxy(self, threadval: ThreadVal, proxysList=None):
        time.sleep(60)

    def is_break(self):
        return False

    def thread_pool_hook(self, threadinfo: ThreadInfo):
        # 设置代理线程不重启，默认会重启
        if threadinfo.get_thread_name() == self.etn.proxythreadname:
            threadinfo.set_is_restart(False)
        # if threadinfo.get_thread_name() == self.etn.taskthreadname:
        #     threadinfo.set_is_restart(False)
        return {}

    def doc_hook(self, item):
        return item

    async def par_html(self, result_queue, lists):
        for info in lists:
            _id = info["_id"]
            try:
                try:
                    # 不存在就插入

                    item = await self.mvmc.bs.select_one({"_id": _id})
                    item_result = self.doc_hook(item)
                    await self.mvmc.bs2.insert_one(item_result)
                    print("{}插入".format(_id))
                    result_queue.put(("right", _id))
                except DuplicateKeyError as e:
                    print("{}存在".format(_id))
                    result_queue.put(("right", _id))
                except Exception as e:
                    traceback.print_exc()
                    result_queue.put(("err_Exception", _id + ":" + traceback.format_exc()))
            except Exception as e:
                traceback.print_exc()
                result_queue.put(("err_Exception", _id + ":" + traceback.format_exc()))

    async def par_html_many(self, result_queue, lists):
        insert_list = []
        for i in range(0, len(lists), 500):
            lists_item = lists[i:i + 500]
            try:
                try:
                    def deal_dicts(dd):
                        return dd["_id"]
                    lists_item = list(map(deal_dicts, lists_item))
                    # 不存在就插入
                    docs = await self.mvmc.bs.select({"_id": {"$in": lists_item}})
                    for item in docs:
                        item_result = self.doc_hook(item)
                        insert_list.append(item_result)
                        print("获取mongo num:" + str(len(insert_list)))
                        if len(insert_list) >= 100:
                            start_time = time.time()
                            result = await self.mvmc.bs2.insert_many(insert_list)
                            print("百条数据插入时间:" + str(time.time() - start_time))
                            for _id in result.inserted_ids:
                                print("{}插入".format(_id))
                                result_queue.put(("right", _id))
                            insert_list.clear()
                except DuplicateKeyError as e:
                    print("有数据存在，无法插入")

                except Exception as e:
                    traceback.print_exc()
                    result_queue.put(("err_Exception", traceback.format_exc()))
            except Exception as e:
                traceback.print_exc()
                result_queue.put(("err_Exception", traceback.format_exc()))

        if len(insert_list) > 0:
            try:
                result = await self.mvmc.bs2.insert_many(insert_list)
                for _id in result.inserted_ids:
                    print("{}插入".format(_id))
                    result_queue.put(("right", _id))
                insert_list.clear()
            except DuplicateKeyError as e:
                print("存在某个key 批量插入失败")
            except Exception as e:
                traceback.print_exc()
                result_queue.put(("err_Exception", traceback.format_exc()))

    def fun(self, threadval, *args, **kwargs):
        result_queue = threadval.get_result_queue()
        func_list = []
        for lists in args[0]:
            if self.is_many_move:
                func_list.append(self.par_html_many(result_queue, lists))
            else:
                func_list.append(self.par_html(result_queue, lists))
        self.loop.run_until_complete(asyncio.wait(func_list))
