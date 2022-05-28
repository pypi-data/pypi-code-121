#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: v.stone@163.com
import json
from getopt import getopt, GetoptError
import sys
import os

import yaml

from opsctl.render import Render as opsctlRender


def print_help_tool():
    print('\n'.join([
        '\nopsctl',
        '\t'.join([
            '  tmpl2art',
            'Render templates to articles'
        ]),
        '\t'.join([
            '  env2json',
            'Get environ variables to Json file'
        ]),
        '\t'.join([
            '  env2yaml',
            'Get environ variables to YAML file'
        ]),
        '\t'.join([
            '  version',
            'Show opsctl version'
        ]),
    ]))
    exit(1)


def print_help_cmd_tmpl2art():
    print('\n'.join([
        '\nopsctl tmpl2art',
        '\t'.join([
            '  --config',
            'Key-Value config file path, file type is YAML'
        ]),
        '\t'.join([
            '  --tmpldir',
            'Template root path'
        ]),
        '\t'.join([
            '  --artdir',
            'Articles output path'
        ]),
    ]))
    exit(1)


def check_cmd_tmpl2art_opts(cmd_tmpl2art_opts):
    """
    config, template, render are required
    :param cmd_tmpl2art_opts:
    :return:
    """
    _items = dict()
    for k, v in cmd_tmpl2art_opts:
        _items['OPSCTL_%s' % k.replace('--', '').upper()] = v
    if len(_items) == 0:
        print_help_cmd_tmpl2art()
    if not _items.get('OPSCTL_CONFIG'):
        print('--config is required')
        print_help_cmd_tmpl2art()
    if not _items.get('OPSCTL_TMPLDIR'):
        print('--tmpldir is required')
        print_help_cmd_tmpl2art()
    if not _items.get('OPSCTL_ARTDIR'):
        print('--artdir is required')
        print_help_cmd_tmpl2art()
    if not os.path.isfile(_items['OPSCTL_CONFIG']):
        print('%s is not a valid file' % _items['OPSCTL_CONFIG'])
        print_help_cmd_tmpl2art()
    if not os.path.isdir(_items['OPSCTL_TMPLDIR']):
        print('%s is not a valid dir' % _items['OPSCTL_TMPLDIR'])
        print_help_cmd_tmpl2art()
    return _items


def print_help_cmd_env2json():
    print('\n'.join([
        '\nopsctl env2json',
        '\t'.join([
            '  --output',
            'Output Json file path'
        ]),
        '\t'.join([
            '  --input',
            'Optional. Ensure your input file format that is must be same with output of command "env".'
        ]),
        '\t'.join([
            '         ',
            'Get current os environ variables if let this option empty.'
        ]),
    ]))
    exit(1)


def check_cmd_env2json_opts(cmd_env2json_opts):
    """
    output is required
    :param cmd_env2json_opts:
    :return:
    """
    _items = dict()
    for k, v in cmd_env2json_opts:
        _items['OPSCTL_%s' % k.replace('--', '').upper()] = v
    if len(_items) == 0:
        print_help_cmd_env2json()
    if not _items.get('OPSCTL_OUTPUT'):
        print('--output is required')
        print_help_cmd_env2json()
    return _items


def print_help_cmd_env2yaml():
    print('\n'.join([
        '\nopsctl env2yaml',
        '\t'.join([
            '  --output',
            'Output YAML file path'
        ]),
        '\t'.join([
            '  --input',
            'Optional. Ensure your input file format that is must be same with output of command "env".'
        ]),
        '\t'.join([
            '         ',
            'Get current os environ variables if let this option empty.'
        ]),
    ]))
    exit(1)


def check_cmd_env2yaml_opts(cmd_env2yaml_opts):
    """
    output is required
    :param cmd_env2yaml_opts:
    :return:
    """
    _items = dict()
    for k, v in cmd_env2yaml_opts:
        _items['OPSCTL_%s' % k.replace('--', '').upper()] = v
    if len(_items) == 0:
        print_help_cmd_env2yaml()
    if not _items.get('OPSCTL_OUTPUT'):
        print('--output is required')
        print_help_cmd_env2yaml()
    return _items


def output_env(output_type, output_path, input_path):
    output_content = ""
    if input_path:
        with open(input_path, 'r', encoding='utf-8') as f:
            input_file_content = f.read()
        input_items = list()
        for input_file_line in input_file_content.split('\n'):
            input_items.append(input_file_line.replace('=', ': ', 1))
        input_content = '\n'.join(input_items)
    else:
        input_content = dict(os.environ)
    if output_type == "json":
        output_content = json.dumps(input_content)
    elif output_type == "yaml":
        output_content = yaml.safe_dump(input_content)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_content)


def main():
    try:
        tool_cmd = sys.argv[1]
    except IndexError:
        tool_cmd = ''
        print_help_tool()
    cmd_args = sys.argv[2:]
    cmd_args_items = dict()
    if tool_cmd == 'tmpl2art':
        try:
            opts, args = getopt(
                args=cmd_args,
                shortopts='',
                longopts=[
                    'config=',
                    'tmpldir=',
                    'artdir=',
                ]
            )
            cmd_args_items = check_cmd_tmpl2art_opts(opts)
        except GetoptError:
            print_help_cmd_tmpl2art()
        opsctl_render = opsctlRender(
            config_file=cmd_args_items['OPSCTL_CONFIG'],
            template_dir=cmd_args_items['OPSCTL_TMPLDIR'],
            render_dir=cmd_args_items['OPSCTL_ARTDIR']
        )
        opsctl_render.render_all()
    elif tool_cmd == 'env2json':
        try:
            opts, args = getopt(
                args=cmd_args,
                shortopts='',
                longopts=[
                    'output=',
                    'input=',
                ]
            )
            cmd_args_items = check_cmd_env2json_opts(opts)
        except GetoptError:
            print_help_cmd_env2json()
        output_env(
            output_type='json',
            output_path=cmd_args_items['OPSCTL_OUTPUT'],
            input_path=cmd_args_items['OPSCTL_INPUT']
        )
    elif tool_cmd == 'env2yaml':
        try:
            opts, args = getopt(
                args=cmd_args,
                shortopts='',
                longopts=[
                    'output=',
                ]
            )
            cmd_args_items = check_cmd_env2yaml_opts(opts)
        except GetoptError:
            print_help_cmd_env2yaml()
        output_env(
            output_type='yaml',
            output_path=cmd_args_items['OPSCTL_OUTPUT'],
            input_path=cmd_args_items['OPSCTL_INPUT']
        )
    elif tool_cmd == 'version':
        print('opsctl v0.1.6')
    else:
        print_help_tool()


if __name__ == '__main__':
    main()
