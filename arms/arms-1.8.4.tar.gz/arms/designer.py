from lesscli import add_subcommand
from arms.utils.grammar import is_column_sql, parse_column_sql, guess_mockjs
from arms.utils.templates import render_sql_line, render_create_sql_frame, render_json5, \
    render_yapi_query, render_interface_query_body
from arms.utils.wordstyle import word_to_style, WordStyle
from InquirerPy import inquirer
import pyperclip
import re
from rich.console import Console
from rich.syntax import Syntax


console = Console()


def copy_board():
    """
    展示当前的粘贴板内容（不超过1000行和10KB），
    选择确认/放弃
    选确认则返回粘贴板内容
    """
    splitor_start = '─────────────────────────'
    splitor_end = '───────────────────────────'
    content = pyperclip.paste()
    if len(content.splitlines()) > 1000 or len(content) > 10240:
        content = '（粘贴板内容超过了1000行或10KB）'
    content = content.strip()
    answer = inquirer.select(
        message=splitor_start + '\n' + content + '\n' + splitor_end,
        choices=['确认使用粘贴板内容', '放弃'],
        default=None,
    ).execute()
    if answer == '放弃':
        exit(0)
    return content


def design_shimo_to_sql():
    """
    复制石墨表格，转换成建表SQL，保存到粘贴板
    石墨表格的格式：字段名(驼峰)、类型(SQL)、注释
    """
    shimo_content = copy_board()
    camel_stype = inquirer.select(
        message="请选择数据库字段风格",
        choices=['蛇形', '驼峰'],
        default=None,
    ).execute() == '驼峰'
    table_name = inquirer.text(message="请输入数据库表名:").execute()
    table_comment = inquirer.text(message="请输入表的中文注释:").execute()
    sql_lines = []
    primary_key = ''
    for pos, row in enumerate(shimo_content.splitlines()):
        seg_size = len(segs := row.split('\t'))
        assert seg_size == 3, f'第{pos+1}行包含{seg_size}列，应该包含3列'
        name, sql_type, comment = segs
        assert sql_type, f'第{pos + 1}行的第2列(sql_type)不能为空'
        if not camel_stype:
            col_name = word_to_style(name, WordStyle.lower_snake)
        else:
            col_name = name
        if pos == 0:
            primary_key = col_name
        mockjs = guess_mockjs(sql_type, name, comment)
        sql_lines.append(render_sql_line(col_name, sql_type, comment, mockjs, pos == 0))
    sql_content = render_create_sql_frame(table_name, table_comment, primary_key, sql_lines)
    print('创建数据库的SQL如下：')
    console.print(Syntax(sql_content, 'sql'))
    pyperclip.copy(sql_content)
    print('已复制到粘贴板！')


def design_sql_to_shimo():
    """
    复制建表SQL，转换成石墨表格，保存到粘贴板
    石墨表格的格式：字段名(驼峰)、类型(SQL)、注释
    """
    sql_content = copy_board()
    seed = re.compile(r'CREATE TABLE *`?(\w+)`? *\((.*)\)', flags=re.I|re.DOTALL)
    match_size = len(find_ret := seed.findall(sql_content))
    assert match_size == 1, '无法解析该建表SQL'
    table_name, sql_body = find_ret[0]
    shimo_lines = []
    for sql_line in sql_body.splitlines():
        if sql_line and is_column_sql(sql_line):
            col_name, sql_type, comment = parse_column_sql(sql_line)
            name = word_to_style(col_name, WordStyle.lower_camel)
            shimo_line = '\t'.join([name, sql_type, comment])
            shimo_lines.append(shimo_line)
    shimo_content = '\n'.join(shimo_lines)
    print('定义实体的石墨文本如下：')
    console.print(Syntax(shimo_content, 'text'))
    pyperclip.copy(shimo_content)
    print('已复制到粘贴板！')


def design_shimo_to_json5():
    """
    复制石墨表格，转化为json5，保存到粘贴板
    石墨表格的格式：字段名(驼峰)、类型(SQL)、注释
    """
    shimo_content = copy_board()
    shimo_rows = []
    for pos, row in enumerate(shimo_content.splitlines()):
        seg_size = len(segs := row.split('\t'))
        assert seg_size == 3, f'第{pos + 1}行包含{seg_size}列，应该包含3列'
        name, sql_type, comment = segs
        assert sql_type, f'第{pos + 1}行的第2列(sql_type)不能为空'
        mockjs = guess_mockjs(sql_type, name, comment)
        shimo_rows.append((name, sql_type, mockjs, comment))
    tpl_type = inquirer.select(
        message='请选择结果模版:',
        choices=['保持原状', '返回普通对象模版', '返回数组对象(无分页)模版', '分页返回对象模版'],
        default=None,
    ).execute()
    json5_content = render_json5(shimo_rows, tpl_type)
    print('json5内容如下：')
    console.print(Syntax(json5_content, 'json'))
    pyperclip.copy(json5_content)
    print('已复制到粘贴板！')


def design_shimo_to_query():
    """
    复制石墨表格，转化为YAPI文本或JAVA代码，保存到粘贴板
    石墨表格的格式：字段名(驼峰)、类型(SQL)、注释
    YAPI批量添加Query文本的格式：name:example（只能把注释放到example的位置）
    """
    shimo_content = copy_board()
    shimo_rows = []
    for pos, row in enumerate(shimo_content.splitlines()):
        seg_size = len(segs := row.split('\t'))
        assert seg_size == 3, f'第{pos + 1}行包含{seg_size}列，应该包含3列'
        shimo_rows.append(segs)
    answer = inquirer.select(
        message='请选择分页请求参数：',
        choices=['pageNum & numPerPage', '不需分页'],
        default=None,
    ).execute()
    lang_type = inquirer.select(
        message='请选择输出格式：',
        choices=['YAPI批量添加Query', 'JAVA请求参数'],
        default=None,
    ).execute()
    if answer == 'pageNum & numPerPage':
        yapi_query_content = 'pageNum:当前页码，从1开始\nnumPerPage:分页大小\n'
        java_query_content = ',\n        @Valid @ParameterObject PageReq pageReq'
    else:
        yapi_query_content = ''
        java_query_content = ''
    if 'YAPI' in lang_type:
        yapi_query_content += render_yapi_query(shimo_rows)
        print('YAPI批量添加Query文本如下：')
        console.print(Syntax(yapi_query_content, 'text'))
        pyperclip.copy(yapi_query_content)
    else:
        req_query = [{'name': name, 'required': '0', 'desc': comment} for name, sql_type, comment in shimo_rows]
        java_query_content = render_interface_query_body('', req_query) + java_query_content
        print('JAVA请求参数的代码如下：')
        console.print(Syntax(java_query_content, 'java'))
        pyperclip.copy(java_query_content)
    print('已复制到粘贴板！')


def design_sql_join():
    """
    复制多个建表SQL，转换成联合查询SQL，保存到粘贴板
    需要select的字段前加上前缀「out_name:」，相同out_name的默认会join
    """
    sql_content = pyperclip.paste()
    seed = re.compile(r'CREATE TABLE *`?(\w+)`? *\((.*?)\) ENGINE=InnoDB', flags=re.I|re.DOTALL)
    find_ret = seed.findall(sql_content)
    assert find_ret, f'无法解析粘贴板的建表SQL：{repr(sql_content[:100])}...'
    col_index = {}  # dict[col_name: table_name]
    select_list = []
    where_table = ''
    join_list = []
    for table_name, sql_body in find_ret:
        if not where_table:
            where_table = table_name
        for sql_line in sql_body.splitlines():
            if sql_line and is_column_sql(sql_line):
                col_name, sql_type, comment = parse_column_sql(sql_line)
                if col_name.count('`') == 1:
                    col_name += '`'
                elif col_name.endswith(':'):
                    col_name += sql_type
                out_name = ''
                if col_name.startswith(':'):
                    out_name = col_name = col_name.lstrip(':')
                    select_list.append(f'{table_name}.{col_name}')
                elif ':' in col_name:
                    out_name, col_name = col_name.split(':', 1)
                    out_name = f'`{out_name}`'
                    select_list.append(f'{table_name}.{col_name} AS {out_name}')
                if out_name:
                    if out_name in col_index:
                        left_table_name, left_col_name = col_index[out_name]
                        join_list.append(f'LEFT JOIN {table_name} ON {table_name}.{col_name}={left_table_name}.{left_col_name}')
                    else:
                        col_index[out_name] = table_name, col_name
    assert select_list, '提示：需要select的字段前加上前缀「out_name:」或「:」，相同out_name的默认会join'
    sql_result = 'SELECT '
    sql_result += ','.join(select_list) + '\n'
    sql_result += f'FROM {where_table} \n'
    sql_result += ' \n'.join(join_list)
    console.print(Syntax(sql_result, 'sql'))
    pyperclip.copy(sql_result)
    print('已复制到粘贴板！')


@add_subcommand('shimo-to-sql', design_shimo_to_sql)
@add_subcommand('sql-to-shimo', design_sql_to_shimo)
@add_subcommand('shimo-to-json5', design_shimo_to_json5)
@add_subcommand('shimo-to-query', design_shimo_to_query)
@add_subcommand('sql-join', design_sql_join)
def run_design():
    """生成文本并复制"""
    pass
