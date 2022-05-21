import ast
import json5
import re


def is_column_sql(sql_line: str):
    """
    判断一个SQL行是否是合法的列定义SQL
    """
    return not sql_line.strip().upper().startswith(('PRIMARY ', 'KEY ', 'CONSTRAINT ', 'UNIQUE '))


def parse_column_sql(sql_line: str):
    """
    返回：col_name, sql_type, comment
    """
    sql_line = sql_line.strip().rstrip(',')
    if ' COMMENT ' in sql_line:
        sql_line, comment_part = sql_line.split(' COMMENT ', 1)
        comment = ast.literal_eval(comment_part)
    else:
        comment = ''
    col_name, sql_type = sql_line.split(None, 2)[:2]
    col_name = col_name.strip('`')
    return col_name, sql_type, comment


def guess_mockjs(sql_type, name, comment):
    if sql_type.startswith(('enum', 'ENUM')):
        return sql_type.replace('enum', '@pick').replace('ENUM', '@pick')
    sql_type = sql_type.lower()
    if sql_type == 'date':
        return '@date'
    elif sql_type == 'datetime':
        return '@datetime'
    elif sql_type.startswith('bigint'):
        return '@natural'
    elif sql_type.startswith('int'):
        return '@integer(0, 1000000)'
    elif sql_type.startswith('double'):
        return '@float(0, 100)'
    elif sql_type.startswith('enum'):
        return sql_type.replace('enum', '@pick')
    elif '是否' in comment:
        return '@boolean'
    elif comment.endswith(('姓名', '人', '者')):
        return '@cname'
    elif name.lower().endswith(('phone', 'mobile')):
        return '1@integer(3000000000, 9900000000)'
    elif name.lower().endswith('ipaddress') or comment.lower().endswith('ip地址'):
        return '@ip'
    elif name.lower().endswith('address') or comment.endswith('地址'):
        return '@county@cword(2)街@integer(1,100)号@cword(4)小区'
    elif name.lower().endswith('code'):
        return '@word(16)'
    elif name.lower().endswith(('title', 'name')):
        return '@cword(6)'
    else:
        return ''


def guess_java_type(mockjs):
    if isinstance(mockjs, bool):
        return 'Boolean'
    elif isinstance(mockjs, int):
        return 'Integer'
    elif isinstance(mockjs, float):
        return 'Double'
    elif isinstance(mockjs, list):
        subtype = 'String' if not mockjs else guess_java_type(mockjs[0])
        return f'List<{subtype}>'
    elif isinstance(mockjs, dict):
        return 'JSONObject'
    elif mockjs.startswith('@natural'):
        return 'Long'
    elif mockjs.startswith('@float'):
        return 'Double'
    elif mockjs.startswith('@datetime'):
        return 'LocalDateTime'
    elif mockjs.startswith('@date'):
        return 'LocalDate'
    elif mockjs.startswith('@pick'):
        return 'String'  # 后续再优化
    else:
        return 'String'


def sql_type_guess_java_type(sql_type, comment):
    sql_type = sql_type.lower()
    if sql_type == 'date':
        return 'LocalDate'
    elif sql_type == 'datetime':
        return 'LocalDateTime'
    elif sql_type == 'json':
        return 'List<String>'  # 后续改进
    elif sql_type.startswith('bigint'):
        return 'Long'
    elif sql_type.startswith('int'):
        return 'Integer'
    elif sql_type.startswith('enum'):
        return 'String'  # 后续改进
    elif sql_type.startswith('tinyint') and '是否' in comment:
        return 'Boolean'
    else:
        return 'String'


def parse_json5(json5_content: str):
    """
    返回：(data, comment_dict)
    """
    data = json5.loads(json5_content)
    comment_dict = {}
    for line in json5_content.splitlines():
        line = line.strip()
        if '//' in line and (match_ret := re.match(r'"([\w.-]+)" *:', line)):
            key = match_ret.groups()[0]
            if key not in comment_dict:
                comment_dict[key] = line.rsplit('//', 1)[-1]
    return data, comment_dict


def judge_class_name(class_name, suffix):
    assert class_name and class_name[0].isupper() and '_' not in class_name, '类名必须是大写字母开头的驼峰命名'
    assert class_name.endswith(suffix), f'类名后缀必须是{suffix}'
