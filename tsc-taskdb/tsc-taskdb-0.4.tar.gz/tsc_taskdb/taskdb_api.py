from tinydb import TinyDB, Query
from flask import Flask, request
from pprint import pprint, pformat
from bson import ObjectId
import shutil
import os
import numpy as np
import copy
import random
import time
import json
import threading
import traceback
import ast
import requests
import logging
import heapq
import pymongo
import datetime
from tsc_auto import set_gpu


def get_logger(path='log/logger.log', out_log=('ERROR', 'CRITICAL'), mode='w'):
    """
    获取可以写入文件的日志类, 需要包 logging, os
    :param path: str; 输出的日志路径文件, 会根据out_log重命名文件
    :param out_log: list or tuple; 包含哪几种类型的日志文件, 可以包括: DEBUG,INFO,WARNING,ERROR,CRITICAL
    :param mode: str; 日志写入的模式, w表示覆盖, a表示追加
    :return: logger
    """
    print(__file__)
    # 创建目录
    dir = os.path.split(path)[0]
    if dir and not os.path.exists(dir):
        os.makedirs(dir)
    # 创建日志类
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    # 创建日志文件
    for name in out_log:
        fname, fextension = os.path.splitext(path)
        fh = logging.FileHandler(f'{fname}.{name.lower()}{fextension}', mode=mode)
        fh.setLevel(name)
        fh.setFormatter(logging.Formatter(
            # 输出例如: 2021-04-05 15:47:28,573 - shiyan3.py/<module>[line:28] - ERROR: 你好
            "%(asctime)s - %(filename)s/%(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s"
        ))
        logger.addHandler(fh)
    return logger


class TaskDB:
    def __init__(self, dir, new=False, mongo_url=None, mongo_db=None, mongo_co=None, tiny_to_mongo=False):
        """
        注意: 不要对一个数据库打开两个 TaskDB, 否则可能产生一些错误, 比如查询缓存以及非实时修改的上层代码的冲突
        使用了 mongo 参数将不再使用 TaskDB 和镜像文件夹控制, 但是未执行的 main_path 还是会被删除
        :param dir: str; 参数数据库的存储文件夹, 文件夹下还将存储其他 main_path
            使用 TaskDB 时文件夹内其他数据可能会被清理数据(见close函数)
        :param new: bool; 是否覆盖(删除并重建)该路径原有数据库. 注意: 如果为True, 哪怕正在使用中的数据库也会覆盖
            如果 new=True 并且使用 mongo 则会清除原有 collection 内容
        :param mongo_url: None or str; mongodb 的连接url, 比如: mongodb://user:password@ip:port/
            存在这个参数会被认为是 mongodb 模式
        :param mongo_db: None or str; mongodb 的 database name. new=True 时必须, 否则自动读取 config
        :param mongo_co: None or str; mongodb 的 collection name. new=True 时必须, 否则自动读取 config
        :param tiny_to_mongo: bool; 如果 dir 存在 TinyDB 数据库, 同时也存在 mongodb, 是否把 TinyDB 中的数据移动到 mongodb
            只是移动, 不会覆盖 mongodb 中已有的 no 编号数据. 用于数据迁移. 迁移后不再需要, 否则一直迁移就删除不了了
        """
        # 不存在目录新建
        if not os.path.exists(dir):
            os.makedirs(dir)
        db_folder = f'{dir}/database'
        db_conf = f'{dir}/__db.conf'  # 数据库配置文件
        if mongo_url:
            self._db = pymongo.MongoClient(mongo_url)
            print(self._db.server_info())  # 连接不成功会报错
            # 读取和写入配置文件
            if not mongo_db or not mongo_co:
                assert not new, 'mongodb 新建数据库必须要参数 mongo_db 和 mongo_co !'
                with open(db_conf, 'r', encoding='utf8') as r:
                    config_D = ast.literal_eval(r.read().strip())
                mongo_db = config_D['mongo_db']
                mongo_co = config_D['mongo_co']
            else:
                config_D = {'mongo_db': mongo_db, 'mongo_co': mongo_co}
                with open(db_conf, 'w', encoding='utf8') as w:
                    w.write(pformat(config_D))
            # 生成数据库
            self._db_tasks = self._db[mongo_db][mongo_co]  # type: pymongo.collection.Collection
            if new:
                self._db_tasks.delete_many({})
            # unique=True 该键将不能更新; 已有不同索引会报错
            self._db_tasks.create_index([('no', pymongo.ASCENDING)], unique=True, background=True)
            for i in ['priority', 'executed', 'main_path']:
                self._db_tasks.create_index([(i, pymongo.ASCENDING)], unique=False, background=True)
            # tinydb 迁移
            if os.path.exists(f'{db_folder}.json') and tiny_to_mongo:
                db = TinyDB(f'{db_folder}.json', encoding='utf8', access_mode='r+')
                n = 0
                for task in db.table("tasks").all():
                    if self._db_tasks.update_many({'no': task['no']}, {'$setOnInsert': task}, upsert=True).upserted_id:
                        n += 1
                print('tiny_to_mongo count: ', n)
        else:
            # 镜像文件夹, 用于是否重新清理参数
            if not os.path.exists(db_folder):
                os.makedirs(db_folder)
            # 生成数据库
            if new or not os.path.exists(f'{db_folder}.json'):
                print('新建TinyDB数据库:', f'{db_folder}.json')
                db = TinyDB(f'{db_folder}.json', encoding='utf8', access_mode='w+')
            else:
                db = TinyDB(f'{db_folder}.json', encoding='utf8', access_mode='r+')
            # 查询缓存 cache_size 的介绍: https://tinydb.readthedocs.io/en/latest/usage.html#query-caching
            self._db_tasks = db.table("tasks", cache_size=None)
            self._db = db  # 用于关闭数据库
        self._dir = dir.rstrip('/\\')
        # self.clean()  # 不提前清洗防止只读数据库需求干扰正在运行的程序

    @property
    def result(self):
        """
        子类需要在父类基础上重载
        一个任务-结果模版. 兼容TinyDB需要key只能是str类型, 且不能有set, vaule不能带有双引号, TinyDB不支持多线程(需要lock)
        :return:
        """
        result = {
            'no': '1617199720.1552498-0.17835507118070226',  # 任务唯一编号 - 构建任务的时间时间戳+随机数, 极低概率重复
            # add_task 时修改
            'paras': {'test': [1, 2], },  # run_tasks 需要的参数
            'filter': {},  # 用于结果过滤的相关参数
            'priority': 1,  # 任务运行的优先级, 数值越小越优先, 并行时小数值任务未完考虑不运行后面任务. 防止任务之间的依赖
            # run_tasks 时修改
            'executed': False,  # 是否已执行得到结果
            'machine': {},  # 完成这个任务的机器信息, 可以使用 TaskDB.get_machine()
            'main_path': 'None',  # 数据生成的主目录, 和数据库文件目录同级, 不能叫database(或者以__开头), 用于快捷手动重置任务(删除database中对应文件夹即可)
        }
        return result

    @property
    def db_dir(self):
        """
        数据库文件所在主目录
        :return:
        """
        return self._dir

    @property
    def tasks(self):
        """
        返回数据库中的所有任务, tinydb 没有深拷贝, 注意不要修改
        数据库过大不建议频繁使用, 如果是 mongodb 可以使用 que_tasks 的 aggregate 来实现部分返回
        :return:
        """
        if self.is_mongo:
            return list(self.que_tasks({}))
        else:
            return self._db_tasks.all()

    @property
    def uncomplete_tasks(self):
        """
        获取未完成的任务, tinydb 浅拷贝
        数据库过大不建议频繁使用, 如果是 mongodb 可以使用 que_tasks 的 aggregate 来实现部分返回
        :return:
        """
        tasks = self.que_tasks({'executed': False})
        # 按照优先级排序
        tasks = sorted(tasks, key=lambda d: d['priority'])
        return tasks

    @property
    def is_mongo(self):
        if isinstance(self._db_tasks, pymongo.collection.Collection):
            return True
        else:
            return False

    @staticmethod
    def _numpy_to_base(result, print_type=False):
        """
        递归将 result 中可能是numpy的结果转换python基本类型, 防止无法写入json数据库
        :param result:
        :param print_type: bool; 是否输出每个修改后的所有类型及变量的前30个字符, 用于调试
        :return:
        """
        if isinstance(result, dict):
            result_ = {}
            for k, v in result.items():
                result_[k] = TaskDB._numpy_to_base(v, print_type)
        elif isinstance(result, tuple) or isinstance(result, list):
            result_ = [TaskDB._numpy_to_base(v, print_type) for v in result]
        elif "'numpy." in str(type(result)):
            result_ = np.array(result).tolist()
        elif isinstance(result, set):
            raise NameError(f'tinydb数据库不能存入set类型: {result}')
        else:
            if isinstance(result, str) and '"' in result:
                raise NameError('不能带有双引号!', result)
            result_ = result
        if print_type:
            return print(type(result_), ':', str(result_)[:30], '...')
        return result_

    @staticmethod
    def _result_to_query(result, is_mongo=False, root=''):
        """
        这是对存在参数完全相等的匹配
        if is_mongo:
            将结果模版转换为 mongodb 的查询形式
            list/tuple 匹配考虑顺序
        else:
            将结果模版转换为 TinyDB 的查询形式, 返回后需要使用 eval()
            list/tuple 匹配不考虑顺序
            如果 list/tuple 中有 list/tuple 那就要一摸一样才能匹配上
            如果 list/tuple 中的 list/tuple 有 tuple 则匹配不上
        :param result: dict; 参考 一个任务-结果模版
        :param is_mongo: bool; 是否转换为 mongodb 的查询
        :param root: str; 递归需要, 不要传入参数
        :return: str or dict
        """
        if is_mongo:
            query = {}
            if isinstance(result, dict):
                for k, v in result.items():
                    root_ = f'{root}.{k}' if root else k
                    q = TaskDB._result_to_query(v, is_mongo=is_mongo, root=root_)
                    if '$and' in q and '$and' in query:  # 统计value都有数组就会出现多个$and
                        query['$and'] += q['$and']
                        del q['$and']
                    query.update(q)
            elif isinstance(result, tuple) or isinstance(result, list):
                query.setdefault('$and', [])
                for k, v in enumerate(result):  # 数组也要编号
                    query['$and'].append(TaskDB._result_to_query(v, is_mongo=is_mongo, root=f'{root}.{k}'))
            else:
                query[root] = result
        else:
            root = root if root else 'Query()'
            q_L = []
            for k, v in result.items():
                root_ = f'{root}["{k}"]'
                q = ''
                if isinstance(v, dict):
                    q = TaskDB._result_to_query(v, is_mongo=is_mongo, root=root_)
                elif isinstance(v, tuple) or isinstance(v, list):
                    v_ = []
                    for i in v:
                        if isinstance(i, dict):
                            i = TaskDB._result_to_query(i, is_mongo=is_mongo, root='Query()')
                            if i:
                                i = f'{root_}.any({i})'
                                q_L.append(i)  # list/tuple 中有 dist
                        else:
                            if isinstance(i, tuple):  # list/tuple 中有 tuple
                                i = list(i)
                            v_.append(i)
                    if v_:
                        q = f'{root_}.all({v_})'
                else:
                    if isinstance(v, str):  # str需要加双引号, 所以v不能含有双引号
                        v = f'"{v}"'
                    q = f'({root_} == {v})'
                if q:
                    q_L.append(q)
            query = ' & '.join(q_L)
        return query

    @staticmethod
    def get_machine(name='default', is_gpu=None, **kwargs):
        """
        完成这个任务的机器信息
        :param name: str; 自定义名字
        :param is_gpu: bool; 是否使用gpu
        :param kwargs:
        :return:
        """
        ret = set_gpu(return_more=True)
        ret.update({
            'name': name,
            'is_gpu': is_gpu,
        })
        return ret

    def mongo_to_tiny(self):
        """
        将 mongodb 的数据转换到 tinydb, 会清空原来路径的 tinydb 和镜像文件夹数据
        :return: int; 数据总量
        """
        if not self.is_mongo:
            return -1
        db_folder = f'{self.db_dir}/database'
        tasks = self.tasks
        if os.path.exists(db_folder):
            shutil.rmtree(db_folder)
        for task in tasks:
            del task['_id']  # mongodb 的这个_id不能变名字, ObjectId 不能插入 tinydb
            main_path = f'{db_folder}/{task["main_path"]}'
            if task['executed'] and not os.path.exists(main_path):
                os.makedirs(main_path)
        doc_ids = TinyDB(f'{db_folder}.json', encoding='utf8', access_mode='w+').table("tasks").insert_multiple(tasks)
        return len(doc_ids)

    def add_tasks(self, paras_L: list, filter_L: list = None, priority_L: list = None):
        """
        增加多个任务
        :param paras_L: [dict,..]; 运行任务需要的参数, list包裹多组参数
        :param filter_L: [None or dict,..]; 结果过滤器
        :param priority_L: [int,..]; 任务运行的优先级, 数值越小越优先, 并行时小数值任务未完考虑不运行后面任务
        :return: a list containing the inserted documents' IDs
        """
        if filter_L is None:
            filter_L = [None] * len(paras_L)
        if priority_L is None:
            priority_L = [1] * len(paras_L)
        assert len(paras_L) == len(filter_L) == len(priority_L), '增加的任务参数数量不匹配!'
        result_L = []
        for paras, filter, priority in zip(paras_L, filter_L, priority_L):
            assert isinstance(paras, dict), type(paras)
            assert isinstance(filter, dict) or filter is None, type(filter)
            assert isinstance(priority, int), type(priority)
            result = self.result
            result.update({
                'no': f'{time.time()}_{random.random()}',
                'paras': copy.deepcopy(paras),
                'filter': copy.deepcopy(filter),
                'priority': priority,
                'executed': False,
            })
            result = self._numpy_to_base(result)
            result_L.append(result)
        if isinstance(self._db_tasks, pymongo.collection.Collection):
            doc_ids = self._db_tasks.insert_many(result_L).inserted_ids
        else:
            doc_ids = self._db_tasks.insert_multiple(result_L)
        return doc_ids

    def del_tasks(self, result):
        """
        删除任务, 输出的数据文件夹会被保留
        :param result: dict; 部分类似 result 的格式
        :return: 删除数量
        """
        result = self._numpy_to_base(result)
        result = self._result_to_query(result, is_mongo=self.is_mongo)
        if isinstance(self._db_tasks, pymongo.collection.Collection):
            deleted_count = self._db_tasks.delete_many(result).deleted_count
        else:
            deleted_count = len(self._db_tasks.remove(eval(result)))
        return deleted_count

    def que_tasks(self, result, batch_size=3000, limit=None):
        """
        查询任务
        :param result: dict or list; 部分类似 result 的格式
            dict: 对存在参数完全相等的匹配
                tinydb: 数组匹配不关心顺序, 数据数组中有查询数组没有的对象也可以, 等价all匹配
                mongo: 数组匹配关心顺序, 如果数据数组很长, 后面有查询数组没有的对象也可以, 类似于 {'$and': [{'a.0': 1}, {'a.1': 2}]}
                    为了兼容深层嵌套而考虑顺序, 不想考虑顺序可以使用agg方式
            list: 将查询的 result 作为 mongodb 的 aggregate 操作语句而不做其他处理. TinyDB 报错
        :param batch_size: int; mongodb: The maximum number of documents to return per batch
        :param limit: int or None; 使用int会进行返回数量的最大限制. 在 mongodb 中使用这个可以加快速度
        :return: list of matching documents
        """
        if isinstance(result, dict):
            result = self._numpy_to_base(result)
            result = self._result_to_query(result, is_mongo=self.is_mongo)
        if isinstance(self._db_tasks, pymongo.collection.Collection):
            if isinstance(result, dict):
                docs = self._db_tasks.find(result)
            else:
                docs = self._db_tasks.aggregate(result)
            docs = docs.batch_size(batch_size)
            if limit:
                docs = docs.limit(limit)
        else:
            assert isinstance(result, str), 'tinydb 不支持非dict类型的查询: ' + str(type(result))
            docs = self._db_tasks.search(eval(result))
            if limit:
                docs = docs[:limit]
        return list(docs)

    def update_tasks(self, result_L: list, no_L: list):
        """
        更新多个结果
        TinyDB: 如果已执行的话会生成完成标志的镜像文件夹, main_path没有提供会生成默认
        :param result_L: [dict,..]; 部分类似 result 的格式, mongodb 不能含 $ operators, 更新不含 no
        :param no_L: [result['no'],..]; 编号, 用于查找对应的结果
        :return: list of result
        """
        assert len(result_L) == len(no_L), '更新的任务参数数量不匹配!'
        doc_L = []
        if isinstance(self._db_tasks, pymongo.collection.Collection):
            modified_no_L = []
            for result, no in zip(result_L, no_L):
                result.pop('no', 0)  # 更新不含 no
                result = {'$set': self._numpy_to_base(result)}
                if self._db_tasks.update_many({'no': no}, result).modified_count:
                    modified_no_L.append(no)
            doc_L = self.que_tasks([{'$match': {'no': {'$in': modified_no_L}}}])
        else:
            results_L = []
            for result, no in zip(result_L, no_L):
                result.pop('no', 0)  # 更新不含 no
                results_L.append((self._numpy_to_base(result), Query()['no'] == no))
            try:
                doc_ids = self._db_tasks.update_multiple(results_L)
                for doc_id in doc_ids:
                    doc = self._db_tasks.get(doc_id=doc_id)
                    # 生成镜像文件夹
                    if doc['executed']:
                        db_path = f"{self.db_dir}/database/{doc['main_path']}"
                        if not os.path.exists(db_path):
                            os.makedirs(db_path)
                    doc_L.append(doc)
            except:  # 错误检查
                print('results_L:')
                pprint(results_L)
                raise
        return doc_L

    def output_table(self, path=None, cols_limit=100, col_front=('main_path', 'executed', 'priority'),
                     col_back=('no',), min_unique_prior=2, max_null_rate_prior=0.1, query=None):
        """
        将整个数据库的内容全部用tab表格\t的形式输出, 第一行是展开的表头(排序), 行顺序是tasks默认顺序
        如果一列除了空以外的值都一样将不会优先显示, 除非不到cols_limit补充在最后
        :param path: str or None; 表格输出的路径, None表示输出在数据库内
        :param cols_limit: int; 最多输出多少列
            多余的列会不输出(不断的展开最少数量的dict到不能展开,list会直接输出而不展开),只输出排序后的最后一列
            每个 self.result 的根参数都会输出来
        :param col_front: list or tuple; 手动放前面的键值, 剩下的顺序排序
            不在task中的属性会被忽略, 嵌入属性使用"分隔父子层次
        :param col_back: list or tuple; 手动放后面的键值, 剩下的顺序排序
            不在task中的属性会被忽略, 嵌入属性使用"分隔父子层次
        :param min_unique_prior: int; 如果一列除空以外的值总数<min_unique_prior将不会优先显示, 除非不到cols_limit补充在最后
        :param max_null_rate_prior: float; 如果一列空值百分比<=max_null_rate_prior将优先展开
        :param query: None or dict; 对要展示的任务先进行查询过滤, None 表示不过滤
        :return:
        """
        if not path:
            path = f'{self.db_dir}/all_task_table.txt'
        tasks = self.que_tasks(query) if query else self.tasks
        if len(tasks) == 0:  # 没有任务不输出, 防止最后 IndexError: list index out of range
            return None

        # 先一层层展开, 用"连接起dict的命名, 得到值dict
        def extend_f(content, x=None, root=''):
            if x is None:
                x = {}
            if isinstance(content, dict):
                for k, v in content.items():
                    extend_f(v, x, root + f'"{k}')
            else:
                x[root[1:]] = str(content)
            return x  # {'列名':值,..}

        col_content_D = {}  # {'列名':[],..}
        for i, task in enumerate(tasks):
            x = extend_f(task)
            # 先填充col_content_D中有的, 保证每列对应
            for k, v in col_content_D.items():
                if k in x:
                    v.append(x.pop(k))
                else:
                    v.append('')  # 没有的话填空
            # 填充col_content_D中没有的
            for k, v in x.items():
                col_content_D[k] = [''] * int(i) + [v]

        # max_unique_prior 修剪
        col_equality_D = {}  # col_content_D 格式
        for col, content_L in col_content_D.items():
            if len(set(content_L) | {''}) <= min_unique_prior:
                col_equality_D[col] = content_L
        [col_content_D.pop(col) for col in col_equality_D.keys()]
        # max_null_rate_prior 修剪
        col_content_D2 = {}  # col_content_D 格式
        for col, content_L in col_content_D.items():
            if content_L.count('') / len(content_L) > max_null_rate_prior:
                col_content_D2[col] = content_L
        [col_content_D.pop(col) for col in col_content_D2.keys()]

        def nest_f(s_L, nest_D, d_D=None, root=''):
            if d_D is None:
                d_D = nest_D
            root += f'"{s_L[0]}'
            root_ = root[1:]  # 去除第一个 "
            if root_ not in d_D:
                d_D[root_] = {}
            if len(s_L) > 1:
                nest_f(s_L[1:], nest_D, d_D[root_], root)

        # 依据值dict还原出嵌套字典
        nest_D = {}  # {'列名':{'列名':{..},..},..}
        nest_D2 = {}  # nest_D 格式
        for k in col_content_D.keys():
            nest_f(k.split('"'), nest_D)
        for k in col_content_D2.keys():
            nest_f(k.split('"'), nest_D2)
        col_content_D.update(col_content_D2)  # 此处合并 max_null_rate_prior 修剪

        # 依据嵌套字典控制展示数量, 层次遍历+排序
        cols_limit_1 = 0  # 已经限制的列
        partCol_content_D_L = []
        for partCol_content_D in [nest_D.copy(), nest_D2.copy()]:  # {'col':{..},..}
            if partCol_content_D:  # nest_D2 可能为 {}
                min_partCol_content = heapq.nlargest(1, partCol_content_D.items(),
                                                     key=lambda t: [-len(t[1]) if t[1] else -10 ** 100] + t[0].split(
                                                         '"'))[0]  # ('col',{..}), 最小非空值
                while len(partCol_content_D) + len(min_partCol_content[1]) - 1 <= cols_limit - cols_limit_1:
                    # 如果最小值已经无法展开
                    if len(min_partCol_content[1]) == 0:
                        break
                    partCol_content_D.pop(min_partCol_content[0])  # 出栈扩展最少数量那个
                    partCol_content_D.update(min_partCol_content[1])  # 加入最少数量那个
                    min_partCol_content = heapq.nlargest(1, partCol_content_D.items(),
                                                         key=lambda t: [-len(t[1]) if t[1] else -10 ** 100] + t[
                                                             0].split('"'))[0]  # ('col',{..}), 最小非空值
            cols_limit_1 += len(partCol_content_D)
            partCol_content_D_L.append(partCol_content_D)
        partCol_content_D = partCol_content_D_L[0].copy()
        partCol_content_D.update(partCol_content_D_L[1])  # 合并

        # col倒叙过滤, 尽量保留叶子节点, 去除上面展示数量以外的
        partCol_S = set(partCol_content_D)
        colNew_content_D = {}  # 过滤后将要输出的, 和 col_content_D 格式一样
        for col, content_L in sorted(col_content_D.items(), key=lambda t: t[0].split('"'), reverse=True):
            col_L = col.split('"')
            c = None
            for i in range(len(col_L), 0, -1):  # 从长到短遍历
                c = '"'.join(col_L[0:i])
                if c in partCol_S:  # 可以输出
                    break
                else:
                    c = None
            if c:
                colNew_content_D[col] = content_L
                partCol_S.remove(c)
            if len(partCol_S) == 0:
                break
        colNew_L = list(set(colNew_content_D) - set(col_front) - set(col_back))  # ['col',..]
        colNew_L.sort()
        colNew_L = [i for i in col_front if i in colNew_content_D] + colNew_L + \
                   [i for i in col_back if i in colNew_content_D]

        # 补充之前被 max_unique_prior 修剪的列, 如果 cols_limit 还没到的话加上
        col_equality_L = [i for i in list(col_front) + list(col_back) if i in col_equality_D.keys()]  # 剩余的手动列
        col_equality_L += sorted(set(col_equality_D) - set(col_equality_L))  # 剩余的所有相等列
        colNew_L += col_equality_L[0: max(0, cols_limit - len(colNew_L))]
        colNew_content_D.update(col_equality_D)  # 合并所有剩余相等的列

        # tab隔开col展示
        with open(path, 'w', encoding='utf8') as w:
            w.write('\t'.join(colNew_L) + '\n')
            for i in range(len(colNew_content_D[colNew_L[0]])):
                w.write(colNew_content_D[colNew_L[0]][i])
                for col in colNew_L[1:]:
                    w.write('\t' + colNew_content_D[col][i])
                w.write('\n')
        return path

    def run_tasks(self, **kwargs):
        """
        需要重载, 循环完成未完成的任务
        :return:
        """
        tasks = self.uncomplete_tasks
        完成任务 = 0
        # 对于每个任务
        while len(tasks) != 0:
            if len(tasks) != 0:
                task = tasks.pop(0)
            paras = copy.deepcopy(task['paras'])  # 后续可能需要修改
            # 结果过滤
            result = {}
            filter = task['filter']
            if not filter:  # 防止无参数输入错误
                filter = {'test': None}
            while self.filtrate_result(result, **filter):
                # 运行得到结果
                time_start = time.time()
                result = {
                    'executed': True,
                    'main_path': str(len(tasks)),
                    'machine': self.get_machine(),
                    'time_start': time_start,
                    'run_tasks_test': [{'1': [1, 2, 3, 4], '2': [2]}, {'3': [3], '4': [4]}, {'5': [5], '6': [6]}],
                }
            # 写入数据
            self.update_tasks([result], [task['no']])
            完成任务 += 1
            print('=' * 20, '本次任务结果:')
            pprint(result)
            print('=' * 20, f'已完成第{完成任务}个任务, 剩余{len(tasks)}个.')
            print()

    def stat_result(self, **kwargs):
        """
        可以重载, 统计结果
        :return:
        """
        if isinstance(self._db_tasks, pymongo.collection.Collection):
            complete_num = self._db_tasks.count_documents({'executed': True})
            uncomplete_num = self._db_tasks.count_documents({'executed': False})
        else:
            complete_num = self._db_tasks.count(eval(self._result_to_query({'executed': True})))
            uncomplete_num = self._db_tasks.count(eval(self._result_to_query({'executed': False})))
        return {
            'complete_num': complete_num,  # 已完成任务数
            'uncomplete_num': uncomplete_num,  # 未完成任务数
        }

    def filtrate_result(self, result, **kwargs):
        """
        需要重载, 对参数返回结果进行过滤, 如果结果不好就重新执行任务. 使用 api 建议用 no 寻找 filter
        :param result: dict;
        :param kwargs: 其他参数
        :return: bool; True 表示结果过滤掉
        """
        if not result:
            return True
        return False

    def clean(self):
        """
        清理主目录下非完成任务的文件夹, __开头不删除, 非文件夹不删除
        TaskDB: database 中有 main_path 缺失的完成任务会被重制为未完成任务, 并清除原文件夹
        :return:
        """
        tasks = self.que_tasks({'executed': True})
        path_S = {f"{self.db_dir}/" + t['main_path'].rstrip('/\\') for t in tasks}  # 每个已执行参数的主目录
        path_S |= {f'{self.db_dir}/database'}  # 镜像文件夹不删除
        # 删除多余路径数据
        n = 1
        for i, p in enumerate(os.listdir(self.db_dir)):
            p_ = p
            p = f"{self.db_dir}/{p}"
            if os.path.isdir(p) and p not in path_S and p_[:2] != '__':
                shutil.rmtree(p)
                print(f'删除多余路径数据({n}):', p)
                n += 1
        if not self.is_mongo:
            # 删除缺失镜像文件夹数据并重置任务
            n = 1
            valid_path = set()  # 有效的 main_path 用于清理镜像文件夹
            result_L = []
            no_L = []
            for i, t in enumerate(tasks):
                main_path = t['main_path'].rstrip('/\\')
                p = f"{self.db_dir}/{main_path}"
                dp = f"{self.db_dir}/database/{main_path}"
                if not os.path.exists(dp):
                    if os.path.isdir(p):
                        shutil.rmtree(p)  # 必须是目录
                    print(f'删除缺失镜像文件夹数据({n}):', p)
                    n += 1
                    result_L.append({'executed': False})
                    no_L.append(t['no'])
                else:
                    valid_path.add(dp)
            if result_L and no_L:
                print('重置缺失镜像文件夹任务...')
                print(len(self.update_tasks(result_L, no_L)), '个任务重置')
            # 删除多余镜像文件夹中的文件夹
            n = 1
            for i, p in enumerate(os.listdir(f'{self.db_dir}/database')):
                p = f"{self.db_dir}/database/{p}"
                if os.path.isdir(p) and p not in valid_path:
                    shutil.rmtree(p)
                    print(f'删除多余镜像文件夹中的文件夹({n}):', p)
                    n += 1
            self._db_tasks.clear_cache()

    def close(self):
        """
        关闭数据库
        :return:
        """
        self.clean()
        self._db.close()

    @staticmethod
    def test(db, mongo_url=None, mongo_db=None, mongo_co=None, new=True):
        obj = TaskDB(db, new=new, mongo_url=mongo_url, mongo_db=mongo_db, mongo_co=mongo_co, tiny_to_mongo=True)
        n = 6
        for i in range(n):
            print('增加任务:', obj.add_tasks([obj.result['paras']], priority_L=[i]))
        print()
        print('删除任务:')
        print(obj.del_tasks({'priority': n - 1}))
        print('运行任务:')
        obj.run_tasks()
        print('查询任务:')
        q_L = obj.que_tasks({'priority': 1, 'run_tasks_test': [20]})
        assert len(q_L) == 0
        print(q_L)
        if obj.is_mongo:
            q_L = obj.que_tasks([
                {'$match': {'priority': 1, 'run_tasks_test.1': 1}},
            ])
            print('aggregate:', q_L)
            assert q_L[-1]['priority'] == 1
        q_L = obj.que_tasks({'priority': 1, 'run_tasks_test': [{'1': [1, 2]}]})
        print(q_L)
        assert q_L[-1]['priority'] == 1
        q_L = obj.que_tasks({'paras': obj.result['paras']})
        print(q_L)
        # print(TaskDB._result_to_query({'paras': obj.result['paras']}, is_mongo=obj.is_mongo))
        print()
        print('更新任务:')
        print(obj.update_tasks([{'executed': False}], [q_L[0]['no']]))
        print(obj.update_tasks([
            {'executed': False}, {'executed': False}, {'test': 123}
        ], [
            q_L[1]['no'], q_L[2]['no'], q_L[-1]['no']
        ]))
        print()
        print('统计结果:', obj.stat_result())
        print()
        print('输出表格展示:')
        print(obj.output_table(query={'executed': False}))
        print(obj.output_table(path=f'{db}/all_task_table_14.txt', cols_limit=14))
        print(obj.output_table(path=f'{db}/all_task_table_17.txt', cols_limit=17))
        print()
        print('mongo_to_tiny:')
        print(obj.mongo_to_tiny())
        print('关闭数据库:')
        obj.close()


class MainPath:
    def __init__(self, main_path: str, root='.', new=True, unfinished='__unfinished'):
        """
        用于主目录的处理, 通过warp实现同一个文件夹下不会出现一摸一样的文件夹.
        :param main_path: str; m, 主目录, 不支持从根目录开始
        :param root: str; r, 主目录所在的目录, 支持 ~
        :param new: bool; 是否会创建未完成的包裹后的 main_path (即 rufm), 不会覆盖(倒也不会重复)
        :param unfinished: str; u, 未完成任务的路径. 注意 TaskDF.clean() 要不会清理这个目录
        """
        assert main_path[0] not in {'/', '\\', '~'}, 'main_path 不支持从根目录开始: ' + main_path
        assert unfinished[0] not in {'/', '\\', '~'}, 'unfinished 不支持从根目录开始: ' + unfinished
        # 根目录
        self._root = os.path.expanduser(root.rstrip('/\\'))
        # 未完成的目录
        self._unfinished = unfinished.rstrip('/\\')
        # main_path 的随机生成的父目录名
        self._father = f"{datetime.datetime.now().strftime('%Y%d%m_%H%M%S')}_{random.random()}"  # 不能重复
        # main_path 名
        self._origin = main_path.rstrip('/\\')
        # rufm: 标准初始路径
        self._all_path = os.path.join(self._root, self._unfinished, self._father, self._origin)  # rufm
        if new and not os.path.isdir(self._all_path):
            os.makedirs(self._all_path)

    def __getitem__(self, brief: str):
        """
        :param brief: str; 将不同表示的路径串联起来, 最后没有 / 符号, 标准初始路径: rufm
            r: root; u: unfinished; f: father; m: origin
        :return:
        """
        path = ''
        for s in brief:
            if s == 'r':
                path = os.path.join(path, self._root)
            elif s == 'u':
                path = os.path.join(path, self._unfinished)
            elif s == 'f':
                path = os.path.join(path, self._father)
            elif s == 'm':
                path = os.path.join(path, self._origin)
            else:
                raise NameError('brief 只能包括 "rufm" 中的一个: ' + brief)
        return path


class TaskDBapi:
    @staticmethod
    def app_run(db_dirs: list, port=19999, log_path=f'log/TaskDBapi.app_run.log', mongo_url=None, passwd=None,
                **kwargs):
        """
        将数据库做成 http api 用于分布式机器任务分配. 任务越多占用内存越多, 开始会获取全库到内存
        :param db_dirs: [数据库目录1,..]
        :param port: int; 访问端口
        :param log_path: str; 日志输出地址
        :param mongo_url: None or str or [url,..]; 不是list会自动扩展为长度为len(db_dirs)的list, 具体含义参见 TaskDB.__init__()
        :param passwd: str or None; 用于api密码校验,使用https才有意义. 为空表示不校验
        :return:
        """
        if not db_dirs:
            return None
        db_obj_D = {}  # {dir:TaskDB(),..}; 所有数据库
        db_obj_num_D = {}  # {dir:总任务数量,..}; 防止每次获取总任务都需要 self.tasks
        db_no_tasks_D = {}  # {dir:{no:task,..},..}; 所有数据库的未完成任务
        db_no8num_D = {}  # {dir:[[[no,分配次数],..],..],..}; 未完成的no序列, 一个优先级=[[no,分配次数],..]
        if not isinstance(mongo_url, list):
            mongo_url = [mongo_url] * len(db_dirs)
        assert len(db_dirs) == len(mongo_url), '数据库参数数量不匹配!'

        for d, url in zip(db_dirs, mongo_url):
            db_no_tasks_D[d] = {}  # {no:task,..}
            db_no8num_D[d] = []  # [[[no,分配次数],..],..]; 按这个顺序分配任务
            db_obj_D[d] = TaskDB(d, mongo_url=url)
            db_obj_num_D[d] = len(db_obj_D[d].tasks)
            priority = ...
            for task in db_obj_D[d].uncomplete_tasks:
                no = task['no']
                db_no_tasks_D[d][no] = task
                # 优先级阶梯
                if priority != task['priority']:
                    db_no8num_D[d].append([])
                    priority = task['priority']
                db_no8num_D[d][-1].append([no, 0])
        api_access_times = [0]  # api访问次数
        logger = get_logger(log_path)

        # 获取任务方法
        def get_one_task(db, query):
            """
            获取一个任务, 获取任务考虑优先级问题
            :param db: post_dict['db']
            :param query: dict or list; 用于que_tasks的查询语句, 用于过滤, executed==False 会自动加入
            :return:
            """
            task = {}
            if len(db_no8num_D[db]) == 0:
                describe = '所有任务已完成'
                status = 1
            else:
                # 查询过滤
                if query:
                    if isinstance(query, dict):
                        query.update({'executed': False})
                    elif isinstance(query, list):
                        query = [{'$match': {'executed': False}}] + query
                    else:
                        raise NameError('query 类型错误, 不是 dict 或 list:', type(query))
                    no_S = {i['no'] for i in db_obj_D[db].que_tasks(query)}
                else:
                    no_S = {db_no8num_D[db][0][0][0]}  # 直接放入第一个编号
                # 获取任务编号和任务
                ii = None
                for i, (no, assigned_num) in enumerate(db_no8num_D[db][0]):
                    if no in no_S:
                        ii = i
                        break
                if ii is None:
                    if no_S:
                        describe = '需要的任务优先级过低,请等待高优先级任务完成!'
                        status = 2  # 这个值有 request_api 依赖, 注意修改
                    else:
                        describe = '没有满足查询要求的任务!'
                        status = 3
                else:
                    no, assigned_num = db_no8num_D[db][0][ii]
                    del db_no8num_D[db][0][ii]
                    db_no8num_D[db][0].append([no, assigned_num + 1])  # 分配的放在队列最后
                    task = db_no_tasks_D[db][no]  # 获取任务
                    describe = f'获取任务成功{"(query)" if query else ""}, 该任务已被分配过{assigned_num}次'
                    status = 4
            return task, describe, status  # status != 0

        # 启动
        app = Flask(__name__)
        lock = threading.RLock()

        @app.route('/api', methods=['POST'])
        def api():
            """
            status 含义在代码中查看
            request_data: dict
                type: 必填, 2种请求模式 request/complete
                    request: 请求任务
                    complete: 完成任务
                db: 必填, 启动api时使用的数据库路径(db_dir)
                query: request, 请求任务的过滤条件
                no: complete, 完成任务的编号
                result: complete, 完成任务的结果
                filter: complete, 是否过滤完成结果, 1表示过滤, 0表示不过滤
                passwd: 访问密码参数, 可选
            :return:
            """
            start_queue = time.time()
            lock.acquire()  # 加锁
            start = time.time()
            api_access_times[0] += 1
            print()
            response = {'task': {}, 'type': 'normal', 'error': '', 'message': '', 'status': 0}
            out_request = None
            try:
                post_dict = dict(request.form)  # type: dict
                if passwd:
                    time.sleep(0.1)  # 防止频繁尝试
                    assert 'passwd' in post_dict and post_dict['passwd'] == passwd, '密码错误!'
                assert 'type' in post_dict, '缺少 type 请求类型(request/complete)!'
                assert 'db' in post_dict, '缺少 db 启动api时使用的数据库路径!'
                try:
                    post_dict['query'] = ast.literal_eval(post_dict.setdefault('query', 'None'))
                except:
                    raise NameError('query 需要 str 形式的 dict 或 list !')
                post_dict['filter'] = int(post_dict.setdefault('filter', 1))
                db = post_dict['db']
                # 请求任务
                if post_dict['type'] == 'request':
                    task, describe, status = get_one_task(db, post_dict['query'])[:3]
                    for k, v in task.items():  # 防止 mongodb 的 ObjectId 无法 json.dumps
                        if isinstance(v, ObjectId):
                            task[k] = str(v)
                    response['task'] = task
                    response['message'] = describe
                    response['status'] = status
                # 完成任务
                elif post_dict['type'] == 'complete':
                    assert 'no' in post_dict, '缺少 no 任务编号!'
                    assert 'result' in post_dict, '缺少 result 任务结果!'
                    try:
                        result = post_dict['result'] = ast.literal_eval(post_dict['result'])  # str转类型
                    except:
                        raise NameError('result 需要 str 形式的 dict !')
                    result['executed'] = True  # 表示执行完成
                    # 获取任务优先级位置, 完成任务不考虑优先级
                    priority = ii = None  # 优先级, 以及优先级中的位置
                    for i, no_num_L in enumerate(db_no8num_D[db]):
                        for j, (no, assigned_num) in enumerate(no_num_L):
                            if post_dict['no'] == no:
                                priority = i
                                ii = j
                                break
                        if priority is not None:
                            break
                    # 是否是未完成
                    if priority is not None:
                        no, assigned_num = db_no8num_D[db][priority][ii]
                        # 过滤
                        if post_dict['filter'] and db_obj_D[db].filtrate_result(result, no=no, api=True):
                            response['message'] = f'完成任务失败-没有通过 filtrate_result 检测!'
                            response['status'] = -1
                        else:
                            # 更新任务
                            db_obj_D[db].update_tasks([result], [no])
                            # 去除完成的任务
                            del db_no8num_D[db][priority][ii]
                            if len(db_no8num_D[db][priority]) == 0:
                                del db_no8num_D[db][priority]
                            response['message'] = f'完成一个任务(优先级第{priority}层,被分配过{assigned_num}次)'
                            response['status'] = 1  # >=1 表示任务完成
                    else:
                        response['message'] = f'完成任务失败-不是未完成的no'
                        response['status'] = -2
                # 错误 type 参数
                else:
                    raise NameError('type 参数错误!')
                out_request = f'请求信息:\n' + pformat(post_dict) + \
                              f"\n数据库({db})未完成/总任务: {len(sum(db_no8num_D[db], []))}/{db_obj_num_D[db]}; " \
                              f"未完成任务的总已分配次数: {sum([i[1] for i in sum(db_no8num_D[db], [])])}; \n" \
                              f"message: {response['message']}"
                logger.critical(out_request + '\n')  # 日志
            except Exception as e:
                error = traceback.format_exc()
                print(error, end='')
                logger.critical('error\n' + error)
                response['type'] = 'error'
                response['message'] = 'error'
                e = str(e).replace("\n", " ")
                response['error'] = 'error'f'{type(e)}: {e}'
            out_response = f'返回信息:\n' + pformat(response) + \
                           f"\napi耗时: {round(time.time() - start, 4)}s; " \
                           f"排队耗时: {round(abs(start_queue - start), 4)}s; " \
                           f"api已访问次数: {api_access_times[0]}"
            print(out_response)
            logger.critical(out_response + '\n')  # 日志
            if out_request:  # 请求结果在前端输出放在后面, 方便查看
                print(out_request)
            lock.release()  # 去锁
            response = json.dumps(response, ensure_ascii=False, indent=2)
            return response

        print('接口可运行在:', f'http://{TaskDB.get_machine()["ip"]}:{port}/api')
        app.run(host='0.0.0.0', port=port, debug=False)

    @staticmethod
    def request_api(request_data: dict, url='http://127.0.0.1:19999', sleep=0.5, try_times=5, mp: MainPath = None,
                    wait_priority_sleep=300, wait_priority_times=10 ** 10, **kwargs):
        """
        app_run.api() 对应的客户端, 任务之间的 main_path 不能相同
        :param request_data: dict; 与 app_run.api() 中的 request_data 一致, request/complete
        :param url: str; 获取数据的api接口, 不需要router
        :param sleep: float or int; 访问间隔, 防止过于频繁, 单位秒
        :param try_times: int; 访问几次失败就返回失败
        :param mp: MainPath() or None; 用于将完成的文件移动到子文件夹, MainPath()且是已完成任务才会移动
            main_path 会从 mp['ruf'] 移动到 mp['r'], 然后删除 mp['ruf']
        :param wait_priority_sleep: float or int; request 请求的优先级任务过低的等待时间, 单位秒
        :param wait_priority_times: int; wait_priority_sleep 的最大等待次数
        :return:
        """
        url = url.strip('/') + '/api'
        response = {}
        for i in range(try_times):
            time.sleep(sleep)
            try:
                response = json.loads(requests.post(url, data=request_data).text)
                times = 1
                while 'type' in request_data and request_data['type'] == 'request' and response['status'] == 2:
                    print(response['message'], f'等待({times}次/{wait_priority_sleep}秒)...')
                    times += 1
                    if times > wait_priority_times:
                        print('放弃, 不再等待!')
                        break
                    time.sleep(wait_priority_sleep)
                    response = json.loads(requests.post(url, data=request_data).text)
                break
            except:
                print(f'request_api 失败{i + 1}次:')
                traceback.print_exc()
                time.sleep(sleep)
        # completed_move
        if mp and 'status' in response and response['status'] >= 1 and request_data['type'] == 'complete':
            result = ast.literal_eval(request_data['result'])
            assert 'main_path' in result, '请求完成的结果中没有主目录 main_path: ' + str(result)
            main_path = result['main_path'].rstrip('/\\')
            assert main_path == mp['m'], f"请求完成结果中的 main_path 与 mp['m'] 不同: {main_path} != {mp['m']}"
            assert os.path.isdir(mp['rufm']), '没有生成未完成的包裹主目录 main_path: ' + mp['rufm']
            assert not os.path.isdir(mp['rum']), '生成了无包裹的主目录 main_path: ' + mp['rum']
            # 移动任务目录
            if not os.path.exists(mp['rm']):
                shutil.move(mp['rufm'], mp['rm'])
                shutil.rmtree(mp['ruf'])
            else:
                with open(f"{mp['ruf']}/complete.txt", 'w', encoding='utf8') as w:
                    w.write('任务已被完成(main_path重复), 不再移动 main_path !')  # 写入文件提示这是完成而没移动的文件
                print('任务已被完成(main_path重复), 不再移动 main_path !')
        return response

    @staticmethod
    def test(db, mongo_url=None, mongo_db=None, mongo_co=None):
        """
        连续运行两次分别测试服务端和客户端
        :return:
        """
        port = 19998
        url = f'http://127.0.0.1:{port}'
        if not TaskDBapi.request_api({}, try_times=1, url=url):  # 是否有服务器存在
            TaskDB.test(db, mongo_url, mongo_db, mongo_co)  # 注意这里运行两次会覆盖TaskDB
            TaskDBapi.app_run(db_dirs=[db], port=port, mongo_url=mongo_url)
        else:
            # 查询请求
            TaskDBapi.request_api(
                request_data={'type': 'request', 'db': db, 'query': "{'priority': 1}"},
                url=url, wait_priority_sleep=5, wait_priority_times=1)
            # 普通请求
            TaskDBapi.request_api(request_data={'type': 'request', 'db': db}, url=url)
            response = TaskDBapi.request_api(request_data={'type': 'request', 'db': db}, url=url)
            # 循环请求完成, 还有一种完成高优先级任务无测试
            while response['task']:
                TaskDBapi.request_api(
                    request_data={'type': 'complete', 'db': db, 'no': response['task']['no'],
                                  'result': "{'test': 123}"}, url=url)
                response = TaskDBapi.request_api(request_data={'type': 'request', 'db': db}, url=url)


if __name__ == '__main__':
    mongo_url = 'mongodb://test_owner:cRtJWhHocN8HTcOL@127.0.0.1:27017/',
    # mongo_url = None  # 这行注释掉就是 mongodb 模式
    mongo_db = 'test'
    mongo_co = 'test'

    TaskDBapi.test(db='test_TaskDB', mongo_url=mongo_url, mongo_db=mongo_db, mongo_co=mongo_co)
    # TaskDB.test(db='test_TaskDB', mongo_url=mongo_url, mongo_db=mongo_db, mongo_co=mongo_co, new=False)
