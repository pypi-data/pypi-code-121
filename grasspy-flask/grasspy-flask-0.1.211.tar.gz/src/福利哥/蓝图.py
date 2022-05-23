导入 flask
从 汉化通用 导入 _反向注入

类 〇蓝图(flask.Blueprint):
    套路 __init__(
        分身,
        名称,
        导入名称,
        静态文件夹='静态',
        静态url路径 = 空,
        模板文件夹 = '模板',
        url前缀 = 空,
        子域 = 空,
        url默认值 = 空,
        根路径 = 空,
        cli分组 = flask.scaffold._sentinel,
    ):
        super().__init__(
            名称,
            导入名称,
            static_folder=静态文件夹,
            static_url_path=静态url路径,
            template_folder=模板文件夹,
            url_prefix=url前缀,
            subdomain=子域,
            url_defaults=url默认值,
            root_path=根路径,
            cli_group=cli分组,
        )
        分身.名称 = 分身.name
        分身.url前缀 = 分身.url_prefix
        分身.子域 = 分身.subdomain
        分身.子域 = 分身.subdomain
        分身.延后函数々 = 分身.deferred_functions
        分身.url值默认回调函数々 = 分身.url_values_defaults
        分身.cli分组 = 分身.cli_group

    套路 记录(分身, 函数):
        分身.record(函数)
    
    套路 记录_一次(分身, 函数):
        分身.record_once(函数)
    
    套路 创建设置状态(分身, 应用, 选项々, 首次注册=假):
        返回 分身.make_setup_state(应用, 选项々, 首次注册)
    
    套路 注册蓝图(分身, 蓝图, **选项々):
        分身.register_blueprint(蓝图, **选项々)
    
    套路 注册(分身, 应用, 选项々):
        分身.register(应用, 选项々)
    
    套路 添加url规则(分身, 规则, 端点=空, 视图函数=空, 提供自动选项=空, **选项々):
        分身.add_url_rule(规则, endpoint=端点, view_func=视图函数,
                         provide_automatic_options=提供自动选项, **选项々)

    套路 应用模板过滤器(分身, 名称=空):
        返回 分身.app_template_filter(名称)
    
    套路 添加应用模板过滤器(分身, 函数, 名称=空):
        分身.add_app_template_filter(函数, 名称)
    
    套路 应用模板测试(分身, 名称=空):
        返回 分身.app_template_test(名称)
    
    套路 添加应用模板测试(分身, 函数, 名称=空):
        分身.add_app_template_test(函数, 名称)
    
    套路 应用模板全局函数(分身, 名称=空):
        返回 分身.app_template_global(名称)
    
    套路 添加应用模板全局函数(分身, 函数, 名称=空):
        分身.add_app_template_global(函数, 名称)

    套路 应用请求之前(分身, 函数):
        返回 分身.before_app_request(函数)
    
    套路 应用首次请求之前(分身, 函数):
        返回 分身.before_app_first_request(函数)
    
    套路 应用请求之后(分身, 函数):
        返回 分身.after_app_request(函数)
    
    套路 应用请求最后(分身, 函数):
        返回 分身.teardown_app_request(函数)
    
    套路 应用上下文处理器(分身, 函数):
        返回 分身.app_context_processor(函数)
    
    套路 应用错误处理函数(分身, 错误码):
        返回 分身.app_errorhandler(错误码)
    
    套路 应用url值预处理器(分身, 函数):
        返回 分身.app_url_value_preprocessor(函数)
    
    套路 应用url默认回调函数(分身, 函数):  # ？
        返回 分身.app_url_defaults(函数)

_反向注入(〇蓝图, flask.Blueprint)