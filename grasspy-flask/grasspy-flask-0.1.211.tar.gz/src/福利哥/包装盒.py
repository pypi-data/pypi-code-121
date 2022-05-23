从 flask 导入 Request, Response
from werkzeug.wrappers.response import ResponseStream
from werkzeug.utils import cached_property
从 汉化通用 导入 _反向注入


类 〇请求(Request):
    """福利哥默认使用的请求对象.
    """

    套路 __init__(分身, 环境, 填充请求=真, 浅=假, populate_request=True, shallow=False):
        super().__init__(环境,
                         populate_request=填充请求 or populate_request,
                         shallow=浅 or shallow)
        分身.环境 = 分身.environ
        分身.浅 = 分身.shallow
        分身.方法 = 分身.method
        分身.方案 = 分身.scheme
        分身.服务器 = 分身.server
        分身.根路径 = 分身.root_path
        分身.路径 = 分身.path
        分身.查询字符串 = 分身.query_string
        分身.头信息 = 分身.headers
        分身.远程地址 = 分身.remote_addr

    @property
    套路 url字符集(分身):
        返回 分身.url_charset

    @cached_property
    套路 参数々(分身):
        返回 分身.args
    
    @cached_property
    套路 访问路由(分身):
        返回 分身.access_route
    
    @cached_property
    套路 完整路径(分身):
        返回 分身.full_path
    
    @property
    套路 是安全协议(分身):
        返回 分身.is_secure

    @cached_property
    套路 基础url(分身):
        返回 分身.base_url
    
    @cached_property
    套路 根url(分身):
        返回 分身.root_url
    
    @cached_property
    套路 主机url(分身):
        返回 分身.host_url
    
    @cached_property
    套路 主机(分身):
        返回 分身.host
    
    @cached_property
    套路 酷卡々(分身):
        返回 分身.cookies
    
    @cached_property
    套路 内容长度(分身):
        返回 分身.content_length
    
    @property
    套路 mime类型(分身):
        返回 分身.mimetype
    
    @property
    套路 mime类型参数々(分身):
        返回 分身.mimetype_params

    @cached_property
    套路 特殊指令(分身):
        返回 分身.pragma
    
    @cached_property
    套路 接受的mime类型々(分身):
        返回 分身.accept_mimetypes
    
    @cached_property
    套路 接受的字符集々(分身):
        返回 分身.accept_charsets
    
    @cached_property
    套路 接受的编码方式々(分身):
        返回 分身.accept_encodings
    
    @cached_property
    套路 接受的语言々(分身):
        返回 分身.accept_languages
    
    @cached_property
    套路 缓存控制(分身):
        返回 分身.cache_control
    
    @cached_property
    套路 如果匹配(分身):
        返回 分身.if_match
    
    @cached_property
    套路 如无匹配(分身):
        返回 分身.if_none_match
    
    @cached_property
    套路 如有修改(分身):
        返回 分身.if_modified_since
    
    @cached_property
    套路 如无修改(分身):
        返回 分身.if_unmodified_since
    
    @cached_property
    套路 如果范围(分身):  # ?
        返回 分身.if_range
    
    @cached_property
    套路 范围(分身):
        返回 分身.range
    
    @cached_property
    套路 用户代理(分身):
        返回 分身.user_agent
    
    @cached_property
    套路 授权(分身):
        返回 分身.authorization
    
    @property
    套路 是json(分身):
        返回 分身.is_json

    @classmethod
    套路 从值创建(本类, *参数々, **关键词参数々):
        返回 本类.from_values(*参数々, **关键词参数々)
    
    @classmethod
    套路 应用程序(本类, 函数):
        返回 本类.application(函数)

    @property
    套路 希望解析表单数据(分身):
        返回 分身.want_form_data_parsed

    套路 创建表单数据解析器(分身):
        返回 分身.make_form_data_parser()

    套路 关闭(分身):
        分身.close()

    @cached_property
    套路 流(分身):
        返回 分身.stream
    
    @cached_property
    套路 数据(分身):
        返回 分身.data

    套路 获取数据(分身, 缓存=真, 转为文本=假, 解析表单数据=假):
        返回 分身.get_data(cache=缓存, as_text=转为文本, parse_form_data=解析表单数据)

    @cached_property
    套路 表单(分身):
        返回 分身.form
    
    @cached_property
    套路 值々(分身):
        返回 分身.values
    
    @cached_property
    套路 文件々(分身):
        返回 分身.files
    
    @property
    套路 脚本根(分身):
        返回 分身.script_root

    @cached_property
    套路 url根(分身):
        返回 分身.url_root

    套路 获取json(分身, 强制=假, 静默=假, 缓存=真):
        返回 分身.get_json(force=强制, silent=静默, cache=缓存)
    
    @property
    套路 内容最大长度(分身):
        返回 分身.max_content_length
    
    @property
    套路 端点(分身):
        返回 分身.endpoint
    
    @property
    套路 蓝图(分身):
        返回 分身.blueprint
    
    @property
    套路 蓝图々(分身):
        返回 分身.blueprints

    套路 json加载失败时(异常):
        返回 分身.on_json_loading_failed(异常)

〇请求.内容类型 = Request.content_type
〇请求.编码编码方式 = Request.content_encoding
〇请求.内容md5 = Request.content_md5
〇请求.访问来源 = Request.referrer
〇请求.日期 = Request.date
〇请求.最大转发次数 = Request.max_forwards
〇请求.起源 = Request.origin
〇请求.访问控制请求头 = Request.access_control_request_headers
〇请求.访问控制请求方法 = Request.access_control_request_method
〇请求.输入流 = Request.input_stream
〇请求.远程用户 = Request.remote_user
〇请求.是多线程 = Request.is_multithread
〇请求.是多进程 = Request.is_multiprocess
〇请求.只运行一次 = Request.is_run_once
〇请求.json模块 = Request.json_module
〇请求.url规则 = Request.url_rule
〇请求.视图参数々 = Request.view_args
〇请求.路由异常 = Request.routing_exception

_反向注入(〇请求, Request)        


类 〇响应(Response):
    """福利哥默认使用的响应对象.
    """

    套路 __init__(分身, 响应体=空, 状态=空, 头信息=空, mime类型=空, 内容类型=空, 直通=假,
                  response=None, status=None, headers=None, mimetype=None,
                  content_type=None, direct_passthrough=False):
        super().__init__(response=响应体 or response,
                         status=状态 or status,
                         headers=头信息 or headers,
                         mimetype=mime类型 or mimetype,
                         content_type=内容类型 or content_type,
                         direct_passthrough=直通 or direct_passthrough)
        分身.头信息 = 分身.headers
        分身.响应体 = 分身.response

    @property
    套路 状态码(分身):
        返回 分身.status_code

    @状态码.setter
    套路 状态码(分身, 代码):
        分身.status_code = 代码
    
    @property
    套路 状态(分身):
        返回 分身.status

    @状态.setter
    套路 状态(分身, 值):
        分身.status = 值

    套路 设置酷卡(分身, 键, 值="", 最大年龄=空, 到期时间=空, 路径="/",
                 域=空, 安全=假, 仅限http=假, 同一站点=空):
        分身.set_cookie(键, value=值, max_age=最大年龄, expires=到期时间,
                        path=路径, domain=域, secure=安全, httponly=仅限http,
                        samesite=同一站点)
    
    套路 删除酷卡(分身, 键, 路径="/", 域=空, 安全=假, 仅限http=假, 同一站点=空):
        分身.delete_cookie(键, path=路径, domain=域, secure=安全,
                           httponly=仅限http, samesite=同一站点)

    @property
    套路 是json(分身):
        返回 分身.is_json
    
    @property
    套路 mime类型(分身):
        返回 分身.mimetype
    
    @mime类型.setter
    套路 mime类型(分身, 值):
        分身.mimetype = 值
    
    @property
    套路 mime类型参数々(分身):
        返回 分身.mimetype_params

    @property
    套路 多少秒后重试(分身):
        返回 分身.retry_after
    
    @多少秒后重试.setter
    套路 多少秒后重试(分身, 值):
        分身.retry_after = 值

    @property
    套路 缓存控制(分身):
        返回 分身.cache_control

    套路 设置etag(分身, etag, 弱=假):
        分身.set_etag(etag, 弱)
    
    套路 获取etag(分身):
        返回 分身.get_etag()

    @property
    套路 内容范围(分身):
        返回 分身.content_range
    
    @内容范围.setter
    套路 内容范围(分身, 值):
        分身.content_range = 值

    @property
    套路 www认证(分身):
        返回 分身.www_authenticate

    @property
    套路 内容安全策略(分身):
        返回 分身.content_security_policy
    
    @内容安全策略.setter
    套路 内容安全策略(分身, 值):
        分身.content_security_policy = 值
    
    @property
    套路 内容安全策略_仅报告(分身):
        返回 分身.content_security_policy_report_only
    
    @内容安全策略_仅报告.setter
    套路 内容安全策略_仅报告(分身, 值):
        分身.content_security_policy_report_only = 值
    
    @property
    套路 访问控制_允许凭证(分身):
        返回 分身.access_control_allow_credentials
    
    @访问控制_允许凭证.setter
    套路 访问控制_允许凭证(分身, 值):
        分身.access_control_allow_credentials = 值

    套路 关闭时调用(分身, 函数):
        返回 分身.call_on_close(函数)
    
    @classmethod
    套路 强制类型(本类, 响应, 环境=空):
        返回 本类.force_type(响应, 环境)
    
    @classmethod
    套路 从应用创建(本类, 应用, 环境, 缓冲=假):
        返回 本类.from_app(应用, 环境, 缓冲)

    套路 获取数据(分身, 转为文本=假):
        返回 分身.get_data(转为文本)
    
    套路 设置数据(分身, 值):
        分身.set_data(值)

    数据 = property(
        获取数据,
        设置数据,
        doc="A descriptor that calls :meth:`get_data` and :meth:`set_data`.",
    )

    套路 计算内容长度(分身):
        返回 分身.calculate_content_length()
    
    套路 转成序列(分身):
        分身.make_sequence()
    
    套路 迭代_编码(分身):
        返回 分身.iter_encoded()

    @property
    套路 是流(分身):
        返回 分身.is_streamed
    
    @property
    套路 是序列(分身):
        返回 分身.is_sequence
    
    套路 关闭(分身):
        分身.close()
    
    套路 冻结(分身):
        分身.freeze()
    
    套路 获取wsgi头信息(分身, 环境):
        返回 分身.get_wsgi_headers(环境)
    
    套路 获取应用迭代器(分身, 环境):
        返回 分身.get_app_iter(环境)
    
    套路 获取wsgi响应(分身, 环境):
        返回 分身.get_wsgi_response(环境)

    套路 获取json(分身, 强制=假, 静默=假):
        返回 分身.get_json(force=强制, silent=静默)

    @cached_property
    套路 流(分身):
        返回 分身.stream

    套路 转成条件式(分身, 请求或环境, 接受的范围=假, 完整长度=空):
        返回 分身.make_conditional(请求或环境, accept_ranges=接受的范围,
                                  complete_length=完整长度)

    套路 添加etag(分身, 覆写=假, 弱=假):
        分身.add_etag(overwrite=覆写, weak=弱)

    @property
    套路 酷卡最大大小(分身):
        返回 分身.max_cookie_size

〇响应.位置 = Response.location
〇响应.年龄 = Response.age
〇响应.内容类型 = Response.content_type
〇响应.内容长度 = Response.content_length
〇响应.内容位置 = Response.content_location
〇响应.内容编码方式 = Response.content_encoding
〇响应.内容md5 = Response.content_md5
〇响应.日期 = Response.date
〇响应.到期时间 = Response.expires
〇响应.最后修改时间 = Response.last_modified
〇响应.多样化 = Response.vary # ？
〇响应.内容语言 = Response.content_language
〇响应.允许 = Response.allow
〇响应.接受的范围 = Response.accept_ranges
〇响应.访问控制_允许的头信息 = Response.access_control_allow_headers
〇响应.访问控制_允许的方法 = Response.access_control_allow_methods
〇响应.访问控制_允许的起源 = Response.access_control_allow_origin
〇响应.访问控制_暴露的头信息 = Response.access_control_expose_headers
〇响应.访问控制_最大年龄 = Response.access_control_max_age
〇响应.跨域打开器策略 = Response.cross_origin_opener_policy   # ？
〇响应.跨域嵌入器策略 = Response.cross_origin_embedder_policy # ？
〇响应.默认mime类型 = Response.default_mimetype
〇响应.json模块 = Response.json_module
# 〇响应.自动纠正位置头 = Response.autocorrect_location_header

_反向注入(〇响应, Response)


类 〇响应流(ResponseStream):

    套路 写入(分身, 值):
        返回 分身.write(值)
    
    套路 写入行々(分身, 序列):
        分身.writelines(序列)
    
    套路 关闭(分身):
        分身.close()
    
    套路 强制刷新(分身):
        分身.flush()
    
    套路 是终端(分身):
        返回 分身.isatty()
    
    套路 定位(分身):
        返回 分身.tell()

    @property
    套路 编码方式(分身):
        返回 分身.encoding
    
    @property
    套路 响应(分身):
        返回 分身.response
    
    @property
    套路 已关闭(分身):
        返回 分身.closed

_反向注入(〇响应流, ResponseStream)