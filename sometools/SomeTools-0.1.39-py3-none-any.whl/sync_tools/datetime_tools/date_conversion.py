"""无脑处理时间（兼容各种类型和格式互转）"""

# 时区
# https://blog.csdn.net/x356982611/article/details/90296245

# %代号
# https://blog.csdn.net/cunchi4221/article/details/107475858
# %a 英文星期简写
# %A 英文星期的完全
# %b 英文月份的简写
# %B 英文月份的完全
# %c 显示本地日期时间
# %d 日期，取1-31
# %H 小时， 0-23
# %I 小时， 0-12
# %m 月， 01 -12
# %M 分钟，1-59
# %j 年中当天的天数
# %w 显示今天是星期几
# %W 第几周
# %x 当天日期
# %X 本地的当天时间
# %y 年份 00-99间
# %Y 年份的完整拼写


import re
import datetime
from datetime import timedelta
from sometools.sync_tools.base import Base

_datetime_fmt_list = ['%Y-%m-%d %H:%M:%S',
                      "%Y-%m-%dT%H:%M:%S.%fZ",
                      '%Y-%m-%d %H:%M:%S',
                      '%Y-%m-%d %H:%M',
                      '%Y-%m-%d  %H:%M',
                      '%Y-%m-%d%H:%M:%S',
                      '%Y-%m-%d',
                      '(%m-%d %H:%M)',
                      '（%Y年%m月%d日）',
                      '(%Y-%m-%d)',
                      '(%m-%d)',
                      '%Y/%m/%d %H:%M:%S',
                      '%Y/%m/%d %H:%M',
                      '[%Y/%m/%d%H:%M]',
                      '[%Y/%m/%d %H:%M]',
                      '%Y/%m/%d',
                      '%Y%m%d',
                      '%d/%m/%Y %H:%M',
                      '%d-%b-%Y%H:%M',
                      '%d-%b-%Y %H:%M ',
                      '    (%m/%d %H:%M)',
                      '%m/%d',
                      '%m/%d/%Y %H:%M:%S',
                      '%d-%Y %H:%M',
                      '%d/%Y %H:%M',
                      '%d %b %Y',
                      '时间：%Y-%m-%d',
                      '时间：%Y-%m-%d %H:%M:%S',
                      '时间：%Y-%m-%d %H:%M',
                      '[%Y-%m-%d]',
                      '发布时间：%Y-%m-%d',
                      '发布日期：%Y-%m-%d',
                      '更新日期：%Y-%m-%d',
                      '更新时间：%Y-%m-%d',
                      '发布时间：%Y-%m-%d %H:%M:%S',
                      '更新时间：%Y-%m-%d %H:%M:%S',
                      '更新日期：%Y-%m-%d %H:%M:%S',
                      '发布时间：%Y-%m-%d %H:%M',
                      '%Y-%m-%dT%H:%M:%S+00:00',
                      '【%Y-%m-%d】',
                      '创建日期：%Y-%m-%d',
                      '公开时间：%Y-%m-%d',
                      '%d%b%Y',
                      '%Y年%m月',
                      '%Y年%m月%d日',
                      '%Y.%m.%d',
                      '%Y-%m',
                      '(%m月%d日 %H:%M)',
                      '%Y年%m月%d日%H：%M',
                      '1',
                      '%d-%m-%Y',
                      ' %Y年%m月%d日  %H:%M',
                      '(%Y年%m月%d日 %H:%M)',
                      '%m-%d %H:%M',
                      '%m-%d',
                      '%m/%d',
                      '%Y年%m月%d日资金市场日评',
                      '%m月%d日 %H:%M',
                      '%Y年%m月%d日 %H:%M',
                      '%m/%d %H:%M',
                      '[%m月%d日 %H:%M]',
                      '[ %Y年%m月%d日 ]',
                      '%Y-%m-%d %H:%M 来源：',
                      '%Y年%m月%d日%H:%M | 来源：',
                      '[%m月%d日]',
                      'crtime=%Y-%m-%d;document.write(crtime);',
                      '%Y年%m月%d日  %A',
                      'None',
                      '%d%Y-%m',
                      '%d%B%Y',
                      "crtime= '%Y-%m-%d';\r\n"
                      '  \t                \r\n'
                      '  \t                    document.write(crtime);',
                      '大公信用%Y年第%m期',
                      'Expired: %Y-%m-%d',
                      '%Y %m月 %d',
                      '%H:%M:%S',
                      '%d %b %Y',
                      '%B %d, %Y',
                      '%B %Y',
                      '今天 %M:%S',
                      '时间：%Y年%m月%d日 %H:%M:%S&nbsp中财网',
                      '%m-%b-%Y %H:%M',
                      ]


class DatetimeMixIn(Base):
    def __init__(self, *args, **kwargs):
        super(DatetimeMixIn, self).__init__(*args, **kwargs)

    @classmethod
    def str_to_obj(self, datetime_str: str, change_future_time: bool = False) -> datetime.datetime:
        """
        字符串转为datetime对象
        :param datetime_str: str
        :param change_future_time: bool
        :return: datetime.datetime
        """
        assert isinstance(datetime_str, str)
        if not hasattr(self, 'clean_string_5_space_limit'):
            from sometools.sync_tools.string_tools import StringMixIn
            self.clean_string_5_space_limit = StringMixIn().clean_string_5_space_limit
        if not hasattr(self, 'clean_string_5_space_limit'):
            from sometools.sync_tools.string_tools import StringMixIn
            self.clean_string = StringMixIn().clean_string

        # 1. 处理常见时间文字描述
        _now_date_time = datetime.datetime.now()
        datetime_str = self.clean_string_5_space_limit(datetime_str)
        if datetime_str in ['昨天', '1天前']:
            return _now_date_time - timedelta(days=1)
        if '昨天' in datetime_str:
            return _now_date_time - timedelta(days=1)

        if datetime_str in ['前天', '2天前']:
            return _now_date_time - timedelta(days=2)
        if '前天' in datetime_str:
            return _now_date_time - timedelta(days=2)

        if datetime_str in ['大前天', '3天前']:
            return _now_date_time - timedelta(days=3)
        if '小时前' in datetime_str:
            if datetime_str.endswith('小时前'):
                if ':' in datetime_str:
                    temp_str = datetime_str.replace('小时前', '')
                    temp_str = temp_str.split(':')[-1]
                else:
                    temp_str = datetime_str.replace('小时前', '')
                return _now_date_time - timedelta(hours=int(temp_str))
        if '分钟前' in datetime_str:
            if datetime_str.endswith('分钟前'):
                if ':' in datetime_str:
                    temp_str = datetime_str.replace('分钟前', '')
                    temp_str = temp_str.split(':')[-1]
                else:
                    temp_str = datetime_str.replace('分钟前', '')
                return _now_date_time - timedelta(minutes=int(temp_str))
        if '天前' in datetime_str:
            if datetime_str.endswith('天前'):
                if ':' in datetime_str:
                    temp_str = datetime_str.replace('天前', '')
                    temp_str = temp_str.split(':')[-1]
                else:
                    temp_str = datetime_str.replace('天前', '')
                return _now_date_time - timedelta(days=int(temp_str))
        if '刚刚' in datetime_str:
            return _now_date_time
        if '今天' in datetime_str:
            return _now_date_time

        if len(datetime_str) >= 10:
            try:
                return datetime.datetime.fromtimestamp(float(datetime_str[:10]))
            except:
                pass

        # 2. 处理带时区的缩写的 step1
        # EDT（Eastern Daylight Timing）指美国东部夏令时间。东部时区慢北京时间12小时。
        # GMT Greenwich Mean Time 格林尼治标准时间 北京时区比GMT快8个小时
        # EST eastern standard time (美国)东部标准时间  慢北京时间 13个小时。
        time_zone_dict = {'EDT': 12,
                          'EST': 13,
                          'GMT': 8, }
        timze_zone_timedelta = 0
        for str_key, str_valeu in time_zone_dict.items():
            if str_key in datetime_str:
                datetime_str = datetime_str.replace(str_key, '')
                timze_zone_timedelta = str_valeu
                break

        # 开始匹配转换字符串到对象
        p_date = None
        for _temp_index, fmt in enumerate(_datetime_fmt_list):
            try:
                p_date = datetime.datetime.strptime(self.clean_string_5_space_limit(datetime_str), self.clean_string_5_space_limit(fmt))
                break
            except Exception as e:
                if _temp_index == len(_datetime_fmt_list) - 1:
                    mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", datetime_str)
                    if mat:
                        datetime_str = mat.groups()[0]
                        p_date = datetime.datetime.strptime(datetime_str, '%Y-%m-%d')
                    mat = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)", datetime_str)
                    if mat:
                        datetime_str = mat.groups()[0]
                        p_date = datetime.datetime.strptime(datetime_str, '%Y年%m月%d日')
                else:
                    pass
        if not p_date:  # 如果保留部分空格拿不到日期，那么就去掉所有的空格去进行匹配
            for _temp_index, fmt in enumerate(_datetime_fmt_list):
                try:
                    p_date = datetime.datetime.strptime(self.clean_string(datetime_str),
                                                        self.clean_string(fmt))
                    break
                except Exception as e:
                    if _temp_index == len(_datetime_fmt_list) - 1:
                        mat = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", datetime_str)
                        if mat:
                            datetime_str = mat.groups()[0]
                            p_date = datetime.datetime.strptime(datetime_str, '%Y-%m-%d')
                        mat = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)", datetime_str)
                        if mat:
                            datetime_str = mat.groups()[0]
                            p_date = datetime.datetime.strptime(datetime_str, '%Y年%m月%d日')
                    else:
                        pass
        if p_date:
            # 2. 处理带时区的缩写的 step2
            p_date = p_date + timedelta(hours=timze_zone_timedelta)

            # 不带年的加上年
            if p_date.year == 1900:
                p_date = p_date.replace(year=_now_date_time.year)
            if change_future_time:
                # 未来判定,转为过去
                if p_date.year == _now_date_time.year:
                    if p_date.month > _now_date_time.month:
                        p_date = p_date.replace(year=_now_date_time.year - 1)
                    if p_date.month == _now_date_time.month:
                        if p_date.day > _now_date_time.day:
                            p_date = p_date.replace(year=_now_date_time.year - 1)
            return p_date

    @staticmethod
    def obj_to_str(datetime_obj: datetime.datetime, datetime_format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        datetime对象转为字符串
        :param datetime_obj: datetime.datetime
        :return: str
        """
        try:
            assert isinstance(datetime_obj, datetime.datetime)
        except Exception as e:
            print(datetime_obj)
            print(e)
            return ''
        return datetime.datetime.strftime(datetime_obj, datetime_format_str)

    @staticmethod
    def timestamp_int_to_obj(timestamp_int: int) -> datetime.datetime:
        """
        时间戳转为datetime对象
        :param timestamp_int: int
        :return: datetime.datetime
        """
        assert isinstance(timestamp_int, int)
        return datetime.datetime.fromtimestamp(timestamp_int)
