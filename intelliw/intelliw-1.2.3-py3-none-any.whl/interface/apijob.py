#!/usr/bin/env python
# coding: utf-8

import os
import json
import signal
import tornado
import tornado.options
import intelliw.utils.message as message
from intelliw.config import config
from intelliw.utils.util import default_dump
from intelliw.core.infer import Infer
from intelliw.core.report import RestReport
from intelliw.utils.logger import get_logger
from intelliw.utils.global_val import gl
from intelliw.interface import apihandler

logger = get_logger()


childs = []
def exit_handler(signum, frame):
    for child in childs:
        child.terminate()

class Application(tornado.web.Application):
    # Set URL handlers
    HANDLERS = []
    HAS_INFER = False

    def __init__(self, custom_router, reporter):
        self.reporter = reporter
        # Set settings
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            xsrf_cookies=False,
            autoescape=None,
            session_age=10 * 60 * 60,
        )
       
        Application.__hander_process(custom_router)
        tornado.web.Application.__init__(self, Application.HANDLERS, **settings)
    
    @classmethod
    def route(cls, path, **options):
        def decorator(f):
            func = f.__name__
            if func == 'infer':
                cls.HAS_INFER = True
            cls.HANDLERS.append((path, apihandler.MainHandler, {'func': func, 'method':options.pop('method', 'post'), 'need_featrue':options.pop('need_featrue', True)}))
            return f
        return decorator

    @classmethod
    def __hander_process(cls, router):
        # 加载自定义api, 配置在algorithm.yaml中
        for r in router:
            path, func, method, need_featrue = r["path"], r["func"], r.get("method", "post").lower(), r.get("need_featrue", True)
            if func == 'infer':
                cls.HAS_INFER = True
            cls.HANDLERS.append((path, apihandler.MainHandler, {'func': func, 'method':method, 'need_featrue':need_featrue}))

        # 检查用户是否完全没有配置路由
        if len(cls.HANDLERS) == 0 or not cls.HAS_INFER:
            cls.HANDLERS.append((r'/predict', apihandler.MainHandler, {'func': 'infer', 'method':'post', 'need_featrue':True}))  # 默认值
        
        # 输出路由
        for r,_,info in cls.HANDLERS:
            f, m, nf = info.get("func"), info.get("method"), info.get("need_featrue")
            logger.info(f"方法: {f} 加载成功, 访问路径：{r}, 访问方法:{m}, 是否需要特征处理:{nf}")

        # healthcheck
        cls.HANDLERS.append((r'/healthcheck', apihandler.HealthCheckHandler))


class ApiService:
    def __init__(self, port, path, response_addr):
        self.port = port        # 8888
        self.PERODIC_INTERVAL = config.PERODIC_INTERVAL if config.PERODIC_INTERVAL == 0 else 10
        infer = Infer(path, response_addr, self.PERODIC_INTERVAL)

        # 获取自定义api
        self.custom_router = infer.pipeline.custom_router

        # infer存入全局
        tornado.options.define("infer", default=infer, help="infer object")

        self.reporter = RestReport(response_addr)
        msg = [{
            'status': 'start',  # 'start'
            'inferid': config.INFER_ID,             # ''
            'instanceid': config.INSTANCE_ID,       # ''
            'inferTaskStatus': []           # []
        }]
        self.reporter.report(
            message.CommonResponse(200, "inferstatus", '', json.dumps(msg, default=default_dump, ensure_ascii=False)))

    def perodic_callback(self):
        tornado.options.options.infer.perodic_callback()
        if self.PERODIC_INTERVAL > 0:
            self.io_loop.call_later(
                self.PERODIC_INTERVAL, self.perodic_callback)

    def run(self):
        signal.signal(signal.SIGILL, exit_handler)
        app = tornado.httpserver.HTTPServer(
            request_callback=Application(self.custom_router, self.reporter), xheaders=True)
        app.listen(self.port)
        self.io_loop = tornado.ioloop.IOLoop.instance()
        if self.PERODIC_INTERVAL > 0:
            self.io_loop.call_later(
                self.PERODIC_INTERVAL, self.perodic_callback)
        self.io_loop.start()
