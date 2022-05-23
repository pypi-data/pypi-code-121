从 flask.scaffold 导入 Scaffold, find_package
from 福利哥.帮手 import locked_cached_property
从 汉化通用 导入 _反向注入


类 〇脚手架(Scaffold):
    """ '〇福利哥' 类和 '〇蓝图' 类都有的共同行为
    """
    套路 __init__(
        分身,
        导入名称,
        静态文件夹=空,
        静态url路径=空,
        模板文件夹=空,
        根路径=空
    ):
        super().__init__(
            import_name=导入名称,
            static_folder=静态文件夹,
            static_url_path=静态url路径,
            template_folder=模板文件夹,
            root_path=根路径
        )
        分身.导入名称 = 分身.import_name
        分身.模板文件夹 = 分身.template_folder
        分身.根路径 = 分身.root_path
        分身.视图函数々 = 分身.view_functions
        分身.错误处理函数规格 = 分身.error_handler_spec
        分身.请求之前调用的函数々 = 分身.before_request_funcs
        分身.请求之后调用的函数々 = 分身.after_request_funcs
        分身.请求最后调用的函数々 = 分身.teardown_request_funcs
        分身.模板上下文处理器々 = 分身.template_context_processors
        分身.url值预处理器々 = 分身.url_value_preprocessors
        分身.url默认回调函数々 = 分身.url_default_functions

    @property
    套路 静态文件夹(分身):
        返回 分身.template_folder
    
    @静态文件夹.setter
    套路 静态文件夹(分身, 值):
        分身.template_folder = 值

    @property
    套路 有静态文件夹(分身):
        返回 分身.has_static_folder

    @property
    套路 静态url路径(分身):
        返回 分身.static_url_path
    
    @静态url路径.setter
    套路 静态url路径(分身, 值):
        分身.static_url_path = 值

    套路 获取发送文件最大年龄(分身, 文件名):
        返回 分身.get_send_file_max_age(文件名)
    
    套路 发送静态文件(分身, 文件名):
        返回 分身.send_static_file(文件名)

    @locked_cached_property
    套路 金甲加载器(分身):
        返回 分身.jinja_loader

    套路 打开资源(分身, 资源, 模式='rb'):
        返回 分身.open_resource(资源, 模式)

    套路 查_get(分身, 规则, **选项々):
        返回 分身.get(规则, **选项々)
    
    套路 增_post(分身, 规则, **选项々):
        返回 分身.post(规则, **选项々)
    
    套路 改_put(分身, 规则, **选项々):
        返回 分身.put(规则, **选项々)
    
    套路 删_delete(分身, 规则, **选项々):
        返回 分身.delete(规则, **选项々)
    
    套路 补_patch(分身, 规则, **选项々):
        返回 分身.patch(规则, **选项々)

    套路 路由(分身, 规则, **选项々):
        如果 '方法々' 在 选项々:
            选项々['methods'] = 选项々.弹出('方法々')

        返回 分身.route(规则, **选项々)

    套路 端点(分身, 端点):
        返回 分身.endpoint(端点)

    套路 请求之前(分身, 函数):
        返回 分身.before_request(函数)

    套路 请求之后(分身, 函数):
        返回 分身.after_request(函数)
    
    套路 请求最后(分身, 函数):
        返回 分身.teardown_request(函数)
    
    套路 上下文处理器(分身, 函数):
        返回 分身.context_processor(函数)
    
    套路 url值预处理器(分身, 函数):
        返回 分身.url_value_preprocessor(函数)

    套路 url默认回调函数(分身, 函数):
        返回 分身.url_defaults(函数)
    
    套路 错误处理函数(分身, 错误码或异常):
        返回 分身.errorhandler(错误码或异常)
    
    套路 注册错误处理函数(分身, 错误码或异常, 函数):
        返回 分身.register_error_handler(错误码或异常, 函数)
    
_反向注入(〇脚手架, Scaffold)


套路 查找包(导入名称):
    返回 find_package(导入名称)