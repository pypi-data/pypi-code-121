from markupsafe import escape
from markupsafe import Markup
从 汉化通用 导入 _反向注入

套路 转义(对象):
    返回 escape(对象)

类 〇标记(Markup):

    套路 连接(分身, 序列):
        返回 分身.join(序列)
    
    套路 分割(分身, 分隔符=空, 最大分割次数=-1):
        返回 分身.split(sep=分隔符, maxsplit=最大分割次数)
    
    套路 右分割(分身, 分隔符=空, 最大分割次数=-1):
        返回 分身.rsplit(sep=分隔符, maxsplit=最大分割次数)
    
    套路 划分(分身, 分隔符):
        返回 分身.partition(分隔符)
    
    套路 右划分(分身, 分隔符):
        返回 分身.rpartition(分隔符)
    
    套路 分行(分身, 保留换行符=假):
        返回 分身.splitlines(保留换行符)
    
    套路 格式化(分身, *参数々, **关键词参数々):
        返回 分身.format(*参数々, **关键词参数々)

    套路 取消转义(分身):
        返回 分身.unescape()
    
    套路 去除标签(分身):
        返回 分身.striptags()
    
    @classmethod
    套路 转义(本类, 字符串):
        返回 本类.escape(字符串)

_反向注入(〇标记, Markup)