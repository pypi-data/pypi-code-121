# 工具箱中的工具都是开箱即用的，不依赖特别的数据、配置和业务逻辑
__author__ = 'zhangkun'

from sometools.sync_tools.string_tools import StringMixIn
from sometools.sync_tools.log_tools import LogMixIn
from sometools.sync_tools.datetime_tools import DatetimeMixIn
from sometools.sync_tools.chinese_to_pinyin_acronym import ChineseToPinyinMixIn
from sometools.sync_tools.traditional_simplified_chinese_conversion import TraditionalSimplifiedChineseMixIn
from sometools.sync_tools.url_tools import UrlEncodeDecodeMixIn
from sometools.sync_tools.redis_tools import RedisMixIn
from sometools.sync_tools.re_tools import ExtractStringMixIn
from sometools.sync_tools.image_tools import ImageMixin
from sometools.sync_tools.char_tools import CharMixin
from sometools.sync_tools.os_tools import OsMixin
from sometools.sync_tools.ip_tools import IpMixIn
from sometools.sync_tools.calendar_tools import CalendarMixIn


class Common_tools(ChineseToPinyinMixIn, TraditionalSimplifiedChineseMixIn, UrlEncodeDecodeMixIn, DatetimeMixIn,
                   StringMixIn, IpMixIn, CalendarMixIn, ImageMixin, CharMixin, ExtractStringMixIn, OsMixin, LogMixIn, RedisMixIn):
    def __init__(self, *args, **kwargs):
        super(Common_tools, self).__init__(*args, **kwargs)
