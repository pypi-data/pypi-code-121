#!/usr/bin/env python3.6
#! -*- coding: utf-8 -*-

import io
import xml.etree.cElementTree as ET

def parse_xml(indata):
    """解析XML文本为dict类型

    :param str|bytes indata: payload data
    :rtype: dict 
    """
    if isinstance(indata, str):
        fd = io.StringIO(indata)
    elif isinstance(indata, bytes):
        fd = io.BytesIO(indata)
    result = {}
    cursor = result
    last_event = ''
    last_tag = ''
    parent_tag = ''
    parent_cursor = cursor
    for event, elem in ET.iterparse(fd, events=('start', 'end')):
        if event == 'start':
            if 'end' == last_event:
                if elem.tag == last_tag:
                    if not isinstance(cursor[elem.tag]):
                        cursor[elem.tag] = [cursor[elem.tag]]
            elif 'start' == last_event and last_tag:
                parent_cursor = cursor
                parent_tag = last_tag
                if last_tag not in cursor:
                    cursor[last_tag] = ''
                if cursor[last_tag] == '':
                    cursor[last_tag] = {}
                    cursor = cursor[last_tag]
                else:
                    if not isinstance(cursor[last_tag], list):
                        cursor[last_tag] = [cursor[last_tag]]
                    cursor[last_tag].append({})
                    cursor = cursor[last_tag][len(cursor[last_tag])-1]

            last_tag = elem.tag
        elif event == 'end':
            if 'start' == last_event:
                value = elem.text.strip() if isinstance(elem.text, str) else elem.text
                if elem.tag not in cursor:
                    cursor[elem.tag] = value
                else:
                    if not isinstance(cursor[elem.tag], list):
                        cursor[elem.tag] = [cursor[elem.tag]]
                    cursor[elem.tag].append(value)
            
            elif 'end' == last_event:
                if parent_tag:
                    cursor = parent_cursor
            
        last_event = event

    return result

def format_xml(params, parent_key=''):
    """组装xml数据

    :param dict params: payload data
    :rtype: str 
    """
    result = []
    if isinstance(params, list):
        for e in params:
            result.append('<{0}>{1}</{0}>'.format(parent_key, format_xml(e, parent_key)))
    elif isinstance(params, dict):
        for k, v in params.items():
            if isinstance(v, list):
                result.append(format_xml(v, k))
            else:
                if isinstance(v, dict):
                    value = format_xml(v, k)
                elif v is None:
                    value = ''
                else:
                    value = str(v)
                result.append('<{0}>{1}</{0}>'.format(k, value))
    else:
        result.append(str(params))
    return ''.join(result)
