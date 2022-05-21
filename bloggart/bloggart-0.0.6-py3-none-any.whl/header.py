import tornado.ioloop
import tornado.web
from bloggart.core import config
from bloggart.core import database
from bloggart.core import fileserver
from bloggart.core import static
from bloggart.core import service
# import socket
# g_server_ip = socket.gethostbyname(socket.gethostname())
import argparse

def get_args_parser():
    parser = argparse.ArgumentParser(description="bloggart command line interface.")
    parser.add_argument("-c", "--config", default='config.ini', help="配置文件路径")
    parser.add_argument("-p", "--port", default=80, type=int, help="配置文件路径")
    return parser.parse_args()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def Run():
    args = get_args_parser()
    print(args)

    config.Parse(args.config)
    print(config.CONFIG)

    handler = []
    handler.extend(database.Handle(config.Get_database()))
    handler.extend(fileserver.Handle(config.Get_fileserver()))
    handler.extend(static.Handle(config.Get_uploadserver()))
    service.Serving(int(args.port), handler)
    
    exit()
    
if __name__ == "__main__":
    Run()
