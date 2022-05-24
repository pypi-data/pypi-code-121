import asyncio
import gzip
import json

from re_common.baselibrary.utils.basefile import BaseFile
from re_common.baselibrary.utils.basegzip import BaseGzip
from re_common.baselibrary.utils.basemotor import BaseMotor


class Configs(object):

    def __init__(self):
        self.mgdb_conn_motor = "mongodb://cjrw:vipdatacenter@192.168.31.243:32920,192.168.31.206:32920,192.168.31.208:32920/?authSource=htmljson"
        self.mgdb_db = "htmljson"
        self.mgdb_col = "other"
        self.filepath = r"F:\fun3\up\detail\mbalib.big_json.gz"
        self.query = {}
        self.feild = None
        self.one_file_num = 100000


class MongoToFile(object):
    def __init__(self, conf):
        self.conf = conf
        self.file_open = None
        self.i = 0

    def init_conn_mongodb(self):
        self.bs = BaseMotor()
        self.bs.AsyncIOMotorClient(
            self.conf.mgdb_conn_motor,
            self.conf.mgdb_db)
        self.bs.get_col(self.conf.mgdb_col)

    def open_file(self):
        i = BaseGzip.get_gz_line_num(self.conf.filepath)
        if i >= self.conf.one_file_num:
            self.conf.filepath = BaseFile.get_new_filename(self.conf.filepath)
        self.file_open = gzip.open(self.conf.filepath, "wb")

    def close_file(self):
        self.file_open.close()

    def asyncio_run(self):
        asyncio.get_event_loop().run_until_complete(
            self.bs.find(self.dic_deal, self.conf.query, self.conf.feild))
        self.close_file()

    def hook_doc(self, doc):
        return doc

    async def dic_deal(self, doc):
        doc = self.hook_doc(doc)
        line = json.dumps(doc, ensure_ascii=False) + '\n'
        lines = line.encode()
        self.file_open.write(lines)
        self.i = self.i + 1
        print(self.i)
        if self.i >= self.conf.one_file_num:
            self.close_file()
            self.conf.filepath = BaseFile.get_new_filename(self.conf.filepath)
            self.open_file()
            self.i = 0
