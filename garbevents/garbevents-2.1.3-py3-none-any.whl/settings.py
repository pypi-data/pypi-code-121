# -*- coding: utf-8 -*-

"""
Parameter initialization is a global variable by default. When calling the relevant API,
you need to inherit the setting class and set the corresponding parameters.

"""


class Settings(object):
    """
    # 目标 url
    ST.url = 'https://www.baidu.com/'
    # 报告生成路径，默认在当前路径生成report文件夹
    ST.report_path = 'report'
    # 所有事件名称
    ST.all_events = ['event_name_1', 'event_name_2']
    # 接口地址
    ST.interface_url = ['apipool', 'APIPOOL']
    """
    report_path = 'report'  # 默认在当前路径生成report文件夹
    db_path = 'proxy'
    url = None
    all_events = []
    interface_url = []
    mock_json = {}
    events_properties = {}
    result = None
    result_dict = None
    expect = None
    actual = None
    exclude_paths = None
    global_url = None
    api_collection = {}
