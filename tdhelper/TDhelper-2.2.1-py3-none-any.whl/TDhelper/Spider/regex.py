#!/usr/bin/env python3.6
# -*- encoding: utf-8 -*-
'''
@File    :   regex.py
@Time    :   2020/04/17 16:25:57
@Author  :   Tang Jing 
@Version :   1.0.0
@Contact :   yeihizhi@163.com
@License :   (C)Copyright 2020
@Desc    :   None
'''

# here put the import lib
import gc
import json
import os
import re
import hashlib
import threading
import time

from TDhelper.network.http.http_helper import m_http
from TDhelper.network.http.http_postdataformat import xWwwFormUrlencoded, jsonData, formData
from TDhelper.Event.Event import Event
from TDhelper.Spider.models.spider_event import event
from TDhelper.Spider.models.status import STATUS as SPIDER_STATUS

# code start


class Analysis(Event):
    def __init__(self, rulesConfig):
        super(Analysis, self).__init__()
        self.__http = m_http()  # HTTP对象
        self.__max_reconnect = 10  # 如果http访问失败最大重试次数
        self.__lock = threading.Lock()  # 线程锁主要用于同步回调函数.
        self.__is_to_fingerprint = True  # 验证页面内容重复临时开关.
        self.__fingerprint = None  # 临时缓存内容hash值
        self.debug = False  # 调试模式开关
        self.__interceptToken = dict()  # 拦截开关
        # 定义私有变量
        self.__access_delays = 0  # 控制爬取频率 默认0秒
        self.__define_var = dict()  # 变量缓存
        self.__config = dict()  # 爬取规则配置
        self.__configKey = ''  # 规则KEY
        self.__head = None  # requets head头
        self.__postdata = None  # request post data
        self.__prefix_domain = None  # 前缀名称
        self.__currentUrl = None  # 当前爬取地址
        self.__baseCurrentUrl = None  # 原始爬取地址
        self.__nextUrl = None  # 生成翻页地址
        self.__state = SPIDER_STATUS.SPIDER_SUCCESS  # 爬虫状态
        self.__response_html = None  # 爬取到的内容
        self.__data = dict(
            {"sources": "", "source_index": None, "analysis_key": "", "type": '', "data": None, "html": ''})
        if rulesConfig:
            self.config(rulesConfig)

    @property
    def getStatus(self):
        return self.__state

    @property
    def getData(self):
        return self.__data

    @property
    def getNextUrl(self):
        return self.__nextUrl

    @property
    def getCurrentUrl(self):
        return self.__baseCurrentUrl

    @property
    def getFingerprint(self):
        return self.__fingerprint

    def start(self, key, url=None, head=None, postdata=None):
        '''
        入口
        '''
        self.__configKey = key
        self.__currentUrl = url
        self.__url_check()
        self.__head = head
        self.__postdata = None
        if self.__state == SPIDER_STATUS.SPIDER_SUCCESS:
            self.__baseCurrentUrl = self.__currentUrl
            self.__httpControl()
            if self.__state == SPIDER_STATUS.HTTP_SUCCESS:
                # 进入规则路由
                self.__state = SPIDER_STATUS.SPIDER_SUCCESS
                if 'name' in self.__config[self.__configKey]:
                    self.__data['sources'] = self.__config[self.__configKey]['name']
                if 'source_index' in self.__config[self.__configKey]:
                    self.__data['source_index'] = self.__config[self.__configKey]['source_index']
                if 'key' in self.__config[self.__configKey]:
                    self.__data['analysis_key'] = self.__config[self.__configKey]['key']
                if 'debug' in self.__config[self.__configKey]:
                    self.debug = self.__config[self.__configKey]['debug']
                if 'reconnect' in self.__config[self.__configKey]:
                    self.__max_reconnect = self.__config[self.__configKey]['reconnect']
                if 'access_delays' in self.__config[self.__configKey]:
                    self.__access_delays = self.__config[self.__configKey]['access_delays']
                self.__route()
            if self.__access_delays > 0:
                # 控制访问频率延时.
                time.sleep(self.__access_delays)

    def search(self, params:list= []):
        if params:       
            for key,config in self.__config.items():
                self.__configKey= key
                if "search_cfg" in config:
                    m_url=''
                    m_params= {}
                    m_headers= None
                    m_metod= 'get'
                    if "url" in config["search_cfg"]:
                        m_url = config["search_cfg"]["url"]
                        if m_url:
                            self.__currentUrl= m_url
                    else:
                        self.__error('confing {0} -root.search_cfg.url, not found key.'.format(key),SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    if "params" in config["search_cfg"]:
                        m_params= config["search_cfg"]["params"]
                        offset=0
                        for k,v in config["search_cfg"]["params"].items():
                            if not v:
                                if offset < len(params):
                                    m_params[k]=params[offset]
                                    offset+=1
                                else:
                                    self.__error('Parameter:array length exceeded.', SPIDER_STATUS.SPIDER_ERROR)
                    else:
                        self.__error('confing {0} -root.search_cfg.params, not found key.'.format(key),SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    if "method" in config["search_cfg"]:
                        m_method= config["search_cfg"]["method"]
                    else:
                        self.__error('confing {0} -root.search_cfg.method, not found key.'.format(key),SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    if m_method.lower()=="post":
                        '''POST,处理POST参数.'''
                        if "content_type" in config["search_cfg"]:
                            m_content_type= config["search_cfg"]["content_type"].lower()
                            if m_content_type == "multipart/form-data":
                                m_headers, m_post_data= formData(m_params)
                            elif m_content_type == "application/json":
                                m_headers, m_post_data= jsonData(m_params)
                            elif m_content_type == "application/x-www-form-urlencoded":
                                m_headers, m_post_data= xWwwFormUrlencoded(m_params)
                            else:
                                m_headers, m_post_data= xWwwFormUrlencoded(m_params)
                        else:
                            self.__error('confing {0} -root.search_cfg.search, not found key.'.format(key),SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)    
                    else:
                        m_headers, m_post_data= xWwwFormUrlencoded(m_params)
                        if m_post_data:
                            if self.__currentUrl.find("?",0,len(self.__currentUrl)) < 0:
                                self.__currentUrl+="?"+str(m_post_data, encoding= 'utf-8')
                            else:
                                self.__currentUrl+="&"+str(m_post_data, encoding= 'utf-8')
                            m_post_data= None
                    # 开始爬取                        
                    self.__baseCurrentUrl = self.__currentUrl
                    self.__url_check()
                    if m_headers:
                        self.__head= m_headers
                    if m_post_data:
                        self.__postdata= m_post_data
                    self.__httpControl(method= m_method)
                    if self.__state == SPIDER_STATUS.HTTP_SUCCESS:
                        # 进入规则路由
                        self.__state = SPIDER_STATUS.SPIDER_SUCCESS
                        if 'name' in self.__config[self.__configKey]:
                            self.__data['sources'] = self.__config[self.__configKey]['name']
                        if 'source_index' in self.__config[self.__configKey]:
                            self.__data['source_index'] = self.__config[self.__configKey]['source_index']
                        if 'key' in self.__config[self.__configKey]:
                            self.__data['analysis_key'] = self.__config[self.__configKey]['key']
                        if 'debug' in self.__config[self.__configKey]:
                            self.debug = self.__config[self.__configKey]['debug']
                        if 'reconnect' in self.__config[self.__configKey]:
                            self.__max_reconnect = self.__config[self.__configKey]['reconnect']
                        if 'access_delays' in self.__config[self.__configKey]:
                            self.__access_delays = self.__config[self.__configKey]['access_delays']
                        self.__route()
                    if self.__access_delays > 0:
                        # 控制访问频率延时.
                        time.sleep(self.__access_delays)
                else:
                    return self.__error("-root.search_cfg, can't found key.", SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        else:
            self.__error("parameter is none.", SPIDER_STATUS.SPIDER_ERROR)

    def __url_check(self):
        self.__state = SPIDER_STATUS.SPIDER_SUCCESS
        self.__define_var = dict()
        self.__data['type'] = None
        self.__data['data'] = None
        self.__data['html'] = ''
        self.__postdata = None
        self.__head = None
        if self.__currentUrl == None:
            if self.__state != SPIDER_STATUS.SPIDER_CONFIG_IS_NOT_LOAD:
                if "entrance" in self.__config[self.__configKey]:
                    # if config hav't 'entrance' key, return.
                    self.__currentUrl = self.__config[self.__configKey]['entrance']
                    m_result = re.fullmatch(
                        self.__config[self.__configKey]['entrance'], self.__currentUrl, re.M | re.I)
                    if m_result:
                        self.__is_to_fingerprint = False
                    else:
                        self.__is_to_fingerprint = True
                else:
                    self.__is_to_fingerprint = True
                    msg = "-root.entrance, can't found key."
                    return self.__error(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    # 验证URL是否是入口地址，入口地址不检测页面重复性
        # test url prefix
        if "prefix_domain" not in self.__config[self.__configKey]:
            msg = "-root.prefix_domain, can't found key."
            return self.__error(msg, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        self.__prefix_domain = self.__config[self.__configKey]['prefix_domain']
        if not re.match(r'^(http|https)://', self.__currentUrl, re.M | re.I):
            # if re.match(self.__prefix_domain, self.__currentUrl, re.M | re.I) == None:
            self.__currentUrl = self.__prefix_domain + self.__currentUrl
        if 'exclude' in self.__config[self.__configKey]:
            # 检查URL是否需要跳过
            for item in self.__config[self.__configKey]['exclude']:
                if re.search(item, self.__currentUrl, re.I | re.M):
                    self.__state = SPIDER_STATUS.SPIDER_EXCLUDE
                    break

    def config(self, rulesConfig):
        '''
        加载配置文件

        - Parameters: 
            - path: string, 配置文件路径. 
        '''
        if rulesConfig:
            for item in rulesConfig:
                if item['path']:
                    # test config file path.
                    if os.path.exists(item['path']):
                        # read config file, open by read mode.
                        try:
                            with open(item['path'], 'r', encoding="utf-8") as json_file:
                                self.__config[item['key']
                                              ] = json.load(json_file)
                                json_file.close()
                                self.__state = SPIDER_STATUS.SPIDER_SUCCESS
                        except Exception as e:
                            self.__error(e, SPIDER_STATUS.SPIDER_ERROR)
                    else:
                        self.__error("can't found config file. path(%s)" % str(item['path']), SPIDER_STATUS.SPIDER_ERROR)
                else:
                    self.__error("config path is null.", SPIDER_STATUS.SPIDER_ERROR)
        else:
            self.__error('rules config is null', SPIDER_STATUS.SPIDER_ERROR)

    def __httpControl(self, time_out=5, method= 'GET'):
        '''
        HTTP控件

        - Parameters: 
            - time_out: int, 超时时间

        - Returns: 
            - string, int: 返回页面内容，HTTP状态
        - Exception: 
        '''
        if self.__http:
            # if request object is ready
            if self.__currentUrl:
                try:
                    self.__validateInterceptUrl()
                    if method.upper()=="GET":
                        html, state = self.__http.getcontent(self.__currentUrl)
                    else:
                        html, state= self.__http.post(url=self.__currentUrl,header=self.__head,data=self.__postdata)
                    if state == 200:
                        self.__state = SPIDER_STATUS.HTTP_SUCCESS
                        self.__response_html = html
                        self.__validateIntercept()
                    elif state == "CONNECT_IS_ERROR":
                        reconnect_total = 0
                        for i in range(0, self.__max_reconnect):
                            reconnect_total += 1
                            # TIMEOUT重试
                            if method.upper()=="GET":
                                html, state = self.__http.getcontent(self.__currentUrl)
                            else:
                                html, state= self.__http.post(url=self.__currentUrl,header=self.__head,data=self.__postdata)
                            if state == 200:
                                self.__state = SPIDER_STATUS.HTTP_SUCCESS
                                self.__response_html = html
                                self.__validateIntercept()
                                break
                        if reconnect_total >= self.__max_reconnect:
                            self.__error(
                                "访问超时.", SPIDER_STATUS.HTTP_GATEWAY_TIME_OUT)
                            # 生成翻页
                    else:
                        self.__error(html, SPIDER_STATUS.HTTP_BAD_REQUEST)
                except Exception as e:
                    self.__error(e, SPIDER_STATUS.REQUEST_ERROR)
            else:
                self.__error('访问地址为空.', SPIDER_STATUS.REQUEST_URL_IS_NONE)
        else:
            self.__error('HTTP对象未定义.', SPIDER_STATUS.REQUEST_IS_NONE)

    def __validateInterceptUrl(self):
        if self.__configKey in self.__interceptToken:
            if not re.search(r"&FbmNv=[a-z|0-9|A-Z]{16}|\?FbmNv=[a-z|0-9|A-Z]{16}", self.__currentUrl, re.I | re.M):
                if re.search(r"\?", self.__currentUrl, re.I | re.M):
                    self.__currentUrl = self.__currentUrl + \
                        "&FbmNv={0}".format(
                            self.__interceptToken[self.__configKey])
                else:
                    self.__currentUrl = self.__currentUrl + \
                        "?FbmNv={0}".format(
                            self.__interceptToken[self.__configKey])
            else:
                m_ret = re.search(
                    r"[a-z|0-9|A-Z]{16}", self.__currentUrl, re.I | re.M)
                if m_ret:
                    m_ret = m_ret.group()
                    if m_ret != self.__interceptToken[self.__configKey]:
                        self.__currentUrl = re.sub(r'FbmNv=[a-z|0-9|A-Z]{16}', "FbmNv={0}".format(
                            self.__interceptToken[self.__configKey]), self.__currentUrl, count=0, flags=0)

    def __validateIntercept(self):
        '''
            解决广东电信不良信息ISP拦截跳转问题.
        '''
        if re.search(r"<title>页面已拦截</title>", self.__response_html, re.I | re.M):
            self.__state = SPIDER_STATUS.HTTP_BAD_REQUEST
            m_token = re.search(
                r"var token = \"[a-z|0-9|A-Z]{16}\"", self.__response_html, re.I | re.M)
            if m_token:
                m_token = m_token.group()
                m_token = re.search(
                    r"[a-z|0-9|A-Z]{16}", m_token, re.I | re.M).group()
                self.__interceptToken[self.__configKey] = m_token
                self.__httpControl()
            else:
                pass

    def __generate_next_url(self):
        item = self.__config[self.__configKey]
        if item:
            if "page_url" in item:
                if "verification_page_url" in item['page_url']:
                    page_str = re.search(
                        item['page_url']['verification_page_url'], self.__currentUrl, re.M | re.I)
                    if page_str:
                        page_str = page_str.group()
                        page_param = re.findall(r"[1-9]\d*", page_str, flags=0)
                        if page_param:
                            if 'page_param_index' in item['page_url']:
                                if len(page_param) < item['page_url']['page_param_index']:
                                    # default next page index is 2.
                                    page_param.append("2")
                                else:
                                    # calculation next page index
                                    page_param_index = item['page_url']['page_param_index']
                                    if page_param_index != 0:
                                        page_param_index -= 1
                                        page_param[page_param_index] = str(
                                            int(page_param[page_param_index]) + 1)
                                if 'template' in item['page_url']:
                                    self.__nextUrl = item['page_url']['template'].format(
                                        page_param)
                                    self.__nextUrl = re.sub(
                                        item['page_url']['verification_page_url'], self.__nextUrl, self.__currentUrl, count=0, flags=0)

    def __fingerprintPage(self):
        '''
        生成内容指纹
        '''
        # create file fingerprint
        if not self.debug:
            if self.__is_to_fingerprint:
                m_md5 = hashlib.md5()
                m_md5.update(self.__response_html.encode('UTF-8'))
                m_fingerprint = m_md5.hexdigest()
                self.__fingerprint = m_fingerprint
                try:
                    self.__lock.acquire()
                    if self.debug:
                        self.on(
                            event.onDebug, self, **{"event": event.onFingerprintComplete, "data": self.__data})
                    else:
                        m_check_status = self.on(
                            event.onFingerprintComplete, self)
                    if m_check_status:
                        self.__error(
                            "内容没有改变.", SPIDER_STATUS.SPIDER_FINGERPRINT_IS_REPEAT)
                        #self.__nextUrl= None
                finally:
                    self.__lock.release()

    def __route(self):
        '''
        规则路由
        '''
        if "rules" in self.__config[self.__configKey]:
            rule_total = 0
            for item in self.__config[self.__configKey]['rules']:
                if "url_checking" in self.__config[self.__configKey]['rules'][rule_total]:
                    m_completion = ""  # 如果地址被拦截则补全参数
                    m_ret = re.search(
                        "&FbmNv=[a-z|0-9|A-Z]{16}|\\?FbmNv=[a-z|0-9|A-Z]{16}", self.__currentUrl, re.I | re.M)
                    if m_ret:
                        m_completion = m_ret.group()
                        if re.search(r"^\?", m_completion, re.I | re.M):
                            m_completion = "\\" + m_completion
                        m_validateUrl = "(" + \
                            self.__config[self.__configKey]['rules'][rule_total]['url_checking'] + \
                            ")"+m_completion
                    else:
                        m_validateUrl = self.__config[self.__configKey]['rules'][rule_total]['url_checking']
                    matching_rule = re.fullmatch(
                        m_validateUrl, self.__currentUrl, re.I | re.S)
                    if not matching_rule:
                        # 查找下一个规则
                        rule_total += 1
                        continue
                    else:
                        # 定义变量
                        if 'define' in item:
                            for define_config in item['define']:
                                self.__define(config=define_config)

                        # 找到规则进行内容截取
                        self.__interceptPage(rule_total)
                        if self.__state == SPIDER_STATUS.SPIDER_SUCCESS:
                            # 生成文件指纹
                            if 'type' in item:
                                if item['type'] == 'detail':
                                    self.__fingerprintPage()
                            if self.__state != SPIDER_STATUS.SPIDER_FINGERPRINT_IS_REPEAT:
                                # 进入分析
                                self.__action(rule_total)
                            # if self.__state== SPIDER_STATUS.SPIDER_SUCCESS:

                            # 进入事件
                            if 'type' in item:
                                m_type = item['type']
                                if m_type == "index":
                                    # 触发INDEX爬取完成事件
                                    try:
                                        self.__lock.acquire()
                                        if self.debug:
                                            self.on(
                                                event.onDebug, self, **{"event": event.onIndexComplete, "data": self.__data})
                                        else:
                                            self.on(
                                                event.onIndexComplete, self)
                                    finally:
                                        self.__lock.release()
                                elif m_type == "list":
                                    # 触发LIST爬取完成事件
                                    try:
                                        self.__lock.acquire()
                                        # 页面验证有重复或则页面filter有错则不进入下一页面.
                                        if (self.__state != SPIDER_STATUS.SPIDER_FINGERPRINT_IS_REPEAT) and (self.__state != SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_FILTER_FAIL):
                                            self.__generate_next_url()
                                        if self.debug:
                                            self.on(
                                                event.onDebug, self, **{"event": event.onListComplete, "data": self.__data})
                                        else:
                                            self.on(event.onListComplete, self)
                                    finally:
                                        self.__lock.release()
                                elif m_type == "detail":
                                    # 触发详细页面爬取完成事件
                                    try:
                                        self.__lock.acquire()
                                        if self.debug:
                                            self.on(
                                                event.onDebug, self, **{"event": event.onDetailComplete, "data": self.__data})
                                        else:
                                            self.on(
                                                event.onDetailComplete, self)
                                    finally:
                                        self.__lock.release()
                                else:
                                    self.__error(
                                        "分析规则TYPE错误, 找不到事件触发.", SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_ACTION_FAIL)
                            else:
                                self.__error(
                                    "root.rules.{0}.type, can't found" % rule_total, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                        break
                else:
                    self.__error('root.rules.{0}.url_checking can''t found.' %
                                 rule_total, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    break
            # 没有找到规则
            if rule_total >= len(self.__config[self.__configKey]['rules']):
                self.__error(
                    '没有找到分析规则.', SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_RULES_CAN_NOT_FOUND)
        else:
            self.__error(
                '没有找到规则配置.', SPIDER_STATUS.SPIDER_REGAULE_MATCH_IS_ERROR)

    def __interceptPage(self, index):
        '''
        截取页面

        - Parameters: 
            - index: rules 索引
        '''
        # 计算截取开始结束位置
        config_item = self.__config[self.__configKey]["rules"][index]
        if "start_anchor" not in config_item:
            return self.__error("root.rules.{0}.start_anchor" % str(index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        if "end_anchor" not in config_item:
            return self.__error("root.rules.{0}.end_anchor" % str(index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        # 开始截取
        offset_start = -1
        offset_end = -1
        m_regex = re.search(
            config_item['start_anchor'], self.__response_html, re.M | re.I)
        if m_regex:
            offset_start = m_regex.start()
            m_regex = None
        m_regex = re.search(
            config_item['end_anchor'], self.__response_html, re.M | re.I)
        if m_regex:
            offset_end = m_regex.start()
            m_regex = None
        if offset_start < 0:
            return self.__error("没有匹配到起始位置.", SPIDER_STATUS.SPIDER_REGAULE_MATCH_IS_ERROR)
        if offset_end < 0:
            return self.__error("没有匹配到结束位置.", SPIDER_STATUS.SPIDER_REGAULE_MATCH_IS_ERROR)
        if offset_start >= offset_end:
            return self.__error("截取范围出错.({0},{1})" % (offset_start, offset_end), SPIDER_STATUS.SPIDER_INTERCEPT_ERROR)
        self.__response_html = self.__response_html[offset_start: offset_end]

    def __action(self, index):
        action_config_item = None
        if "actions" in self.__config[self.__configKey]['rules'][index]:
            action_config_item = self.__config[self.__configKey]['rules'][index]['actions']
            action_total = 0  # action计数
            for m_action in action_config_item:
                # 执行分析
                if 'action' not in m_action:
                    self.__error("root.rules.{0}.actions.{1}.action, can't found key." % (
                        index, action_total), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    break
                action_type = m_action['action']
                if action_type == "filter":
                    # 提取
                    if self.__state == SPIDER_STATUS.SPIDER_SUCCESS:
                        self.__filter(index, action_total)
                    else:
                        break
                elif action_type == "replace":
                    # 替换
                    if self.__state == SPIDER_STATUS.SPIDER_SUCCESS:
                        self.__replace(index, action_total)
                    else:
                        break
                elif action_type == "inserhtml":
                    if self.__state == SPIDER_STATUS.SPIDER_SUCCESS:
                        self.__insertHtml(index, action_total)
                    else:
                        break
                elif action_type == "validate":
                    if self.__state == SPIDER_STATUS.SPIDER_SUCCESS:
                        self.__validate(index, action_total)
                    else:
                        break
                else:
                    self.__error("找不到分析器, root.rules.{0}.actions.{1}.action." % (
                        index, action_total), SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_ACTION_FAIL)
                    break
                action_total += 1
            if self.__state == SPIDER_STATUS.SPIDER_SUCCESS:
                self.__serialize_data(index, action_total)
        else:
            self.__error('root.rules.{0},actions, can''t found key.' %
                         index, SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)

    def __validate(self, rule_index, action_index):
        '''
        验证数据
        '''
        backups_response_html = self.__response_html
        m_config = self.__config[self.__configKey]['rules'][rule_index]['actions'][action_index]
        if "extract_regex" in m_config:
            m_body = re.search(
                m_config['extract_regex'], self.__response_html, re.I | re.M)
            if 'condition' in m_config:
                if bool(m_body) == m_config['condition']:
                    if 'func' in m_config:
                        if ('extract_regex' in m_config['func']) and ('replace_str' in m_config['func']):
                            tmp_body = ''
                            body = m_body.group()
                            tmp_body = re.sub(
                                m_config['func']['extract_regex'], m_config['func']['replace_str'], body, count=0, flags=0)
                            if 'template' in m_config['func']:
                                tmp_body = re.sub(
                                    r"{{value}}", tmp_body, m_config['func']['template'], count=0, flags=0)
                            self.__response_html = re.sub(
                                m_config['extract_regex'], tmp_body, self.__response_html, count=0, flags=0)
                            if 'debug' in m_config:
                                if m_config['debug']:
                                    self.on(event.onDebug, self, **{"event": 'actiondebug', "data": "-{0}, regular:{1}\r\n\t- befor:{2}\r\n\t- after:{3}".format(
                                        self.getCurrentUrl, m_config['extract_regex'], backups_response_html, self.__response_html)})
                        else:
                            self.__error("root.rules.{0}.actons.{1}.func extract_regex or replace_str, can't found key." % (
                                rule_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                    else:
                        self.__error("root.rules.{0}.actons.{1}.func, can't found key." % (
                            rule_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
            else:
                self.__error("root.rules.{0}.actons.{1}.condition, can't found key." % (
                    rule_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        else:
            self.__error("root.rules.{0}.actons.{1}.extract_regex, can't found key." % (
                rule_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)

    def __filter(self, rule_index, action_index):
        '''
        提取页面

        - Parameters: 
            - reule_index: 规则索引.
            - action_index: 动作索引.  
        '''
        backups_response_html = self.__response_html
        filter_html = ""
        m_config = self.__config[self.__configKey]['rules'][rule_index]['actions'][action_index]
        m_re_state = re.search(
            m_config['extract_regex'], self.__response_html, flags=0)
        if not m_re_state:
            self.__state = SPIDER_STATUS.SPIDER_PAGE_ANALYSIS_FILTER_FAIL
            self.__nextUrl = None
        else:
            if 'extract_regex' in m_config:
                for filter_item in re.finditer(m_config['extract_regex'], self.__response_html, flags=0):
                    filter_html += str(filter_item.group())
                if filter_html:
                    self.__response_html = filter_html
                    self.__status = SPIDER_STATUS.SPIDER_SUCCESS
                else:
                    self.__status = SPIDER_STATUS.SPIDER_ERROR
                if 'debug' in m_config:
                    if m_config['debug']:
                        self.on(event.onDebug, self, **{"event": 'actiondebug', "data": "-{0}, regular:{1}\r\n\t- befor:{2}\r\n\t- after:{3}".format(
                            self.getCurrentUrl, m_config['extract_regex'], backups_response_html, self.__response_html)})
            else:
                self.__error("root.rules.{0}.actons.{1}.extract_regex, can't found key." % (
                    rule_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        backups_response_html = None

    def __define(self, config):
        '''定义变量

            config json:

            "define": [
                    {
                        "key": "变量名称",
                        "extract_regex": "提取正则",
                        "func": [
                            {
                                "extract_regex": "正则",
                                "replace_str":"替换字段"
                            }
                        ]
                    }
                ]
        '''
        m_config = config
        try:
            m_body = re.search(
                m_config['extract_regex'], self.__response_html, re.I | re.M)
            if m_body:
                value = m_body.group()
                for item in m_config['func']:
                    value = re.sub(
                        item['extract_regex'], item['replace_str'], value, count=0, flags=0)
                self.__define_var[m_config['key']] = value
        except Exception as e:
            self.__error(e,SPIDER_STATUS.SPIDER_ERROR)

    def __replace(self, rule_index, action_index):
        '''
        替换页面元素

        - Parameters: 
            - reule_index: 规则索引.
            - action_index: 动作索引.
        '''
        backups_response_html = self.__response_html
        m_config = self.__config[self.__configKey]['rules'][rule_index]['actions'][action_index]
        if 'extract_regex' in m_config:
            replace_str = m_config['replace_str']
            for item in re.finditer(r"{{.*?}}", replace_str, re.I | re.M):
                item = item.group().replace("{{", "")
                item = item.replace("}}", "")
                if item in self.__define_var:
                    replace_str = replace_str.replace(
                        r"{{"+item+"}}", self.__define_var[item])
            self.__response_html = re.sub(
                m_config['extract_regex'], replace_str, self.__response_html, count=0, flags=0)
            if 'debug' in m_config:
                if m_config['debug']:
                    self.on(event.onDebug, self, **{"event": 'actiondebug', "data": "-{0}, regular:{1}\r\n\t- befor:{2}\r\n\t- after:{3}".format(
                        self.getCurrentUrl, m_config['extract_regex'], backups_response_html, self.__response_html)})
        else:
            self.__error("root.rules.{0}.actons.{1}.extract_regex, can't found key." % (
                rule_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        backups_response_html = None

    def __insertHtml(self, rule_index, action_index):
        '''
        说明

        - Parameters: 
            - reule_index: 规则索引.
            - action_index: 动作索引.
        '''
        backups_response_html = self.__response_html
        m_config = self.__config[self.__configKey]['rules'][rule_index]['actions'][action_index]
        if 'html' in m_config:
            ret = "end"
            if "pos" in m_config:
                ret = m_config['pos']
            if ret == 'end':
                self.__response_html += m_config['html']
            elif ret == "head":
                self.__response_html = m_config['html'] + self.__response_html
            if 'debug' in m_config:
                if m_config['debug']:
                    self.on(event.onDebug, self, **{"event": 'actiondebug', "data": "-{0}, regular:{1}\r\n\t- befor:{2}\r\n\t- after:{3}".format(
                        self.getCurrentUrl, m_config['extract_regex'], backups_response_html, self.__response_html)})
        else:
            self.__error("root.rules.{0}.actons.{1}.html, can't found key." % (
                rule_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        backups_response_html = None

    def __serialize_data(self, rules_index, action_index):
        '''
        序列化数据

        - Parameters: 
            - reule_index: 规则索引.
            - action_index: 动作索引.
        '''
        cfg_item = self.__config[self.__configKey]['rules'][rules_index]
        if 'serialize_data' in cfg_item:
            cfg_serialize_data = cfg_item['serialize_data']
            if "serialize_type" in cfg_serialize_data:
                if "split_str" in cfg_serialize_data:
                    if "fields" in cfg_serialize_data:
                        # 过滤换行符、制表符.
                        m_html = re.sub(r"\r\n|\r|\n|\t", "",
                                        self.__response_html, count=0, flags=0)
                        # 序列化数据
                        m_data = re.split(
                            cfg_serialize_data['split_str'], m_html, maxsplit=0, flags=0)
                        # 删除空数据
                        m_data = [i for i in m_data if i != '']
                        # 检查数据完整性.
                        m_data = self.__check_result(
                            rules_index, action_index, m_data)
                        fields_count = len(cfg_serialize_data['fields'])
                        data_count = len(m_data)
                        if (fields_count == 0) or (data_count == 0):
                            self.__error("数据格式化有误.(data_length:{0},fields_length:{1})" % (
                                data_count, fields_count), SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)
                            self.__data['type'] = cfg_item['type']
                            self.__data['data'] = None
                            self.__data['html'] = self.__response_html
                        else:
                            if data_count % fields_count:
                                msg = "-{0}, {1}".format(self.__currentUrl, "数据长度与字段长度不一致: length({0}:{1})\r\n\tsplit_html({2})\r\n\tfields({3})".format(
                                    data_count, fields_count, str(m_data), str(cfg_serialize_data['fields'])))
                                self.__error(
                                    msg, SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)
                            else:
                                result = []
                                for step_split in range(0, data_count, fields_count):
                                    m_dict = dict()
                                    for step_fields in range(0, fields_count):
                                        m_dict[cfg_serialize_data['fields'][step_fields]
                                               ] = m_data[step_split + step_fields]
                                    if len(m_dict) > 0:
                                        result.append(m_dict)
                                if len(result) <= 0:
                                    msg = "-序列化数据为空."
                                    return self.__error(msg, SPIDER_STATUS.SPIDER_SERIALIZE_ERROR)
                                self.__data['type'] = cfg_item['type']
                                self.__data['data'] = result
                                self.__data['html'] = self.__response_html
                    else:
                        self.__error("root.rules.{0}.actions.{1}.serialize_data.fields, can't found key." % (
                            rules_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
                else:
                    self.__error("root.rules.{0}.actions.{1}.serialize_data.split_str, can't found key." % (
                        rules_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
            else:
                self.__error("root.rules.{0}.actions.{1}.serialize_data.serialize_type, can't found key." % (
                    rules_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)
        else:
            self.__error("root.rules.{0}.actions.{1}.serialize_data, can't found key." % (
                rules_index, action_index), SPIDER_STATUS.SPIDER_CONFIG_CAN_NOT_FOUND_KEY)

    def __check_result(self, rules_index, action_index, result):
        '''
        检查数据集结果规范, 根据serialize_data.check_fields_type配置项进行检查.如果检查结果不匹配则使用默认值替代

        - Parameters：
            - reule_index: 规则索引.
            - action_index: 动作索引.
            - result: []
        '''
        cfg_item = self.__config[self.__configKey]['rules'][rules_index]
        if "check_fields_type" in cfg_item:
            for check_config in cfg_item['check_fields_type']:
                if len(check_config) == 4:
                    if len(result) >= check_config[0]:
                        m_re_result = re.search(
                            check_config[1], result[check_config[0]], re.I | re.M)
                        if not m_re_result:
                            if check_config[3] == "insert":
                                result.insert(check_config[0], check_config[2])
                        else:
                            re.sub(
                                check_config[1], check_config[2], result[check_config[0]], count=0, flags=0)
        return result
    # oerror

    def __error(self, msg, state):
        '''
        错误处理

        - Parameters: 
            - msg: string, 错误信息
            - state: any, 错误状态值

        - Returns: 
            None 
        '''
        try:
            self.__state = state
            msg = "- {0},code: {1} body: {2}".format(
                self.__currentUrl, state, msg)
            # 错误处理事件
            self.on(event.onError, self, msg)
        finally:
            return None
