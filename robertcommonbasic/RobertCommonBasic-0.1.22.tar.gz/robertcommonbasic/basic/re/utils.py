import re
from typing import Any
from datetime import datetime

#检测ip是否正确
def check_is_ip(ip: str):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    return False

#格式化数字字母以外的字符 \u4e00-\u9fa5_
def format_name(name: str, pattern: str=r'[^a-zA-Z0-9_]+', replace: str='_'):
    if name is None:
        return ''
    else:
        return re.sub(r'^_|_$', '', re.sub(pattern, replace, name.strip()))

def format_value(value: Any, mapping: dict={}, decimal: int=3):
    if isinstance(value, str):
        return format_value(mapping.get(value, value), mapping, decimal)
    elif isinstance(value, float):
        value = f"{value: .{decimal}f}"
        return f"{float(value): g}"
    elif isinstance(value, datetime):
        return datetime.strptime('%Y-%m-%d %H:%M:%S')
    elif isinstance(value, bool):
        return 1 if value else 0
    elif isinstance(value, int):
        return value
    return str(value)