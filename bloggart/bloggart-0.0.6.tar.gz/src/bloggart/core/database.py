import tornado.web
import sqlite3
import json
import os

# TODO 并发性能问题
# sqlite3.connect()
# 当一个数据库被多个连接访问，且其中一个修改了数据库，此时 SQLite 数据库被锁定，直到事务提交。
# timeout 参数表示连接等待锁定的持续时间，直到发生异常断开连接。timeout 参数默认是 5.0（5 秒）。

DATABASE = ''
DATABASE_DQL_BASEURI = 'dql'
DATABASE_DCL_BASEURI = 'dcl'


def _ddl(sql):
    return

# dql不需要commit
def _dql(sql):
    print("_dql", sql)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    cursor = c.execute(sql)
    result = list(cursor)
    # for row in cursor:
    #     print "ID = ", row[0]
    #     print "NAME = ", row[1]
    #     print "ADDRESS = ", row[2]
    #     print "SALARY = ", row[3], "\n"
    conn.close()
    print(result)
    return result
    

class DQLHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        print(db)
        self.db = db

    def post(self):
        self.set_header("Content-Type", "text/plain")
        # curl -X POST http://localhost:8888/dql -d '{"sql":"SELECT * FROM BLOG"}'
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        print(param)
        result = _dql(param['sql'])
        self.write(json.dumps(result, ensure_ascii=False))


def _dcl(sql):
    print("_dcl", sql)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    print ("数据库打开成功")
    cursor = c.execute(sql)
    print(cursor.fetchall())
    result = list(cursor)
    conn.commit()
    print ("数据插入成功")
    conn.close()
    print(result)
    return True

class DCLHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        print(db)
        self.db = db

    def post(self):
        self.set_header("Content-Type", "text/plain")
        # curl -X POST http://localhost:8888/bloggart/dcl -d '{"sql":"INSERT INTO BLOG (DATETIME,NAME,MEMO,HEADIMG,LINK,CLASS) VALUES (\'7\', \'8\', \'9\', \'10\', \'11\', \'12\');"}'
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        print(param)
        result = _dcl(param['sql'])
        self.write(json.dumps(result, ensure_ascii=False))

def init(sqlpath = ""):
    print("loading sql file from:", sqlpath)
    conn = sqlite3.connect(DATABASE)
    conn.executescript(open(sqlpath,'r').read())
    conn.commit()
    print ("数据插入成功")
    conn.close()
    return

def Handle(config):
    global DATABASE
    DATABASE = config['path']

    if 'init' in config:
        init(config['init'])

    urls = [
        # 我们修改了原先的映射规则，将默认页请求映射到test的规则修改成，访问相对目录/test
        (os.path.join(r"/", config['base_uri'], DATABASE_DQL_BASEURI), DQLHandler, dict(db=DATABASE)),
        (os.path.join(r"/", config['base_uri'], DATABASE_DCL_BASEURI), DCLHandler, dict(db=DATABASE)),
    ]
    return urls
