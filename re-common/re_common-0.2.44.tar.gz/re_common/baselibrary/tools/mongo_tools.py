import time

from re_common.baselibrary.utils.basemotor import BaseMotor
from re_common.baselibrary.utils.basepymongo import BasePyMongo


class MongoTools(object):
    def __init__(self, conn_str, db_name, col):
        self.conn_str = conn_str
        self.db_name = db_name
        self.col = col
        self.bs_conn = None

    def conn_mongo_base(self):
        self.bs_conn = BasePyMongo(self.conn_str)
        self.bs_conn.use_db(self.db_name)
        self.bs_conn.create_col(self.col)

    def conn_mongo_motor(self):
        self.bs_conn = BaseMotor()
        self.bs_conn.AsyncIOMotorClient(self.conn_str, self.db_name)
        self.bs_conn.get_col(self.col)

    def get_first_id(self, query):
        for item in self.bs_conn.find({"sub_db_id": "00075", "_id": {"$lt": ""}},
                                      {"_id": 1}).skip(0).limit(1):
            return item["_id"]

    def get_ids(self, ids, query):
        count = 0
        while True:
            lists = []
            query_temp = query.update({"_id": {"$gt": ids}})
            for i in self.bs_conn.find(query_temp, {"_id": 1}).sort([("_id", 1)]).limit(1000000):
                count = count + 1
                ids = i["_id"]
                lists.append((i["_id"]))
                if len(lists) % 10000 == 1:
                    print(len(lists))


if __name__ == "__main__":
    # mt = MongoTools(
    #     conn_str="mongodb://datahouse:vipdatacenter@192.168.31.243:32920/data_warehouse.base_obj_meta_a?authSource=data_warehouse",
    #     db_name="data_warehouse", col="base_obj_meta_a")
    mt = MongoTools(
        conn_str="mongodb://datahouse:vipdatacenter@192.168.31.208:32920,192.168.31.206:32920,192.168.31.243:32920/data_warehouse.base_obj_meta_a?authSource=data_warehouse",
        db_name="data_warehouse", col="base_obj_meta_a")
    mt.conn_mongo_base()
    print(mt.get_first_id({"sub_db_id": "00075"}))
