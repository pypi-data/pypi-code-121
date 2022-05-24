#!/usr/bin/env python3
# coding: utf-8

from volkanic.utils import indented_json_dumps, select_from_dict


def smart_json_dumps(obj, llen=60):
    s = indented_json_dumps(obj, indent=None)
    if len(s) < llen:
        return s
    return indented_json_dumps(obj)


def _wrap_code(lang: str, content):
    if content is None:
        return
    if lang == 'json' and not isinstance(content, str):
        content = smart_json_dumps(content)
    return f'```{lang}\n{content}\n```'


def markdown_fmt_web_api(method: str, path: str, *json_blks):
    parts = [
        f'## {path}',
        _wrap_code('http', f'{method.upper()} {path}'),
    ]
    parts += [_wrap_code('json', blk) for blk in json_blks]
    return '\n\n'.join(s for s in parts if s is not None)


def markdown_print_web_api(*args, **kwargs):
    print_keywords = ['sep', 'end', 'file', 'flush']
    print_kwargs = select_from_dict(kwargs, print_keywords, pop=True)
    print(markdown_fmt_web_api(*args, **kwargs), **print_kwargs)
    print('-' * 60, **print_kwargs)
