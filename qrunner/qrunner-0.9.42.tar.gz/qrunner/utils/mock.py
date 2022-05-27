import time
from qrunner.utils.faker import Faker
from qrunner.utils.log import logger

"""
可用的mock方法见：https://zhuanlan.zhihu.com/p/87203290
"""


# 兼容老版本
mock = Faker('zh_CN')
mock_en = Faker()


# 建议使用
class RandomData(Faker):
    """随机数据"""

    def __init__(self, language='中文'):
        if language == '中文':
            locale = 'zh_CN'
            super().__init__(locale=locale)
        elif language == '英文':
            super().__init__()
        else:
            logger.debug(f'暂不支持这种语言-{language}')

    def get_word(self):
        """随机词语"""
        return self.word()

    def get_words(self):
        """随机词语列表"""
        return self.words()

    def get_phone(self):
        """随机手机号"""
        return self.phone_number()

    def get_company_name(self):
        """随机公司名"""
        return self.company()

    def get_name(self):
        """随机人名"""
        return self.name()

    def get_timezone(self):
        """随机时区"""
        return self.timezone()

    def get_date(self):
        """随机日期"""
        return self.date()

    def get_number(self, length=3):
        """随机数"""
        return self.random_number(digits=length)

    def get_ssn(self):
        """随机身份证号"""
        return self.ssn()

    def get_email(self):
        """随机邮箱"""
        return self.email()

    def get_url(self):
        """随机url地址"""
        return self.url()


class CommonData:
    """其它常用数据"""

    @staticmethod
    def get_timestamp(length=None) -> str:
        """获取当前时间戳"""
        timestamp = str(int(time.time()))
        if length is None:
            return timestamp
        else:
            return timestamp.ljust(length, '0')

    @staticmethod
    def get_date(_format="%Y-%m-%d"):
        """获取当前日期"""
        return time.strftime(_format)

    @staticmethod
    def get_now_time(_format="%Y-%m-%d %H:%M:%S"):
        """获取当前时间"""
        return time.strftime(_format)












