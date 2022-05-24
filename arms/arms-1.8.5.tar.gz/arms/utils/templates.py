import ast
import json
import re
from arms.utils.wordstyle import word_to_style, WordStyle


def render_create_sql_frame(table_name: str, table_comment: str, primary_key: str, sql_lines: list):
    sql_body = '\n'.join(sql_lines)
    return f"""CREATE TABLE `{table_name}` (
{sql_body}
    PRIMARY KEY (`{primary_key}`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='{table_comment}';"""


def render_sql_line(col_name: str, sql_type: str, comment: str, mockjs: str, is_primary: bool):
    if mockjs.startswith('@natural'):
        sql_type = 'bigint(20) unsigned'
    elif sql_type.lower() == 'int':
        sql_type += '(11)'
    elif sql_type.lower() == 'bigint':
        sql_type += '(20) unsigned'
    elif sql_type.lower() == 'tinyint':
        sql_type += '(4)'
    elif sql_type.lower() == 'varchar':
        sql_type += '(200)'
    if col_name.lower().replace('_','') == 'nickname':
        sql_type += ' COLLATE utf8mb4_unicode_ci'
    comment = comment.replace("'", '"')
    default_part = ' DEFAULT NULL'
    if is_primary:
        default_part = ' NOT NULL'
    elif sql_type.lower() in ['text', 'blob']:
        default_part = ''
    elif col_name.lower().replace('_','') in ['createdat', 'updatedat', 'createtime', 'updatetime']:
        default_part = ' DEFAULT CURRENT_TIMESTAMP'
    extra_part = ''
    if col_name.lower().replace('_','') in ['updatedat', 'updatetime']:
        extra_part = ' ON UPDATE CURRENT_TIMESTAMP'
    elif is_primary and 'int' in sql_type.lower():
        extra_part = ' AUTO_INCREMENT'
    return f"""    `{col_name}` {sql_type}{default_part}{extra_part} COMMENT '{comment}',"""


def quote_mockjs(mockjs: str):
    if re.match('^[0-9.]+$', mockjs) or mockjs in ['true', 'false']:
        return str(mockjs)
    if mockjs.startswith(('"', "'")) and mockjs.endswith(('"', "'")):
        mockjs = ast.literal_eval(mockjs)
    return json.dumps(mockjs, ensure_ascii=False)


def render_json5(shimo_rows, tpl_type):
    indent = '    '
    if tpl_type == '返回普通对象模版':
        start_lines = [
            '{',
            f'{indent}"code": 0,',
            f'{indent}"msg": "成功",',
            f'{indent}"data": {{',
        ]
        end_lines = [f'{indent}}}', '}']
        depth = 2
    elif tpl_type == '返回数组对象(无分页)模版':
        start_lines = [
            '{',
            f'{indent}"code": 0,',
            f'{indent}"msg": "成功",',
            f'{indent}"data|3": [',
            f'{indent * 2}{{',
        ]
        end_lines = [
            f'{indent * 2}}}',
            f'{indent}]',
            '}',
        ]
        depth = 3
    elif tpl_type == '分页返回对象模版':
        start_lines = [
            '{',
            f'{indent}"code": 0,',
            f'{indent}"msg": "成功",',
            f'{indent}"data": {{',
            f'{indent * 2}"totalCount": 10, //总记录数',
            f'{indent * 2}"currentPage": 1, //当前页码',
            f'{indent * 2}"numPerPage": 10, //分页大小',
            f'{indent * 2}"recordList|10": [',
            f'{indent * 3}{{',
        ]
        end_lines = [
            f'{indent * 3}}}',
            f'{indent * 2}]',
            f'{indent}}}',
            '}'
        ]
        depth = 4
    else:
        start_lines = ['{']
        end_lines = ['}']
        depth = 1
    body_lines = []
    for name, sql_type, mockjs, comment in shimo_rows:
        mockjs = quote_mockjs(mockjs)
        comment = comment.replace('//', ' ').replace('\n', ' ')
        line = f'''{indent * depth}"{name}": {mockjs}, //{comment}'''
        body_lines.append(line)
    return '\n'.join(start_lines + body_lines + end_lines)


def render_yapi_query(shimo_rows):
    body_lines = []
    for name, sql_type, comment in shimo_rows:
        comment = comment.replace(':', '=').replace('\n', ';')
        line = f'''{name}:{comment}'''
        body_lines.append(line)
    return '\n'.join(body_lines)


def render_java_controller_frame(package_name, class_name, interface_body):
    code_body = f"""package {package_name};

import io.swagger.v3.oas.annotations.Operation;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.validation.Valid;

@Validated
@RestController
public class {class_name} {{
{interface_body}
}}"""
    return code_body


def render_interface_query_body(path, req_query: list):
    if not req_query:
        return ''
    indent = '        '
    query_lines = []
    for query_item in req_query:
        name, required, desc = query_item['name'], query_item.get('required'), query_item.get('desc') or query_item.get('example', '')
        if name in ['pageNum', 'numPerPage']:
            continue
        desc = desc.replace('"', "'")
        if '{' + name + '}' in path:
            query_lines.append(f"""{indent}@Parameter(description = "{desc}") @PathVariable Long {name}""")
        elif required == '0':
            query_lines.append(f"""{indent}@Parameter(description = "{desc}") @RequestParam(required = false) String {name}""")
        else:
            query_lines.append(f"""{indent}@Parameter(description = "{desc}") @RequestParam String {name}""")
    query_body = '\n' + ',\n'.join(query_lines)
    return query_body


def make_interface_name(method: str, path: str):
    method = method.lower()
    segs = ['create' if method == 'post' else 'edit' if method == 'put' else method]
    path = path.replace('{', 'by-').replace('}', '').replace('-', '/').replace('_', '/').replace('/', ' ')
    segs.extend(x.lower() for x in path.split())
    return word_to_style('_'.join(segs), WordStyle.lower_camel)


def render_java_postkind_interface(method: str, path: str, title: str, vo_class, dto_class, req_query: list):
    method = method.capitalize()
    interface_name = make_interface_name(method, path)
    title = title.replace('"', "'")
    vo_varname = word_to_style(vo_class, WordStyle.lower_camel)
    dto_varname = word_to_style(dto_class, WordStyle.lower_camel)
    interface_query_body = render_interface_query_body(path, req_query)
    code_body = f"""
    @Operation(summary = "{title}", description = "")
    @{method}Mapping("{path}")
    public Result<{dto_class}> {interface_name}({interface_query_body}@RequestBody @Valid {vo_class} {vo_varname}) {{
        // todo 工具生成，需要实现
        {dto_class} {dto_varname} = null;
        return Result.success({dto_varname});
    }}
"""
    return code_body


def render_java_pagekind_interface(method: str, path: str, title: str, dto_class, req_query: list):
    method = method.capitalize()
    interface_name = make_interface_name(method, path)
    title = title.replace('"', "'")
    dto_varname = word_to_style(dto_class, WordStyle.lower_camel)
    interface_query_body = render_interface_query_body(path, req_query)
    code_body = f"""
    @Operation(summary = "{title}", description = "")
    @{method}Mapping("{path}")
    public Result<PageBean<{dto_class}>> {interface_name}({interface_query_body},
        @Valid @ParameterObject PageReq pageReq
    ) {{
        // todo 工具生成，需要实现
        IPage<{dto_class}> {dto_varname}IPage = null;
        return Result.success(PageBean.of({dto_varname}IPage));
    }}
    """
    return code_body


def render_java_getkind_interface(method: str, path: str, title: str, dto_class, req_query: list):
    method = method.capitalize()
    interface_name = make_interface_name(method, path)
    title = title.replace('"', "'")
    dto_varname = word_to_style(dto_class, WordStyle.lower_camel)
    interface_query_body = render_interface_query_body(path, req_query)
    code_body = f"""
    @Operation(summary = "{title}", description = "")
    @{method}Mapping("{path}")
    public Result<{dto_class}> {interface_name}({interface_query_body}) {{
        // todo 工具生成，需要实现
        {dto_class} {dto_varname} = null;
        return Result.success({dto_varname});
    }}
    """
    return code_body


def render_java_vo_frame(vo_package, vo_class, title, vo_body):
    code_body = f"""package {vo_package};

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.experimental.Accessors;

import javax.validation.constraints.NotNull;

@Data
@Accessors(chain = true)
@Schema(description = "{title}")
public class {vo_class} {{
{vo_body}
}}
"""
    return code_body


def render_java_vo_body(schema_list):
    vo_body = ''
    for var_name, java_type, comment, required in schema_list:
        if required:
            annotation = '@NotNull\n    '
        else:
            annotation = ''
        schema_body = f"""
    {annotation}@Schema(description = "{comment}")
    private {java_type} {var_name};
"""
        vo_body += schema_body
    return vo_body


def render_java_entity_frame(package_name, entity_class, entity_comment, table_name, entity_body):
    code_body = f"""package {package_name};

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.databind.ser.std.ToStringSerializer;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.experimental.Accessors;
import org.springframework.beans.BeanUtils;

import javax.validation.constraints.NotNull;
import java.time.LocalDateTime;
import java.util.List;

@Data
@Schema(description = "{entity_comment}")
@Accessors(chain = true)
@TableName(value = "{table_name}", autoResultMap = true)
public class {entity_class} {{
{entity_body}
}}
"""
    return code_body


def render_java_entity_body(schema_list):
    newline = '\n    '
    entity_body = ''
    is_primary = True
    for col_name, var_name, java_type, comment in schema_list:
        annotation = ''
        read_only = is_primary or var_name in ['createdAt', 'updatedAt', 'createTime', 'updateTime']
        if read_only:
            annotation += f'@JsonProperty(access = JsonProperty.Access.READ_ONLY){newline}'
        else:
            annotation += f'@NotNull{newline}'
        if is_primary:
            annotation += f'@TableId(value = "{col_name}", type = IdType.ASSIGN_ID){newline}'
            is_primary = False
        if java_type == 'Long':
            annotation += f'@JsonSerialize(using = ToStringSerializer.class){newline}'
        if java_type.endswith('>'):
            annotation += f'@TableField(typeHandler = JacksonTypeHandler.class){newline}'
        schema_body = f"""
    {annotation}@Schema(description = "{comment}")
    private {java_type} {var_name};  // {col_name}
"""
        entity_body += schema_body
    return entity_body


def render_java_service_impl_body(service_package, entity_package, mapper_package, class_name):
    code_body = f"""package {service_package}.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import {entity_package}.{class_name};
import {mapper_package}.{class_name}Mapper;
import {service_package}.{class_name}Service;
import org.springframework.stereotype.Service;

@Service
public class {class_name}ServiceImpl extends ServiceImpl<{class_name}Mapper, {class_name}> implements {class_name}Service {{

}}
"""
    return code_body


def render_java_service_body(service_package, entity_package, class_name):
    code_body = f"""package {service_package};

import com.baomidou.mybatisplus.extension.service.IService;
import {entity_package}.{class_name};

public interface {class_name}Service extends IService<{class_name}> {{

}}
"""
    return code_body


def render_java_mapper_body(mapper_package, entity_package, class_name):
    code_body = f"""package {mapper_package};

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import {entity_package}.{class_name};

public interface {class_name}Mapper extends BaseMapper<{class_name}> {{

}}
"""
    return code_body