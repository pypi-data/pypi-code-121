从 flask.sessions 导入 SessionMixin, SecureCookieSession, SessionInterface
从 汉化通用 导入 _反向注入

类 〇会话混入(SessionMixin):
    
    @property
    套路 永久(分身):
        返回 分身.permanent

    @永久.setter
    套路 永久(分身, 值):
        分身.permanent = 值

    @property
    套路 新创建(分身):
        返回 分身.new

    @新创建.setter
    套路 新创建(分身, 值):
        分身.new = 值
    
    @property
    套路 已修改(分身):
        返回 分身.modified

    @已修改.setter
    套路 已修改(分身, 值):
        分身.modified = 值

_反向注入(〇会话混入, SessionMixin)


类 〇安全酷卡会话(SecureCookieSession):

    套路 获取(分身, 键, 默认值=空):
        返回 分身.get(键, 默认值)

    套路 设默认值(分身, 键, 默认值=空):
        返回 分身.setdefault(键, 默认值)

_反向注入(〇安全酷卡会话, SecureCookieSession)


类 〇会话接口(SessionInterface):

    套路 创建空会话(分身, 应用):
        返回 分身.make_null_session(应用)
    
    套路 是空会话(分身, 对象):
        返回 分身.is_null_session(对象)
    
    套路 获取酷卡名称(分身, 应用):
        返回 分身.get_cookie_name(应用)
    
    套路 获取酷卡域(分身, 应用):
        返回 分身.get_cookie_domain(应用)
    
    套路 获取酷卡路径(分身, 应用):
        返回 分身.get_cookie_path(应用)
    
    套路 获取酷卡的仅限http设置(分身, 应用):
        返回 分身.get_cookie_httponly(应用)
    
    套路 获取酷卡的安全设置(分身, 应用):
        返回 分身.get_cookie_secure(应用)
    
    套路 获取酷卡的同一站点设置(分身, 应用):
        返回 分身.get_cookie_samesite(应用)
    
    套路 获取到期时间(分身, 应用, 会话):
        返回 分身.get_expiration_time(应用, 会话)
    
    套路 应设置酷卡(分身, 应用, 会话):
        返回 分身.should_set_cookie(应用, 会话)

    # 套路 打开会话(分身, 应用, 请求):
    #     报 爻未实现错误()
    
    # 套路 保存会话(分身, 应用, 会话, 响应):
    #     报 爻未实现错误()

    # def open_session(self, app, request):
    #     返回 self.打开会话(app, request)
    
    # def save_session(self, app, session, response):
    #     self.保存会话(app, session, response)

_反向注入(〇会话接口, SessionInterface)