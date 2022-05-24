#!/usr/bin/env python
# coding: utf-8

import os
import json
import signal
import tornado
import traceback
import intelliw.utils.message as message
from intelliw.config import config
from intelliw.utils.util import default_dump
from intelliw.core.pipeline import Pipeline
from intelliw.core.report import RestReport
from intelliw.utils.logger import get_logger

logger = get_logger()

childs = []
pipeline = None


def exit_handler(signum, frame):
    for child in childs:
        child.terminate()


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            global pipeline
            r = json.loads(self.request.body)
            cfgs = r['transforms']
            data = r['data']
            logger.info("请求校验数据 {}".format(data))
            if pipeline is not None:
                result = pipeline.validate_transforms(cfgs, data)
                logger.info("函数校验结果 {}".format(result))
                self.write(str(message.CommonResponse(200, "validate", '', result)))
            else:
                self.write(message.err_invalid_validate_request)
        except Exception as e:
            stack_info = traceback.format_exc()
            self.write(str(message.CommonResponse(500, "validate",
                                                  "验证服务处理推理数据错误 {}, stack:\n{}".format(e, stack_info))))

    def get(self):
        self.write(str(message.err_invalid_validate_request))


class Application(tornado.web.Application):
    def __init__(self, name):
        # Set settings
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__),
                                       "templates"),
            xsrf_cookies=False,
            autoescape=None,
            session_age=10 * 60 * 60,
        )

        # Set URL handlers
        handlers = [(r'/' + name, MainHandler)]
        tornado.web.Application.__init__(self, handlers, **settings)


class ValidateService:
    def __init__(self, name, port, path, reporter):
        self.name = name or 'validate'
        self.port = port
        self.PERODIC_INTERVAL = 10 if config.PERODIC_INTERVAL == 0 else config.PERODIC_INTERVAL
        global pipeline
        pipeline = Pipeline(reporter, self.PERODIC_INTERVAL)
        pipeline.importalg(path)
        pipeline.reporter.report(
            message.CommonResponse(200, "validate", '', json.dumps({}, default=default_dump, ensure_ascii=False)))

    def perodic_callback(self):
        pass

    def run(self):
        signal.signal(signal.SIGILL, exit_handler)
        app = tornado.httpserver.HTTPServer(request_callback=Application(self.name), xheaders=True)
        app.listen(self.port)
        self.io_loop = tornado.ioloop.IOLoop.instance()
        if self.PERODIC_INTERVAL > 0:
            self.io_loop.call_later(self.PERODIC_INTERVAL, self.perodic_callback)
        self.io_loop.start()
