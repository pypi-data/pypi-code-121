from sometools.sync_tools.base import Base

class StringMixIn(Base):

    def __init__(self, *args, **kwargs):
        super(StringMixIn, self).__init__(*args, **kwargs)

    @staticmethod
    def clean_string(temp_string: str) -> str:
        """
        去掉空格回车换行等
        :param temp_string: str
        :return: str
        """
        if temp_string:
            _temp_str = ''.join(temp_string).replace(' ', '').replace('\r', '').replace('\n', '').replace('\t', '').replace('\\r', '').replace('\\n', '').replace('\\t', '')
            return str(_temp_str.strip())
        else:
            return ''

    @staticmethod
    def clean_string_without_space(temp_string: str) -> str:
        """
        去掉回车换行等但是保留空格
        :param temp_string: str
        :return: str
        """
        if temp_string:
            _temp_str = ''.join(temp_string).replace('\r', '').replace('\n', '').replace('\t', '').replace('\\r', '').replace('\\n', '').replace('\\t', '')
            return str(_temp_str.strip())
        else:
            return ''

    @staticmethod
    def clean_string_5_space_limit(temp_string: str) -> str:
        """
        空格小于5个才保留空格,酌情添加,给日期使用，避免干掉全部空格等导致'2021-12-3 19:48:22'变为 '2021-12-319:48:22'以至于时间格式化出错的情况
        :param temp_string: str
        :return: str
        """
        if temp_string:
            if ' ' in temp_string and temp_string.count(' ') < 5:
                return StringMixIn.clean_string_without_space(temp_string)
            else:
                return StringMixIn.clean_string(temp_string)
        else:
            return ''
