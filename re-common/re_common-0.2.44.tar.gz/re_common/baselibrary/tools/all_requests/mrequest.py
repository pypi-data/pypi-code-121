import json

from re_common.baselibrary.utils.core.requests_core import MsgCode


class MRequest(object):
    POST = "post"
    GET = "get"

    def __init__(self, logger=None):
        if logger is None:
            from re_common.baselibrary import MLogger
            logger = MLogger().streamlogger
        self.logger = logger
        self.html = None
        self.html_bytes = None
        self.resp = None
        self.marks = []
        self.middler_list = [self.is_null_html_middlerwares, self.status_code_middlerwares, self.end_middlerwares,
                             self.marks_middlerwares]
        self.status_code = None
        self.header = None
        self.refer = None
        self.proxy = None
        self.url = None
        self.params = None
        self.data = None
        self.cookies = None
        self.sn = None
        self.files = None
        self.auth = None
        self.timeout = None
        self.allow_redirects = True
        self.hooks = None
        self.stream = None
        self.verify = None
        self.cert = None
        self.json = None
        self.resp_encoding = None
        self.resp_errors = "strict"
        self.resp_dicts = {"code": self.status_code, "msg": ""}
        self.allow_resp_text = True
        self.allow_resp_bytes = False
        self.middler_para = {}
        self.skip_auto_headers = None
        self.force_close = None  # "true" or "false"

    def set_force_close(self, true_or_false):
        self.force_close = true_or_false

    def set_skip_auto_headers(self, lists):
        """
        设置skip_auto_headers的参数
        skip_auto_headers 用法: 不对列表内的对应参数进行自动生成
        :return:
        """
        self.skip_auto_headers = lists
        return self

    def set_middler_para(self, dicts):
        """
        设置middler的参数
          def status_code_middlerwares(self, status_code=200):
          可以设置
          dicts = {”status_code_middlerwares“:{"status_code":200}}
        :return:
        """
        self.middler_para = dicts

    def set_allow_redirects(self, flag=True):
        """
        设置是否允许重定向
        :param flag:
        :return:
        """
        self.allow_redirects = flag
        return self

    def set_allow_resp_text(self, flag=True):
        """
        设置是否返回response内容
        解决重定向设置为false时内容无法解析导致编码错误
        :param flag:
        :return:
        """
        self.allow_resp_text = flag
        return self

    def set_allow_resp_bytes(self, flag=True):
        """
        设置是否返回response内容的字节信息，grpc可以用到
        :param flag:
        :return:
        """
        self.allow_resp_bytes = flag
        return self

    def set_resp_errors(self, errors):
        """
        设置结果是否忽略乱码错误 可以设置为 ignore
        errors 为 decode 的属性 errors=errors
        :param errors:
        :return:
        """
        self.resp_errors = errors
        return self

    def set_resp_encoding(self, encode):
        """
        设置结果编码
        :param encode:
        :return:
        """
        self.resp_encoding = encode
        return self

    def set_html(self, html):
        """
        设置html
        :param html:
        :return:
        """
        self.html = html
        return self

    def set_status_code(self, status_code):
        """
        设置状态码
        :param status_code:
        :return:
        """
        self.status_code = status_code
        self.resp_dicts["code"] = self.status_code
        return self

    def set_middler_list(self, lists):
        """
        设置需要验证的步骤
        :param lists:
        :return:
        """
        if lists is not None:
            self.middler_list = lists
        return self

    def set_marks(self, marks: list):
        """
        设置验证码
        :param marks:
        :return:
        """
        self.marks = marks
        return self

    def set_timeout(self, timeout):
        """
        设置超时
        :param timeout:
        :return:
        """
        self.timeout = timeout
        return self

    def set_header(self, header):
        """
        设置header
        :return:
        """
        self.header = header
        return self

    def set_refer(self, refer):
        """
        设置header中的refer，每次请求有可能变化
        :return:
        """
        self.refer = refer
        return self

    def set_proxy(self, proxy):
        """
        设置代理
        :return:
        """
        self.proxy = proxy
        return self

    def set_url(self, url):
        """
        设置请求的url
        :return:
        """
        self.url = url
        return self

    def set_params(self, params):
        """
        get 请求参数
        :return:
        """
        self.params = params
        return self

    def set_data(self, data):
        """
        设置请求参数
        :return:
        """
        self.data = data
        return self

    def set_cookies(self, cookies):
        """
        设置cookie
        :return:
        """
        self.cookies = cookies
        return self

    def set_sn(self, sn):
        """
        设置会话
        :return:
        """
        self.sn = sn
        return self

    def close_sn(self):
        """
        关闭会话
        :return:
        """
        if self.sn is not None:
            self.sn.close()

    def builder(self):
        """
        建造成需要的对象用于接下来请求使用
        :return:
        """
        if self.refer != "":
            self.header["refer"] = self.refer

    def get(self):
        """
        get 请求
        :return:
        """
        pass

    def post(self):
        """
        post 请求
        :return:
        """

    def on_request_start(self):
        """
        请求前的钩子函数
        :return:
        """

    def on_request_end(self):
        """
        请求结束的钩子函数
        :return:
        """

    def status_code_middlerwares(self, status_code=200):
        """
        验证返回码
        :return:
        """
        if "status_code_middlerwares" in self.middler_para.keys():
            if "status_code" in self.middler_para["status_code_middlerwares"].keys():
                status_code = self.middler_para["status_code_middlerwares"]["status_code"]
        if self.status_code != status_code:
            self.resp_dicts["code"] = self.status_code
            self.resp_dicts["msg"] = "status_code err {}".format(self.status_code)
            return False, self.resp_dicts
        return True, self.resp_dicts

    def end_middlerwares(self, endstring="</html>"):
        """
        必须以什么结束
        :return:
        """
        if "end_middlerwares" in self.middler_para.keys():
            if "endstring" in self.middler_para["end_middlerwares"].keys():
                endstring = self.middler_para["end_middlerwares"]["endstring"]
        if not self.html.endswith(endstring):
            self.resp_dicts["code"] = MsgCode.END_STRING_ERROR
            self.resp_dicts["msg"] = "not endswith {}".format(endstring)
            return False, self.resp_dicts
        return True, self.resp_dicts

    def is_none_html_middlerwares(self):
        """
        空的html 在使用某些代理时 如果https 写成了http,会有这种情况
        建议所有http的网站使用这个验证器以监控网站何时变成http
        :return:
        """
        if self.html is not None:
            if len(self.html) == 0:
                self.resp_dicts["code"] = MsgCode.NONE_HTML
                self.resp_dicts["msg"] = "空的html"
                return False, self.resp_dicts
        else:
            self.resp_dicts["code"] = MsgCode.NONE_HTML
            self.resp_dicts["msg"] = "空的html"
            return False, self.resp_dicts
        return True, self.resp_dicts

    def is_null_html_middlerwares(self):
        """
        api 如果忘记return 会返回 null 字符串
        :return:
        """
        if self.html == "null":
            self.resp_dicts["code"] = MsgCode.NONE_HTML
            self.resp_dicts["msg"] = "api没有return导致返回 null"
            return False, self.resp_dicts
        return True, self.resp_dicts

    def have_end_middlerwares(self, havestring="</html>"):
        if "have_end_middlerwares" in self.middler_para.keys():
            if "havestring" in self.middler_para["have_end_middlerwares"].keys():
                havestring = self.middler_para["have_end_middlerwares"]["havestring"]

        if self.html.find(havestring) == -1:
            self.resp_dicts["code"] = MsgCode.END_STRING_ERROR
            self.resp_dicts["msg"] = "not have endswith {}".format(havestring)
            return False, self.resp_dicts
        return True, self.resp_dicts

    def marks_middlerwares(self):
        """
        建议至少两个，
        一个是id 防止因为cookie请求到其他的页面
        一个为验证该html关键词，用于改版预测
        :param marks: 一个列表
        :return:
        """
        mark_str = ""
        for mark in self.marks:
            if self.html.find(mark) == -1:
                mark_str = mark_str + mark + ";"

        if mark_str != "":
            self.resp_dicts["code"] = MsgCode.MARK_ERROR
            self.resp_dicts["msg"] = "mark Feature err: {}".format(mark_str)
            return False, self.resp_dicts
        else:
            return True, self.resp_dicts

    def is_json_middlerwares(self):
        """
        验证返回结果是否是json
        :return:
        """
        try:
            dic = json.loads(self.html)
        except Exception as e:
            self.resp_dicts["code"] = MsgCode.NOT_IS_JSON
            self.resp_dicts["msg"] = "not is json error, {}".format(repr(e))
            return False, self.resp_dicts
        return True, self.resp_dicts

    def fail_middlerwares(self):
        """
        当请求失败时,返回错误信息
        废弃这个方法 请使用msg_status_code_middlerwares
        :return:
        """
        try:
            dic = json.loads(self.html)
            if dic["status"] == "SUCCESS":
                return True, self.resp_dicts
            else:
                self.resp_dicts["code"] = MsgCode.STATUS_ERROR
                self.resp_dicts["msg"] = "Status error"
                return False, self.resp_dicts
        except Exception as e:
            self.resp_dicts["code"] = MsgCode.NOT_IS_JSON
            self.resp_dicts["msg"] = "not is json error, {}".format(repr(e))
            return False, self.resp_dicts

    def msg_status_code_middlerwares(self, status=["SUCCESS"], msg_code=[200]):
        """
        status 和 msg_code 错误拦截
        :return:
        """
        if "msg_status_code_middlerwares" in self.middler_para.keys():
            if "status" in self.middler_para["msg_status_code_middlerwares"].keys():
                status = self.middler_para["msg_status_code_middlerwares"]["status"]
            if "msg_code" in self.middler_para["msg_status_code_middlerwares"].keys():
                msg_code = self.middler_para["msg_status_code_middlerwares"]["msg_code"]
        try:
            dic = json.loads(self.html)
            if dic["status"] not in status:
                self.resp_dicts["code"] = MsgCode.STATUS_ERROR
                self.resp_dicts["msg"] = "error, {}".format(self.html)
                return False, self.resp_dicts
            if dic["msg_code"] not in msg_code:
                self.resp_dicts["code"] = MsgCode.CODE_ERROR
                self.resp_dicts["msg"] = "error data code, {}".format(dic["msg_code"])
                return False, self.resp_dicts
        except Exception as e:
            self.resp_dicts["code"] = MsgCode.NOT_IS_JSON
            self.resp_dicts["msg"] = "not is json error, {}".format(repr(e))
            return False, self.resp_dicts
        return True, self.resp_dicts
