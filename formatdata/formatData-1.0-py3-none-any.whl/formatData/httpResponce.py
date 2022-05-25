# Create your views here.
"""
The best sentence

1 Don’t hate your enemy, or you will make wrong judgment.
2 I'm gonna make him an offer he can't refuse.
3 A friend should always underestimate your virtues and an enemy overestimate your faults.
4 You know...the world’s full of lonely people afraid to make the first move
5 I suffer that slight alone,because I’m not accepted by my own people,
    because i’m not like them either! So if I'm not black enough and if I'm not white enough,
    then tell me, Tony, what am I !?
6 whatever you do,do it a hundred percent.when you work,when you laugh,laugh,when you eat,eat like it's your last meal.

@author:StrongXiuXiu
@file:
@time:2021/10/11
"""
import datetime


class DataFormatBase:
    """
        一个基础的数据返回模板，用于返回json字符串结构给到前端
        包含可以调控的 status_code 错误识别码
    """
    status_code = 1  # code类型为1时，操作成功 0 失败

    def __init__(
            self,
            code=None,
            ch_message=None,
            en_message="eng",
            data=None,
            serialize=False):
        self._result = {}
        self._en_message = en_message  # 英文注释
        self._ch_message = ch_message  # 中文注释
        self._data = data  # body内容
        self._code = code  # 返回状态
        self.time = self.gettime()
        self.serialize = serialize

    def __repr__(self):
        return '<%(cls)s chMessage=%(chMessage)s%(data)s code=%(code)s>' % {
            'cls': self.__class__.__name__,
            'chMessage': self._ch_message,
            'data': self._data,
            'code': self.status_code}

    @property
    def chMessage(self):
        """返回中文错误信息"""
        if self._ch_message is not None:
            return self._ch_message
        return " 未设置返回信息 <<< No Settings information"

    @chMessage.setter
    def chMessage(self, value):
        """生成中文错误信息"""
        self._ch_message = value

    @property
    def data(self):
        """返回数据data数据资源"""

        if self._data is not None:
            return self._data
        return '[]'

    @data.setter
    def data(self, value):
        """生成data数据"""
        self._data = value

    @property
    def code(self):
        """返回错误信息验证码，唯一标识识别码"""
        if self._code is not None:
            if isinstance(self._code, int):
                return self._code
            else:
                raise MyError("code格式错误,code必须为int型")
        return 1

    @code.setter
    def code(self, value):
        """生成code"""
        self._code = value

    def joint(self):
        """
            拼接完整的http协议内的body数据包，包含
            code,chMessage,Message,enMessage,data,createTime
        """
        if self._code is not None:
            self._result["code"] = self.code
        else:
            self._result["code"] = self.status_code
        self._result["chMessage"] = self.chMessage
        self._result["msg"] = self.chMessage  # 预留的一个字段，需改进！
        self._result["enMessage"] = self._en_message
        if self.serialize:
            self._result["data"] = self._serialize(self._data)
        else:
            self._result["data"] = self._data
        self._result["createTime"] = str(self.time)
        return self._result

    def _make_enMessage(self):
        """
            这个位置准备使用第三方模块进行中英互换，目前还没有加入该模块
        """
        return self._en_message is not None

    def gettime(self):
        """获取一个当前时间，并且以年月日时分秒进行规范化转译"""
        dt = datetime.datetime.now()
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def _serialize(self, data):
        """ 序列化data数据"""
        _data = []
        if isinstance(data, dict):
            return self._serialize_dict(data)
        for i in data:
            _data.append(i)
        return _data

    def _serialize_dict(self, data):
        _data = []
        for k, v in data.items():
            data_dict = {}
            if isinstance(v, (int, str)):
                data_dict[k] = v
            else:
                data_dict[k] = self._serialize(v)
            _data.append(data_dict)
        return _data


class SuccessDataFormat(DataFormatBase):
    """
        这是一个成功信息模板的集合，代表操作成功
        操作成功即可调用该模块,继承了数据模板基类
    """
    status_code = 1

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    @staticmethod
    def serialize(data):
        """ 序列化data数据"""
        _data = []
        for i in data:
            _data.append(i)
        return _data

    def result(self):
        return self.joint()


class ErrorDataFormat(DataFormatBase):
    """
        这是一个失败信息模板的集合，代表操作失败
        操作失败即可调用该模块,继承了数据模板基类
    """
    status_code = 0

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    def result(self):
        return self.joint()


class ExceptionDataFormat(DataFormatBase):
    """
        这是一个异常信息模板的集合，代表操作发现异常
        操作产生异常时即可调用该模块，,继承了数据模板基类
    """
    status_code = 2

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    def result(self):
        return self.joint()
