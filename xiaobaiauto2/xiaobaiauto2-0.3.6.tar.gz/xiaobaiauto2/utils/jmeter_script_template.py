#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'jmeter_script_template.py'
__create_time__ = '2020/12/24 14:44'

from typing import Optional
from re import findall
from urllib.parse import urlparse
from xml.sax.saxutils import escape
from xiaobaiauto2.utils.xiaobaiauto2Installer import getWebList

NEED_EXTRACTOR = False
EXTRACTOR_NAME = []
REQUEST_NAME_LIST = []

def JMETER_SCRIPT_HEAD(JMETER_VERSION: Optional[str] = '5.4.3'):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="{JMETER_VERSION}">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="测试计划" enabled="true">
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <CookieManager guiclass="CookiePanel" testclass="CookieManager" testname="HTTP Cookie管理器" enabled="true">
        <collectionProp name="CookieManager.cookies"/>
        <boolProp name="CookieManager.clearEachIteration">false</boolProp>
        <boolProp name="CookieManager.controlledByThreadGroup">false</boolProp>
      </CookieManager>
      <hashTree/>
      <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="察看结果树" enabled="true">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp>
          <name>saveConfig</name>
          <value class="SampleSaveConfiguration">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>false</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>false</responseData>
            <samplerData>false</samplerData>
            <xml>false</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>false</responseHeaders>
            <requestHeaders>false</requestHeaders>
            <responseDataOnError>false</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>0</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <threadCounts>true</threadCounts>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>
        <stringProp name="filename"></stringProp>
      </ResultCollector>
      <hashTree/>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="线程组" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">1</stringProp>
        <stringProp name="ThreadGroup.ramp_time">1</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>'''

def JMETER_SCRIPT_FOOT():
    return '''
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>'''

def JMETER_SCRIPT_HEADER(key, value):
    try:
        key = escape(key)
    except Exception as e:
        pass
    try:
        value = escape(value)
    except Exception as e:
        pass
    return f'''
              <elementProp name="" elementType="Header">
                <stringProp name="Header.name">{key}</stringProp>
                <stringProp name="Header.value">{value}</stringProp>
              </elementProp>'''

def JMETER_SCRIPT_EXTRACTOR(t: Optional[str] = 're',
                            name: Optional[str] = None,
                            match: Optional[str] = None,
                            match_num: Optional[int] = 1):
    if name in [None, ''] or match in [None, '']:
        return ''
    else:
        try:
            name = escape(name.strip())
        except Exception as e:
            pass
        try:
            match = escape(match.strip())
        except Exception as e:
            pass
    if 're' == t:
        return f'''
          <RegexExtractor guiclass="RegexExtractorGui" testclass="RegexExtractor" testname="{name}正则提取器" enabled="true">
            <stringProp name="RegexExtractor.useHeaders">false</stringProp>
            <stringProp name="RegexExtractor.refname">{name}</stringProp>
            <stringProp name="RegexExtractor.regex">{match}</stringProp>
            <stringProp name="RegexExtractor.template">$1$</stringProp>
            <stringProp name="RegexExtractor.default"></stringProp>
            <stringProp name="RegexExtractor.match_number">{match_num}</stringProp>
          </RegexExtractor>
          <hashTree/>'''
    elif 'json' == t:
        return f'''
          <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="{name}JSON提取器" enabled="true">
            <stringProp name="JSONPostProcessor.referenceNames">{name}</stringProp>
            <stringProp name="JSONPostProcessor.jsonPathExprs">{match}</stringProp>
            <stringProp name="JSONPostProcessor.match_numbers">{match_num}</stringProp>
          </JSONPostProcessor>
          <hashTree/>'''

def JMETER_EQUEST(file_path: Optional[str] = '',
                  post_value: Optional[str] = '',
                  contentEncoding: Optional[str] = '',
                  url: Optional[str] = '/',
                  method: Optional[str] = 'GET',
                  headers: Optional[dict] = None,
                  response: Optional[str] = ''):
    global NEED_EXTRACTOR, EXTRACTOR_NAME, REQUEST_NAME_LIST
    handle = ''
    header = ''
    if isinstance(headers, dict):
        for k, v in headers.items():
            header += JMETER_SCRIPT_HEADER(k, v)
    HTTPer = urlparse(url=url)
    scheme = HTTPer.scheme
    netloc = HTTPer.netloc.split(':')[0]
    if HTTPer.port is not None:
        port = HTTPer.port
    else:
        if HTTPer.scheme == 'https':
            port = '443'
        elif HTTPer.scheme == 'http':
            port = '80'
        else:
            port = ''
    if HTTPer.query != '':
        if HTTPer.fragment != '':
            path = f'{HTTPer.path}?{HTTPer.query}#{HTTPer.fragment}'
        else:
            path = f'{HTTPer.path}?{HTTPer.query}'
    else:
        path = HTTPer.path
    request_name = 'index' if HTTPer.path in ['', '/'] else HTTPer.path.split('/')[-1]
    if request_name not in REQUEST_NAME_LIST:
        REQUEST_NAME_LIST.append(request_name)
    else:
        _i = 1
        while request_name + '_' + _i.__str__() in REQUEST_NAME_LIST:
            _i += 1
        REQUEST_NAME_LIST.append(request_name + '_' + _i.__str__())
        request_name = request_name + '_' + _i.__str__()
    if NEED_EXTRACTOR and response != '' and len(EXTRACTOR_NAME) > 0:
        '''
            json:
                '{"name": "Tser", "age": 30}'
                '{'name': 'Tser', 'age': 30}'
            xml/html:
                <man><name>Tser</name><age>30</age></man>
                <man name="Tser" age="30"></man>
                <man name='Tser' age='30'></man>
            text:
                name: Tser, age: 30
                name=Tser, age=30
        '''
        EXTRACTORED_NAME = []
        for key in EXTRACTOR_NAME:
            if key in response and NEED_EXTRACTOR:
                m = findall(f'({key}[\"\'=:\s0-9a-zA-Z}}>/]+)', response)
                mat = m[0] if len(m) > 0 else ''
                if '=' in mat:
                    fsp = '='
                elif ':' in mat:
                    fsp = ':'
                else:
                    fsp = ' '
                ma_list = mat.split(fsp)
                if '"' in ma_list[1]:
                    sp = '"'
                elif "'" in ma_list[1]:
                    sp = "'"
                else:
                    sp = ' '
                ma1_list = ma_list[1].split(sp)
                if len(ma1_list) >= 3:
                    match = ''.join([ma_list[0], fsp, ma1_list[0], sp, "(.+?)", sp, ma1_list[2]])
                elif len(ma1_list) == 1:
                    match = ''.join([ma_list[0], fsp, sp, "(.+?)", sp])
                else:
                    val0 = findall(f'"{key}": "(.+?)"', response)
                    val1 = findall(f"'{key}': '(.+?)'", response)
                    val2 = findall(f'{key}="(.+?)"', response)  # HTML/XML属性中
                    val3 = findall(f"{key}='(.+?)'", response)
                    val4 = findall(f'{key}:"(.+?)"', response)
                    val5 = findall(f"{key}:'(.+?)'", response)
                    val6 = findall(f'{key}=([0-9a-zA-Z]+?)', response)  # HTML/XML属性中
                    if len(val0) > 0:
                        match = f'"{key}": "(.+?)"'
                    elif len(val1) > 0:
                        match = f"'{key}': '(.+?)'"
                    elif len(val2) > 0:
                        match = f'{key}="(.+?)"'
                    elif len(val3) > 0:
                        match = f"{key}='(.+?)'"
                    elif len(val4) > 0:
                        match = f'{key}:"(.+?)"'
                    elif len(val5) > 0:
                        match = f"{key}:'(.+?)'"
                    elif len(val6) > 0:
                        match = f'{key}=([0-9a-zA-Z]+?)'
                    else:
                        match = ''
                handle += JMETER_SCRIPT_EXTRACTOR(name=key, match=match)
                if match != '':
                    EXTRACTORED_NAME.append(key)
        for k in EXTRACTORED_NAME:
            EXTRACTOR_NAME.remove(k)
        if EXTRACTOR_NAME == []:
            NEED_EXTRACTOR = False
    if '${' in post_value or '${' in header:
        if NEED_EXTRACTOR is False:
            NEED_EXTRACTOR = True
        EXTRACTOR_NAME.extend(findall('\${(.+?)}', post_value))
        EXTRACTOR_NAME.extend(findall('\${(.+?)}', header))
    return f'''
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{escape(request_name)}" enabled="true">
          <elementProp name="HTTPsampler.Files" elementType="HTTPFileArgs">
            <collectionProp name="HTTPFileArgs.files">
              <elementProp name="{escape(file_path)}" elementType="HTTPFileArg">
                <stringProp name="File.path">{escape(file_path)}</stringProp>
                <stringProp name="File.paramname"></stringProp>
                <stringProp name="File.mimetype"></stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
            <collectionProp name="Arguments.arguments">
              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">{escape(post_value)}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.domain">{escape(netloc)}</stringProp>
          <stringProp name="HTTPSampler.port">{port}</stringProp>
          <stringProp name="HTTPSampler.protocol">{scheme}</stringProp>
          <stringProp name="HTTPSampler.contentEncoding">{contentEncoding}</stringProp>
          <stringProp name="HTTPSampler.path">{escape(path)}</stringProp>
          <stringProp name="HTTPSampler.method">{method}</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree>
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP信息头管理器" enabled="true">
            <collectionProp name="HeaderManager.headers">
              {header}
            </collectionProp>
          </HeaderManager>
          <hashTree/>
          {handle}
        </hashTree>'''

def create_jmeter(request: Optional[list] = None):
    try:
        latest = getWebList(url='https://mirrors.tuna.tsinghua.edu.cn/apache/jmeter/binaries/HEADER.html',
                            match='Apache JMeter (.+?) requires')
        version = latest[0] if len(latest) > 0 else '5.4'
    except Exception as e:
        version = '5.4'
    if request is None:
        return JMETER_SCRIPT_HEAD(version) + JMETER_EQUEST() + JMETER_SCRIPT_FOOT()
    else:
        code = ''
        if len(request) == 1 and isinstance(request[0], dict):
            try:
                code = JMETER_EQUEST(
                    post_value=request[0].get('data'),
                    url=request[0].get('url'),
                    method=request[0].get('method'),
                    headers=request[0].get('headers'),
                    response=request[0].get('response')) + code
            except KeyError as e:
                print(e)
        else:
            for i in range(len(request) - 1, -1, -1):
                v = request[i]
                try:
                    if isinstance(v, dict):
                        code = JMETER_EQUEST(
                            post_value=v.get('data'),
                            url=v.get('url'),
                            method=v.get('method'),
                            headers=v.get('headers'),
                            response=v.get('response')) + code
                except KeyError as e:
                    print(e)
        return JMETER_SCRIPT_HEAD(version) + code + JMETER_SCRIPT_FOOT()