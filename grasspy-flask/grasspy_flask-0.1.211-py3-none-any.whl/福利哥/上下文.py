从 flask.ctx 导入 _AppCtxGlobals
从 flask.ctx 导入 after_this_request
从 flask.ctx 导入 copy_current_request_context
从 flask.ctx 导入 has_request_context
从 flask.ctx 导入 has_app_context
从 flask.ctx 导入 AppContext
从 flask.ctx 导入 RequestContext
从 汉化通用 导入 _反向注入

_哨兵 = object()

类 _〇应用上下文全局对象(_AppCtxGlobals):

    套路 获取(分身, 名称, 默认值=空):
        返回 分身.get(名称, 默认值)
    
    套路 弹出(分身, 名称, 默认值=_哨兵):
        返回 分身.pop(名称, 默认值)
    
    套路 设默认值(分身, 名称, 默认值=空):
        返回 分身.setdefault(名称, 默认值)

_反向注入(_〇应用上下文全局对象, _AppCtxGlobals)


套路 本次请求之后(函数):
    返回 after_this_request(函数)

套路 拷贝当前请求上下文(函数):
    返回 copy_current_request_context(函数)

套路 拥有请求上下文():
    返回 has_request_context()

套路 拥有应用上下文():
    返回 has_app_context()


类 〇应用上下文(AppContext):

    套路 压入(分身):
        分身.push()
    
    套路 弹出(分身, 异常=_哨兵):
        分身.pop(异常)

_反向注入(〇应用上下文, AppContext)


类 〇请求上下文(RequestContext):

    @property
    套路 万事通(分身):
        返回 分身.g
    
    @万事通.setter
    套路 万事通(分身, 值):
        分身.g = 值

    套路 拷贝(分身):
        返回 分身.copy()
    
    套路 匹配请求(分身):
        分身.match_request()

    套路 压入(分身):
        分身.push()
    
    套路 弹出(分身, 异常=_哨兵):
        分身.pop(异常)
    
    套路 自动弹出(分身, 异常):
        分身.auto_pop(异常)

_反向注入(〇请求上下文, RequestContext)