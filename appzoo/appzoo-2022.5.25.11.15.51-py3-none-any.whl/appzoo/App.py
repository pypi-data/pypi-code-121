#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : mi.
# @File         : iapp
# @Time         : 2020/10/22 11:01 上午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

from io import BytesIO

from starlette.status import *
from starlette.responses import *
from starlette.staticfiles import StaticFiles

from fastapi import FastAPI, Form, Depends, File, UploadFile, Body, Request
from multipart.multipart import parse_options_header

# ME
from meutils.pipe import *
from meutils.str_utils import json_loads


# app_ = FastAPI(title='AppZoo')  # todo: 全局变量


class App(object):
    """
    from appzoo import App
    app = App()
    app_ = app.app
    app.add_route()

    if __name__ == '__main__':
        app.run(app.app_from(__file__), port=9955, debug=True)
    """

    def __init__(self, verbose=True):
        self.app = FastAPI(title='AppZoo')
        # self.app = app_

        # 原生接口
        self.get = self.app.get
        self.post = self.app.post
        self.api_route = self.app.api_route
        self.mount = self.app.mount  # mount('/subapi', subapp)

    def run(self, app=None, host="0.0.0.0", port=8000, workers=1, access_log=True, debug=False, **kwargs):
        """

        :param app:   app字符串可开启热更新 debug/reload
        :param host:
        :param port:
        :param workers:
        :param access_log:
        :param debug: reload
        :param kwargs:
        :return:
        """

        import uvicorn
        """
        https://www.cnblogs.com/poloyy/p/15549265.html 
        https://blog.csdn.net/qq_33801641/article/details/121313494
        """
        uvicorn.config.LOGGING_CONFIG['formatters']['access'][
            'fmt'] = '%(asctime)s - %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

        # if debug == False:
        #     access_log = False

        uvicorn.run(
            app if app else self.app,
            host=host, port=port, workers=workers, access_log=access_log, debug=debug, **kwargs
        )

    def add_route(self, path='/xxx', func=lambda x='demo': x, method="GET", **kwargs):

        handler = self._handler(func, method, **kwargs)
        self.app.api_route(path=path, methods=[method])(handler)

    def add_route_plus(self, path='/xxx', func=None, method="GET", **kwargs):
        """

        :param path:
        :param func:
            @lru_cache()
            def cache(kwargs: str):
                time.sleep(3)
                return kwargs # json.load(kwargs.replace("'", '"'))

            def nocache(kwargs: dict): # 不指定类型默认字典输入
                time.sleep(3)
                return kwargs
        :param method:
        :param kwargs:
        :return:
        """
        assert isinstance(func, Callable)

        handler = self._handler_plus(func, **kwargs)

        self.app.api_route(path=path, methods=[method])(handler)  # method

    def add_route_uploadfiles(self, path='/xxx', func=lambda x='demo': x, **kwargs):
        """
        def read_func(**kwargs):
        logger.info(kwargs)
        return pd.read_csv(kwargs['files'][0], names=['word']).to_dict('r')

        app.add_route_uploadfiles('/upload', read_func)

        :param path:
        :param func:
        :param kwargs:
        :return:
        """

        handler = self._handler4files(func, **kwargs)
        self.app.api_route(path=path, methods=['POST'])(handler)  # method

    def add_apps(self, app_dir='apps', main_func='main', **kwargs):
        """加载当前app_dir文件夹下的所有app（递归）, 入口函数都是main
        1. 过滤掉 _ 开头的py文件
        2. 支持单文件

        appcli easy-run <app_dir>
        """

        app_home = Path(sys_path_append(app_dir))
        n = app_home.parts.__len__()

        pattern = Path(app_dir).name if Path(app_dir).is_file() else '*.py'

        routes = []
        for p in app_home.rglob(pattern):
            home_parts = p.parts[n:]
            route = f'/{app_home.stem}/' + "/".join(home_parts)[:-3]
            module = importlib.import_module('.'.join(home_parts)[:-3])

            if hasattr(module, main_func):
                func = getattr(module, main_func)
                self.add_route(route, func, method='POST', **kwargs)
                routes.append(route)
            else:
                logger.warning(f"Filter: {p}")

        logger.info(f"Add Routes: {routes}")

        self.add_route(f'/__{app_home.stem}', lambda: routes, method='GET', **kwargs)
        return routes

    def _handler(self, func, method='GET', result_key='data', **kwargs):
        """

        :param func:
        :param method:
            get -> request: Request
            post -> kwargs: dict
        :param result_key:
        :return:
        """
        if method == 'GET':
            async def handler(request: Request):
                input = request.query_params._dict
                return self._try_func(input, func, result_key, **kwargs)

        elif method == 'POST':
            async def handler(kwargs_: dict):
                input = kwargs_
                return self._try_func(input, func, result_key, **kwargs)

        else:
            async def handler():
                return {'Warning': 'method not in {"GET", "POST"}'}

        return handler

    def _handler4files(self, func, result_key='data', **kwargs):
        """

        :param func:
        :param result_key:
        :return:
        """

        async def handler(request: Request, files: List[UploadFile] = File(...)):
            input = request.query_params._dict

            input['files'] = [BytesIO(await file.read()) for file in files]

            return self._try_func(input, func, result_key, **kwargs)

        return handler

    def _handler_plus(self, func, **kwargs):

        # todo: 兼容其他请求，比如 request.form()
        async def handler(request: Request):
            # content_type_header = request.headers.get("Content-Type")
            # content_type, options = parse_options_header(content_type_header)

            input = request.query_params._dict
            body = await request.body()  # get 一般为空

            if body:  # 避免重复 key
                # input.update(json.loads(body))
                input.update(json_loads(body))

            # input4str 方便 cache
            if str(func.__annotations__).__contains__('str'):
                input = str(input)

            return self._try_func_plus(input, func, **kwargs)

        return handler

    @staticmethod
    def _try_func(input, func, result_key='data', **kwargs):  # todo: 可否用装饰器
        __debug = input.pop('__debug', 0)

        output = OrderedDict()
        output['error_code'] = 0
        output['error_msg'] = "SUCCESS"

        if __debug:
            output['requestParams'] = input
            output['timestamp'] = time.ctime()

        try:
            output[result_key] = func(**input)

        except Exception as error:
            output['error_code'] = 1  # 通用错误
            output['error_msg'] = traceback.format_exc().strip() if __debug else error  # debug状态获取详细信息

        finally:
            output.update(kwargs)

        return output

    @staticmethod
    def _try_func_plus(input, func, **kwargs):

        output = OrderedDict(code=200, msg="SUCCESS", **kwargs)

        try:
            output['data'] = func(input)

        except Exception as error:
            output['code'] = 500  # 通用错误
            output['msg'] = traceback.format_exc().strip()  # debug状态获取详细信息

            logger.error(output['msg'])

        # finally:
        #     output.update(kwargs)

        return output

    def app_file_name(self, file=__file__):
        return Path(file).stem

    def app_from(self, file=__file__, app='app_'):
        return f"{Path(file).stem}:{app}"


if __name__ == '__main__':
    import uvicorn

    app = App()
    app.add_route('/get', lambda **kwargs: kwargs, method="GET", result_key="GetResult")
    app.add_route('/post', lambda **kwargs: kwargs, method="POST", result_key="PostResult")

    app.run(port=9000, debug=False, reload=False, access_log=True)
    # app.run(f"{app.app_from(__file__)}", port=9000, debug=False, reload=False) # app_的在 __main__ 之上
