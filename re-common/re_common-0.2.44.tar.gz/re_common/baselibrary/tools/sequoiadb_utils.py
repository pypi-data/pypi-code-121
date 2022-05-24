from typing import Union

from pysequoiadb import client
from pysequoiadb.collection import INSERT_FLG_DEFAULT
from pysequoiadb.lob import LOB_READ, LOB_WRITE


class SequoiadbUtils(object):

    def __init__(self):
        self.db_data = None
        self.db = None
        self.cs = None
        self.cl = None
        self.list_hosts = None

    def set_db_data(self, db_data: dict):
        self.db_data = db_data
        return self

    def set_list_hosts(self, list_hosts):
        self.list_hosts = list_hosts
        return self

    def build(self):
        self.link_db()
        self.link_col()
        return self

    def set_cl(self, cl):
        self.cl = cl

    def link_db(self):
        """
        初始化 host, port, user, password ，连接
        """
        host = self.db_data.get("host", "")
        port = self.db_data.get("port", "")
        user = self.db_data.get("user", "")
        password = self.db_data.get("password", "")
        try:
            self.db = client(host=host, service=port, user=user, psw=password)
            if self.list_hosts:
                # self.list_hosts = [
                #     {'host': '192.168.31.21', 'service': '11810'},
                #     {'host': '192.168.31.22', 'service': '11810'},
                #     {'host': '192.168.31.23', 'service': '11810'},
                #     {'host': '192.168.31.24', 'service': '11810'},
                #     {'host': '192.168.31.25', 'service': '11810'},
                #     {'host': '192.168.31.26', 'service': '11810'},
                #     {'host': '192.168.31.27', 'service': '11810'},
                #     {'host': '192.168.31.219', 'service': '11810'},
                #     {'host': '192.168.31.208', 'service': '11810'}
                # ]
                self.db.connect_to_hosts(self.list_hosts, user=user, psw=password)
            return self.db
        except Exception as e:
            raise e

    def link_col(self):
        collection_space_name = self.db_data.get("collection_space_name", "")
        collection_name = self.db_data.get("collection_name", "")
        is_create = self.db_data.get("is_create", "false")
        try:
            self.cl = self.db.get_collection("{}.{}".format(collection_space_name, collection_name))
            return self.cl
        except:
            print('集合空间或者集合不存在')
            if is_create == "true":
                try:
                    self.cs = self.db.create_collection_space(collection_space_name)
                    print('创建集合空间  ', collection_space_name)
                except:
                    self.cs = self.db.get_collection_space(collection_space_name)
                try:
                    self.cl = self.cs.create_collection(collection_name)
                    print('创建集合空间  ', collection_name)
                    return self.cl
                except:
                    self.cl = self.cs.get_collection(collection_name)

    def insert(self, record: dict, cl=None):
        """
        插入数据
        :return A ObjectId object of record inserted. eg: { '_id': ObjectId('5d5149ade3071dce3692e93b') }
        """
        if cl is None:
            cl = self.cl
        return cl.insert(record)

    def replace_one(self, doc, cl=None, **kwargs):
        """
        更新数据
        rule:  更新数据
        kwargs:
            condition: 匹配规则
            hint: https://doc.sequoiadb.com/cn/SequoiaDB-cat_id-1432190835-edition_id-300
            flags: 默认为0  UPDATE_FLG_KEEP_SHARDINGKEY 更新规则中的分片键在执行时没有被过滤更新或插入。
            如果不给flags,不保留更新规则中的分区键字段，只更新非分区键字段。否则 保留更新规则中的分区键字段。
            指定 flags 参数：保留更新规则中的分区键字段。因为目前不支持更新分区键，所以会报错。
        """
        if cl is None:
            cl = self.cl
        rule = {"$replace": doc}
        return cl.update(rule, **kwargs)

    def bulk_insert(self, flag: int, records: Union[list, tuple], cl=None):
        """
        插入多条数据
        :param flag:
         INSERT_FLG_DEFAULT : 当设置INSERT_FLG_DEFAULT时，当记录命中索引时，数据库将停止插入键重复错误。，插入正常也不会返回id
         INSERT_FLG_CONTONDUP : 如果记录命中索引键重复错误，数据库将跳过它
         INSERT_FLG_RETURN_OID : 返回记录中“_id”字段的值。，如果有重复会报错
         INSERT_FLG_REPLACEONDUP : 如果记录命中索引键重复错误，数据库将用插入新记录，然后继续插入。
        :param records:
        :return:
        当flag不等于INSERT_FLG_RETURN_OID时，将返回一个空字典, eg: { }.
        eg: { '_id': [ObjectId('5d514a25c764c60acb58de38'), ObjectId('5d514a25c764c60acb58de39')]}
        """
        if cl is None:
            cl = self.cl
        return cl.bulk_insert(flag, records)

    def insert_with_flag(self, record, flag=INSERT_FLG_DEFAULT, cl=None):
        """
        插入数据，并可以选择flags
        和 bulk_insert 一样的标志，这样可以实现replace
        :param record:
        :param flag:
        :return:
        """
        if cl is None:
            cl = self.cl
        return cl.insert_with_flag(record, flag)

    def delete(self, cl=None, **kwargs):
        """
        删除数据
        condition: 匹配规则后，删除文档,如果没有提供,删除所有文档
        在 https://doc.sequoiadb.com/cn/sequoiadb-cat_id-1432190843-edition_id-300对hint
        hint: 指定访问计划（v3.0后意义不大）
        """
        if cl is None:
            cl = self.cl
        return cl.delete(**kwargs)

    def update(self, rule: dict, cl=None, **kwargs):
        """
        更新数据
        rule:  更新数据
        kwargs:
            condition: 匹配规则
            hint: https://doc.sequoiadb.com/cn/SequoiaDB-cat_id-1432190835-edition_id-300
            flags: 默认为0  UPDATE_FLG_KEEP_SHARDINGKEY 更新规则中的分片键在执行时没有被过滤更新或插入。
            如果不给flags,不保留更新规则中的分区键字段，只更新非分区键字段。否则 保留更新规则中的分区键字段。
            指定 flags 参数：保留更新规则中的分区键字段。因为目前不支持更新分区键，所以会报错。
        """
        if cl is None:
            cl = self.cl
        return cl.update(rule, **kwargs)

    def upsert(self, rule, cl=None, **kwargs):
        """
        该函数用于更新集合记录。upsert 方法跟 update 方法都是对记录进行更新，不同的是当使用 cond 参数在集合中匹配不到记录时，update 不做任何操作，而 upsert 方法会做一次插入操作
        https://doc.sequoiadb.com/cn/sequoiadb-cat_id-1432190848-edition_id-500
        :param rule: 更新规则
        :param kwargs: condition: 条件
                        hint: 指定索引
                        setOnInsert： 在做插入操作时向插入的记录中追加字段。
                        flags：UPDATE_FLG_KEEP_SHARDINGKEY 默认不给
        :return:
        """
        if cl is None:
            cl = self.cl
        cl.upsert(rule, **kwargs)

    def query(
            self,
            condition: dict = None,
            selector: dict = None,
            order_by: dict = None,
            hint: dict = None,
            num_to_skip: int = 0,
            num_to_return: int = -1,
            flags: int = 0,
            cl=None):
        """
        https://doc.sequoiadb.com/cn/sequoiadb-cat_id-1552489127-edition_id-500
        查询数据
        condition:为空时，查询所有记录；不为空时，查询符合条件记录。如：{"age":{"$gt":30}}。关于匹配条件的使用，可参考匹配符
        selector:为空时，返回记录的所有字段；如果指定的字段名记录中不存在，则按用户设定的内容原样返回。如：{"name":"","age":"","addr":""}。字段值为空字符串即可，数据库只关心字段名。关于选择条件的使用，可参考选择符。
        order_by:指定结果集按指定字段名排序的情况。字段名的值为1或者-1，如：{"name":1,"age":-1}。1代表升序；-1代表降序。 如果不设定 sort 则表示不对结果集做排序。
        hint:指定查询使用索引的情况。字段名可以为任意不重复的字符串，数据库只关心字段值。
        num_to_skip:自定义从结果集哪条记录开始返回。默认值为0，表示从第一条记录开始返回。
        num_to_return：自定义返回结果集的记录条数。默认值为-1，表示返回从skipNum位置开始到结果集结束位置的所有记录。
        flags： QUERY_FLG_WITH_RETURNDATA:强制使用指定的提示进行查询，如果数据库没有提示分配的索引，则查询失败
                query_flg_parallelall:启用并行子查询，每个子查询将完成扫描数据的不同部分
                QUERY_FLG_FORCE_HINT:一般情况下，直到游标从数据库获取数据，查询才会返回数据，当添加此标志时，在查询响应中返回数据，将会更加高性能
                QUERY_PREPARE_MORE:启用查询时准备更多数据
                QUERY_FLG_FOR_UPDATE:当事务被打开且事务隔离级别为“RC”时，事务锁将不会在事务提交或回滚之前释放。
        """
        if condition is None:
            condition = {}
        if selector is None:
            selector = {}
        if order_by is None:
            order_by = {}
        if hint is None:
            hint = {}
        if cl is None:
            cl = self.cl
        return cl.query(condition=condition,
                        selector=selector,
                        order_by=order_by,
                        hint=hint,
                        num_to_skip=num_to_skip,
                        num_to_return=num_to_return,
                        flags=flags)
        # data_list = list()
        # while 1:
        #     try:
        #         result = results.next()
        #         data_list.append(result)
        #     except:
        #         break
        # return str(data_list)

    def query_and_update(self, update, cl=None, **kwargs):
        """

        :param update:  更新的规则
        :param kwargs: 查询条件，和上面查询一样多一个参数
                return_new bool 当为True时，返回更新后的文档，而不是原始文档
        :return: 返回查询的结果
        """
        if cl is None:
            cl = self.cl
        return cl.query_and_update(update, **kwargs)

    def query_and_remove(self, cl=None, **kwargs):
        """
        查询删除
        条件和查询完全一样
        :param kwargs:
        :return: 返回查询的结果
        """
        if cl is None:
            cl = self.cl
        return cl.query_and_remove(**kwargs)

    def save(self, doc, cl=None):
        """
        存在更新，不存在插入
        :param doc:
        :return:
        """
        if cl is None:
            cl = self.cl
        return cl.save(doc)

    def create_lob(self, oid=None, cl=None):
        """
        相当于一个空间
        :param oid: bson.ObjectId  指定要创建的lob的oid，如果为None，则自动生成oid
        :return:  一个objectid
        """
        if cl is None:
            cl = self.cl
        return cl.create_lob(oid=oid)

    def create_lob_id(self, timestamp=None, cl=None):
        """
        创建lob id
        :param timestamp: 用于于生成lob id，如果为None则由服务器生成时间戳。
                            格式:YYYY-MM-DD-HH.mm.ss。如:“2019-07-23 18.04.07”
        :return: lob的一个ObjectId对象。
        """
        if cl is None:
            cl = self.cl
        return cl.create_lob_id(timestamp=timestamp)

    def open_lob(self, oid, mode=LOB_READ, cl=None):
        """
        打开指定的lob进行读写
        :param oid: str/bson.ObjectId    指定的oid
        :param mode:
        int                  The open mode:
                                         lob.LOB_READ for reading.
                                         lob.LOB_WRITE for writing.
                                         lob.LOB_SHARE_READ for share reading.
                                         lob.LOB_SHARE_READ | lob.LOB_WRITE for both reading and writing.

        :return: a lob object
        """
        if cl is None:
            cl = self.cl
        return cl.open_lob(oid, mode)

    def get_lob(self, oid, cl=None):
        """
        获取指定的lob
        :param oid:  str/bson.ObjectId    The specified oid
        :return:  a lob object
        """
        if cl is None:
            cl = self.cl
        return cl.get_lob(oid)

    def remove_lob(self, oid, cl=None):
        """
        删除lob
        :param oid:  str/bson.ObjectId    The oid of the lob to be remove.
        :return:
        """
        if cl is None:
            cl = self.cl
        cl.remove_lob(oid)

    def truncate_lob(self, oid, length, cl=None):
        """截断lob

        Parameters:
           Name     Type                 Info:
           oid      str/bson.ObjectId    The oid of the lob to be truncated.
           length   int/long             The truncate length
        Exceptions:
           pysequoiadb.error.SDBBaseError
        """
        if cl is None:
            cl = self.cl
        cl.truncate_lob(oid, length)

    def list_lobs(self, cl=None, **kwargs):
        """
        lob 列表
        :param kwargs:
        Name              Type     Info:
           - condition       dict     The matching rule, return all the lob if not provided.
           - selected        dict     The selective rule, return the whole infomation if not provided.
           - order_by        dict     The ordered rule, result set is unordered if not provided.
           - hint            dict     Specified options. eg. {"ListPieces": 1} means get the detail piece info of lobs.
           - num_to_skip     long     Skip the first numToSkip lob, default is 0.
           - num_to_Return   long     Only return numToReturn lob, default is -1 for returning all results.

        :return: a cursor object of query
        """
        if cl is None:
            cl = self.cl
        return cl.list_lobs(**kwargs)

    def lob_insert(self, record: str, cl=None):
        """
        插入lob数据,输入字符串
        """
        if cl is None:
            cl = self.cl
        try:
            lob_oid = cl.create_lob_id()
            lob_obj = cl.create_lob(lob_oid)
            lob_obj.write(record, len(record))
            lob_obj.close()
            return str(lob_oid)
        except Exception as e:
            raise e

    def replace_lob(self, record: str, lob_oid: str, cl=None):
        """
        插入lob数据,输入字符串
        """
        if cl is None:
            cl = self.cl
        try:
            lob_obj = cl.open_lob(lob_oid, mode=LOB_WRITE)
            lob_obj.write(record, len(record))
            lob_obj.close()
            return str(lob_oid)
        except Exception as e:
            raise e

    def lob_insert_for_file(self, filepath: str):
        pass

    def lob_query(self, oid, cl=None):
        """
        查询lob数据
        """
        if cl is None:
            cl = self.cl
        lob_file = cl.open_lob(oid)
        return str(lob_file.read(lob_file.get_size()), encoding='utf-8')

    def close(self):
        self.db.disconnect()


def get_col(sdb_util: SequoiadbUtils, collection_space_name, collection_name):
    cl = sdb_util.db.get_collection("{}.{}".format(collection_space_name, collection_name))
    return cl
