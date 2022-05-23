导入 flask

从 福利哥.脚手架 导入 *
# 从 福利哥.配置 导入 〇配置属性
从 福利哥.配置 导入 〇配置

from 福利哥.帮手 import locked_cached_property
从 福利哥.包装盒 导入 〇请求, 〇响应
从 福利哥.配置 导入 〇配置
从 福利哥.帮手 导入 构造url, 获取闪现消息々

# from datetime import timedelta
# from werkzeug.datastructures import ImmutableDict

从 汉化通用 导入 _反向注入


类 〇福利哥(flask.Flask):
    """福利哥对象实现一个 WSGI 应用, 充当枢纽对象.

    """
    request_class = 〇请求
    response_class = 〇响应
    config_class = 〇配置
    # secret_key = 〇配置属性("匚安全密钥")

    """ default_config = ImmutableDict(
        {
            "ENV": None,
            "DEBUG": None,
            "TESTING": False,
            "PROPAGATE_EXCEPTIONS": None,
            "PRESERVE_CONTEXT_ON_EXCEPTION": None,
            "SECRET_KEY": None,
            # "匚安全密钥": None,
            "PERMANENT_SESSION_LIFETIME": timedelta(days=31),
            "USE_X_SENDFILE": False,
            "SERVER_NAME": None,
            "APPLICATION_ROOT": "/",
            "SESSION_COOKIE_NAME": "session",
            "SESSION_COOKIE_DOMAIN": None,
            "SESSION_COOKIE_PATH": None,
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SECURE": False,
            "SESSION_COOKIE_SAMESITE": None,
            "SESSION_REFRESH_EACH_REQUEST": True,
            "MAX_CONTENT_LENGTH": None,
            "SEND_FILE_MAX_AGE_DEFAULT": None,
            "TRAP_BAD_REQUEST_ERRORS": None,
            "TRAP_HTTP_EXCEPTIONS": False,
            "EXPLAIN_TEMPLATE_LOADING": False,
            "PREFERRED_URL_SCHEME": "http",
            "JSON_AS_ASCII": True,
            "JSON_SORT_KEYS": True,
            "JSONIFY_PRETTYPRINT_REGULAR": False,
            "JSONIFY_MIMETYPE": "application/json",
            "TEMPLATES_AUTO_RELOAD": None,
            "MAX_COOKIE_SIZE": 4093,
        }
    ) """

    套路 __init__(
        分身,
        导入名称,
        静态url路径=空,
        静态文件夹='静态',
        静态主机=空,
        主机匹配=假,
        子域匹配=假,
        模板文件夹='模板',
        实例路径=空,
        实例相对配置=假,
        根路径=空
    ):
        super().__init__(
            import_name=导入名称,
            static_url_path=静态url路径,
            static_folder=静态文件夹,
            static_host=静态主机,
            host_matching=主机匹配,
            subdomain_matching=子域匹配,
            template_folder=模板文件夹,
            instance_path=实例路径,
            instance_relative_config=实例相对配置,
            root_path=根路径
        )
        分身.jinja_env.globals.update(构造url=构造url)
        分身.jinja_env.globals.update(获取闪现消息々=获取闪现消息々)
        分身.实例路径 = 分身.instance_path
        分身.配置 = 分身.config
        分身.url构建错误处理函数々 = 分身.url_build_error_handlers
        分身.首次请求之前调用的函数々 = 分身.before_first_request_funcs
        分身.应用上下文销毁时调用的函数々 = 分身.teardown_appcontext_funcs
        分身.交互壳上下文处理器々 = 分身.shell_context_processors
        分身.蓝图々 = 分身.blueprints
        分身.扩展々 = 分身.extensions
        分身.路由规则表 = 分身.url_map
        分身.路由规则表.主机匹配 = 分身.url_map.host_matching
        分身.路由规则表.子域匹配 = 分身.subdomain_matching

    @locked_cached_property
    套路 名称(分身):
        返回 分身.name

    @property
    套路 传播异常(分身):
        返回 分身.propagate_exceptions
    
    @property
    套路 异常时保留上下文(分身):
        返回 分身.preserve_context_on_exception

    @locked_cached_property
    套路 日志器(分身):
        返回 分身.logger
    
    @locked_cached_property
    套路 金甲环境(分身):
        返回 分身.jinja_env

    @property
    套路 已得到第一个请求(分身):
        返回 分身.got_first_request

    套路 创建配置(分身, 相对实例=假):
        返回 分身.make_config(相对实例)

    套路 自动查找实例路径(分身):
        返回 分身.auto_find_instance_path()

    套路 打开实例资源(分身, 资源, 模式='rb'):
        返回 分身.open_instance_resource(资源, 模式)

    @property
    套路 模板自动重载(分身):
        返回 分身.templates_auto_reload
    
    @模板自动重载.setter
    套路 模板自动重载(分身, 值):
        分身.templates_auto_reload = 值

    套路 创建金甲环境(分身):
        返回 分身.create_jinja_environment()

    套路 创建金甲全局加载器(分身):
        返回 分身.create_global_jinja_loader()

    套路 选择金甲自动转义(分身, 文件名):
        返回 分身.select_jinja_autoescape(文件名)

    套路 更新模板上下文(分身, 上下文):
        分身.update_template_context(上下文)

    套路 创建交互壳上下文(分身):
        返回 分身.make_shell_context()

    @property
    套路 调试(分身):
        返回 分身.debug

    @调试.setter
    套路 调试(分身, 值):
        分身.debug = 值
    
    套路 运行(分身, 主机=空, 端口=空, 调试=空, 加载点env=真, **选项々):
        """在本地开发服务器上运行应用.
        """
        分身.run(host=主机, port=端口, debug=调试, load_dotenv=加载点env, **选项々)

    套路 测试_客户端(分身, 使用酷卡=真, **关键词参数々):
        返回 分身.test_client(使用酷卡, **关键词参数々)

    套路 测试_cli运行器(分身, **关键词参数々):
        返回 分身.test_cli_runner(**关键词参数々)

    套路 注册蓝图(分身, 蓝图, **选项々):
        分身.register_blueprint(蓝图, **选项々)
    
    套路 遍历蓝图(分身):
        分身.iter_blueprints()

    套路 测试_请求上下文(分身, *参数々, **关键词参数々):
        返回 分身.test_request_context(*参数々, **关键词参数々)

    套路 模板过滤器(分身, 名称=空):
        """用于注册自定义模板过滤器的装饰器
        """
        返回 分身.template_filter(名称)

    套路 添加模板过滤器(分身, 函数, 名称=空):
        """注册一个自定义模板过滤器
        """
        分身.add_template_filter(函数, 名称)

    套路 模板全局函数(分身, 名称=空):
        """用于注册自定义模板全局函数的装饰器
        """
        返回 分身.template_global(名称)
    
    套路 添加模板全局函数(分身, 函数, 名称=空):
        """注册一个自定义模板全局函数
        """
        分身.add_template_global(函数, 名称)

    套路 模板测试(分身, 名称=空):
        """用于注册自定义模板测试的装饰器
        """
        返回 分身.template_test(名称)
    
    套路 添加模板测试(分身, 函数, 名称=空):
        """注册一个自定义模板测试
        """
        分身.add_template_test(函数, 名称)
    
    套路 添加url规则(分身, 规则, 端点=空, 视图函数=空, 提供自动选项=空, **选项々):
        """注册一条规则用于对传入的请求进行路由并构建 URL 的规则.
        """
        分身.add_url_rule(规则, endpoint=端点, view_func=视图函数,
                          provide_automatic_options=提供自动选项, **选项々)

    套路 首次请求之前(分身, 函数):
        返回 分身.before_first_request(函数)

    @property
    套路 环境(分身):
        返回 分身.env

    套路 应用上下文(分身):
        返回 分身.app_context()

    套路 异步转同步(分身, 函数):
        返回 分身.async_to_sync(函数)

    套路 应用上下文销毁(分身, 函数):
        返回 分身.teardown_appcontext(函数)

    套路 交互壳上下文处理器(分身, 函数):
        返回 分身.shell_context_processor(函数)

    套路 处理http异常(分身, 异常):
        返回 分身.handle_http_exception(异常)
    
    套路 捕捉http异常(分身, 异常):
        返回 分身.trap_http_exception(异常)
    
    套路 处理用户异常(分身, 异常):
        返回 分身.handle_user_exception(异常)
    
    套路 处理异常(分身, 异常):
        返回 分身.handle_exception(异常)
    
    套路 记录异常(分身, 异常信息):
        分身.log_exception(异常信息)
    
    套路 报路由异常(分身, 请求):
        分身.raise_routing_exception(请求)

    套路 办理请求(分身):
        返回 分身.dispatch_request()
    
    套路 全盘办理请求(分身):
        返回 分身.full_dispatch_request()
    
    套路 完结请求(分身):
        返回 分身.finalize_request()
    
    套路 尝试触发首次请求之前调用的函数々(分身):
        返回 分身.try_trigger_before_first_request_functions()
    
    套路 制作默认选项响应(分身):
        返回 分身.make_default_options_response()
    
    套路 应忽略错误(分身, 错误):
        返回 分身.should_ignore_error(错误)
    
    套路 确保同步(分身, 函数):
        返回 分身.ensure_sync(函数)

    套路 制作响应(分身, 响应返回值):
        返回 分身.make_response(响应返回值)

    套路 创建url适配器(分身, 请求):
        返回 分身.create_url_adapter(请求)
    
    套路 注入url默认值(分身, 端点, 值々):
        分身.inject_url_defaults(端点, 值々)
    
    套路 处理url构建错误(分身, 错误, 端点, 值々):
        返回 分身.handle_url_build_error(错误, 端点, 值々)
    
    套路 预处理请求(分身):
        返回 分身.preprocess_request()
    
    套路 处理响应(分身, 响应):
        返回 分身.process_response(响应)
    
    套路 执行请求最后函数(分身, 异常):
        分身.do_teardown_request(异常)
    
    套路 执行应用上下文终结函数(分身, 异常):
        分身.do_teardown_request(异常)
    
    套路 请求上下文(分身, 环境):
        返回 分身.request_context(环境)

    # wsgi_app
    
_反向注入(〇福利哥, flask.Flask)