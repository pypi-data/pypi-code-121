from lesscli import add_subcommand
from arms.utils.wordstyle import word_to_style, WordStyle
from arms.utils.grammar import parse_json5, guess_java_type, judge_class_name, is_column_sql, parse_column_sql, \
    sql_type_guess_java_type
from arms.utils.templates import render_java_vo_body, render_java_vo_frame, render_java_postkind_interface, \
    render_java_pagekind_interface, render_java_getkind_interface, render_java_controller_frame, \
    render_java_entity_body, render_java_entity_frame, \
    render_java_service_impl_body, render_java_service_body, render_java_mapper_body, make_interface_name
from InquirerPy import inquirer
import json
import os
from pathlib import Path
import pyperclip
import re
import requests
from rich.console import Console
from arms.utils.wordstyle import word_to_style

console = Console()


def blank_func():
    pass


def alert_and_exit(text):
    console.print(text.replace('[', '\\['), style="bold red")
    exit(1)


def makedir(dir_path):
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def get_mockjs_item(data, key):
    for k in data.keys():
        if k == key or k.startswith(f'{key}|'):
            return data[k]
    return data[key]  # 抛出KeyError


def find_dto_data(obj):
    data = get_mockjs_item(obj, 'data')
    if 'totalCount' in data and 'currentPage' in data and 'numPerPage' in data:
        return get_mockjs_item(data, 'recordList')[0]
    elif isinstance(data, list):
        return data[0]
    else:
        return data


def parse_json5_to_dll(json5_content, is_dto: bool, is_put: bool):
    """
    输入json5文本，输出：[(var_name, java_type, comment, required)]
    如果is_dto为True，会智能地找到关键data
    """
    data, comment_dict = parse_json5(json5_content)
    if is_dto:
        data = find_dto_data(data)
    schema_list = []
    for var_name, mockjs in data.items():
        java_type = guess_java_type(mockjs)
        comment = comment_dict.get(var_name, '').replace('"', "'")
        if is_put:
            required = comment.startswith('必传')
        else:
            required = not comment.startswith('非必传')
        if '|' in var_name:
            var_name = var_name.split('|', 1)[0]
        schema_list.append((var_name, java_type, comment, required))
    return schema_list


def path_to_package(path):
    return path.split('src/main/java/', 1)[-1].rstrip('/').replace('/', '.')


def make_vo_content(vo_path, vo_class, title, json5_content, is_dto, is_put):
    vo_package = path_to_package(vo_path)
    schema_list = parse_json5_to_dll(json5_content, is_dto, is_put)
    vo_body = render_java_vo_body(schema_list)
    if is_dto:
        title += '的返回对象'
    else:
        title += '的请求对象'
    return render_java_vo_frame(vo_package, vo_class, title, vo_body)


def codegen_controller():
    """
    创建或修改java controller源代码
    """
    # 1.配置目录（与package）
    if not os.path.isdir('.git'):
        alert_and_exit('Please change workdir to top! or run "git init" first.')
    config_path = '.codegen'
    try:
        config_data = json.loads(open(config_path).read())
    except:
        config_data = {}
    default_controller_dir = config_data.get('CONTROLLER_DIR', '')
    controller_dir = inquirer.text(message="请输入controller目录:", default=default_controller_dir).execute()
    assert '/' in controller_dir, 'controller目录至少应是多级目录'
    controller_path = Path() / controller_dir
    assert controller_path.is_dir(), 'controller目录不存在，请先创建目录'
    if default_controller_dir != controller_dir:
        config_data['CONTROLLER_DIR'] = controller_dir
        vo_dir = inquirer.text(message="请输入Vo（Value Object请求对象）目录:").execute()
        vo_path = Path() / vo_dir
        assert vo_path.is_dir(), 'VO目录不存在，请先创建目录'
        config_data['VO_DIR'] = vo_dir
        dto_dir = inquirer.text(message="请输入Dto（返回对象）目录:").execute()
        dto_path = Path() / dto_dir
        assert dto_path.is_dir(), 'DTO目录不存在，请先创建目录'
        config_data['DTO_DIR'] = dto_dir
    package_name = path_to_package(controller_dir)
    # 2.输入类名
    controller_class = inquirer.text(message="请输入controller类名:").execute()
    judge_class_name(controller_class, 'Controller')
    controller_file = controller_path / f'{controller_class}.java'  # todo
    # 3.输入yapi链接和token
    default_yapi_token = config_data.get('YAPI_TOKEN', '')
    yapi_token = inquirer.text(message="请输入YAPI项目TOKEN:", default=default_yapi_token).execute()
    config_data['YAPI_TOKEN'] = yapi_token
    yapi_url = inquirer.text(message="请输入YAPI页面链接:").execute()
    match_ret = re.findall('^(https?://[^/]+)/.*/interface/api/([0-9]+)$', yapi_url)
    assert match_ret, '该链接不是正确的YAPI接口页面链接'
    yapi_host, interface_id = match_ret[0]
    resp = requests.get(f'{yapi_host}/api/interface/get', params={'id': interface_id, 'token': yapi_token})
    assert resp.status_code == 200, f'YAPI接口返回{resp.status_code}'
    yapi_data = resp.json()
    assert yapi_data['errcode'] == 0, f'YAPI接口返回errmsg:{yapi_data["errmsg"]}'
    # 4.收集数据，准备创建controller
    yapi_data = yapi_data['data']
    method = yapi_data['method'].lower()
    path = yapi_data['path']
    title = yapi_data['title']
    req_query = yapi_data.get('req_params', []) + yapi_data.get('req_query', [])
    vo_json5 = yapi_data.get('req_body_other', '')
    dto_json5 = yapi_data.get('res_body', '')
    if method in ['post', 'put']:
        assert yapi_data.get('req_body_type') == 'json' and vo_json5, 'YAPI接口请求对象不能为空'
    assert yapi_data.get('res_body_type') == 'json' and dto_json5, 'YAPI接口返回对象不能为空'
    vo_class = dto_class = ''
    vo_class_prefix = word_to_style(make_interface_name(method, path), WordStyle.upper_camel)
    if vo_json5:
        vo_class = inquirer.text(message="请输入Vo（Value Object请求对象）类名（可为空）:", default=f'{vo_class_prefix}Vo').execute()
        if vo_class:
            judge_class_name(vo_class, 'Vo')
            vo_content = make_vo_content(config_data['VO_DIR'], vo_class, title, vo_json5, is_dto=False,
                                         is_put=(method == 'put'))
            vo_file = Path(config_data['VO_DIR']) / f'{vo_class}.java'
            with vo_file.open('w') as f:
                f.write(vo_content)
        else:
            vo_class = 'Object'
    if dto_json5:
        dto_class = inquirer.text(message="请输入Dto（返回对象）类名（可为空）:", default=f'{vo_class_prefix}Dto').execute()
        if dto_class:
            judge_class_name(dto_class, 'Dto')
            dto_content = make_vo_content(config_data['DTO_DIR'], dto_class, title, dto_json5, is_dto=True, is_put=True)
            dto_file = Path(config_data['DTO_DIR']) / f'{dto_class}.java'
            with dto_file.open('w') as f:
                f.write(dto_content)
        else:
            dto_class = 'Object'
    if method in ['post', 'put']:
        interface_content = render_java_postkind_interface(method, path, title, vo_class, dto_class, req_query)
    elif 'pageNum' in str(req_query) and 'numPerPage' in str(req_query):
        interface_content = render_java_pagekind_interface(method, path, title, dto_class, req_query)
    else:
        interface_content = render_java_getkind_interface(method, path, title, dto_class, req_query)
    if not controller_file.exists():
        controller_content = render_java_controller_frame(package_name, controller_class, interface_content)
    else:
        controller_content = controller_file.open().read().strip().rstrip('}') + interface_content + '\n}\n'
    with controller_file.open('w') as f:
        f.write(controller_content)
    with open(config_path, 'w') as f:
        f.write(json.dumps(config_data))


def codegen_entity():
    """
    基于建表SQL创建java entity源代码
    如果文件已存在则覆盖
    """
    # 1.配置目录（与package）
    if not os.path.isdir('.git'):
        alert_and_exit('Please change workdir to top! or run "git init" first.')
    config_path = '.codegen'
    try:
        config_data = json.loads(open(config_path).read())
    except:
        config_data = {}
    default_entity_dir = config_data.get('ENTITY_DIR', '')
    config_data['ENTITY_DIR'] = entity_dir = inquirer.text(message="请输入entity目录:", default=default_entity_dir).execute()
    assert '/' in entity_dir, 'entity目录至少应是多级目录'
    entity_path = Path() / entity_dir
    assert entity_path.is_dir(), 'entity目录不存在，请先创建目录'
    package_name = path_to_package(entity_dir)
    entity_class = inquirer.text(message="请输入Entity实体类名:").execute()
    judge_class_name(entity_class, '')
    entity_comment = inquirer.text(message="请输入实体的中文描述:").execute()
    assert entity_comment, '实体的中文描述不能为空'
    sql_content = inquirer.text(message="请输入建表SQL(ctrl+o完成输入):", multiline=True).execute()
    seed = re.compile(r'CREATE TABLE *`?(\w+)`? *\((.*)\)', flags=re.I | re.DOTALL)
    match_size = len(find_ret := seed.findall(sql_content))
    assert match_size == 1, '无法解析该建表SQL'
    table_name, sql_body = find_ret[0]
    schema_list = []  # [(col_name, var_name, java_type, comment)]
    for sql_line in sql_body.splitlines():
        if sql_line and is_column_sql(sql_line):
            col_name, sql_type, comment = parse_column_sql(sql_line)
            var_name = word_to_style(col_name, WordStyle.lower_camel)
            java_type = sql_type_guess_java_type(sql_type, comment)
            schema_list.append((col_name, var_name, java_type, comment))
    entity_body = render_java_entity_body(schema_list)
    entity_content = render_java_entity_frame(package_name, entity_class, entity_comment, table_name, entity_body)
    dto_file = entity_path / f'{entity_class}.java'
    with dto_file.open('w') as f:
        f.write(entity_content)
    with open(config_path, 'w') as f:
        f.write(json.dumps(config_data))


def codegen_service():
    """
    创建java service源代码
    如果文件已存在则覆盖
    """
    # 1.配置目录（与package）
    if not os.path.isdir('.git'):
        alert_and_exit('Please change workdir to top! or run "git init" first.')
    config_path = '.codegen'
    try:
        config_data = json.loads(open(config_path).read())
    except:
        config_data = {}
    default_service_dir = config_data.get('SERVICE_DIR', '')
    config_data['SERVICE_DIR'] = service_dir = inquirer.text(message="请输入service目录:",
                                                             default=default_service_dir).execute()
    assert '/' in service_dir, 'service目录至少应是多级目录'
    service_path = Path() / service_dir
    assert service_path.is_dir(), 'service目录不存在，请先创建目录'
    service_package = path_to_package(service_dir)
    # 2.mapper目录
    default_mapper_dir = config_data.get('MAPPER_DIR', '')
    config_data['MAPPER_DIR'] = mapper_dir = inquirer.text(message="请输入mapper目录:", default=default_mapper_dir).execute()
    assert '/' in mapper_dir, 'mapper目录至少应是多级目录'
    mapper_path = Path() / mapper_dir
    assert mapper_path.is_dir(), 'mapper目录不存在，请先创建目录'
    mapper_package = path_to_package(mapper_dir)
    # 3.实体目录
    default_entity_dir = config_data.get('ENTITY_DIR', '')
    config_data['ENTITY_DIR'] = entity_dir = inquirer.text(message="请输入entity目录:", default=default_entity_dir).execute()
    assert '/' in entity_dir, 'entity目录至少应是多级目录'
    entity_path = Path() / entity_dir
    assert entity_path.is_dir(), 'entity目录不存在，请先创建目录'
    entity_package = path_to_package(entity_dir)
    entity_class = inquirer.text(message="请输入Entity实体类名:").execute()
    judge_class_name(entity_class, '')
    # 4.创建各个文件(mapper->service->serviceimpl)
    makedir(service_dir.rstrip('/') + '/impl')
    mapper_content = render_java_mapper_body(mapper_package, entity_package, class_name=entity_class)
    mapper_file = mapper_path / f'{entity_class}Mapper.java'
    with mapper_file.open('w') as f:
        f.write(mapper_content)
    service_content = render_java_service_body(service_package, entity_package, class_name=entity_class)
    service_file = service_path / f'{entity_class}Service.java'
    with service_file.open('w') as f:
        f.write(service_content)
    service_impl_content = render_java_service_impl_body(service_package, entity_package, mapper_package,
                                                         class_name=entity_class)
    service_impl_file = service_path / 'impl' / f'{entity_class}ServiceImpl.java'
    with service_impl_file.open('w') as f:
        f.write(service_impl_content)
    with open(config_path, 'w') as f:
        f.write(json.dumps(config_data))


@add_subcommand('controller', codegen_controller)
@add_subcommand('entity', codegen_entity)
@add_subcommand('service', codegen_service)
def run_codegen():
    """
    生成JAVA文件或修改文件
    自动识别编程语言
    """
    pass
