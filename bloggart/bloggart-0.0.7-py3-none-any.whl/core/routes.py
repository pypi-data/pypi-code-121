import os
import json
import tornado
# from bloggart.core import config

class DQLHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        print(db)
        self.db = db

    # def get(self, table, offset, limit):
    #     _dql(table, offset, limit)

    def post(self):
        self.set_header("Content-Type", "text/plain")
        # curl -X POST http://localhost:8888/dql -d 'message=d'
        # self.write("You wrote " + self.get_body_argument("message"))

        # curl -X POST http://localhost:8888/dql -d '{"message":"d"}'
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        print(param)
        _dql(param['sql'])
        self.write('ok')
 
# import tornado.web
# import os

# FILESERVER_BASEURI = 'static'

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world")

# def Init(config):
#     uri = os.path.join(r"/", config['base_uri'], FILESERVER_BASEURI)
#     print(config, uri)
#     return [(uri, MainHandler)]