#! /usr/bin/env python
# -*- coding=utf-8 -*-
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'template_code.py'
__create_time__ = '2020/11/11 19:19'

yaml_template_code = '''\
# 本数据仅限于Python语言的PyYaml库正常解析，不保证其它库可正常解析
public:
  version: 1.0
  site: &site http://test.xiaobai.com/api/
  env:
    token: 0
list:
  - title: 登录
    method: POST
    headers:
      Content-Type: application/x-www-form-data
    url: !!python/object/apply:os.path.join [*site, login]
    paramers:
    data: username=username&password=password
    assert_mode: json
    assert_path: code
    assert_value: 200
    extract_mode: json
    extract_at: body
    extract_path: data.token
    extract_name: token
  - title: 注册
    method: POST
    url: !!python/object/apply:os.path.join [*site, register]
    paramers:
    data: username=username&password=password&repassword=password
    assert_mode: json
    assert_path: code
    assert_value: 200
  - title: 列表
    method: GET
    headers:
      token: ${token}
    url: !!python/object/apply:os.path.join [*site, list]
    assert_mode: json
    assert_path: code
    assert_value: 200
    extract_mode: json
    extract_at: body
    extract_path: data[1].id
    extract_name: id
'''

appium_head_template_code = '''#! /usr/bin/env python
%s
from appium import webdriver
from selenium.webdriver.common.by import By

caps = {
    'automationName': 'uiautomator2',
    'platformName': 'Android',
    'platformVersion': '%s',
    'deviceName': '%s',
    'noReset': True,
    'allowClearUserData': 'true',
    'fullReset': "false",
    'exported': "true",
    'appPackage': '%s',
    'appActivity': '%s',
    'unicodeKeyboard': True,
    'resetKeyboard': True
}

app = webdriver.Remote('http://127.0.0.1:4723/wd/hub', caps)
# 点击动作可以录制，输入动作需要手动修改
'''

appium_location_by_xpath_of_click_template_code = '''
# xpath定位
app.find_element(by=By.XPATH, value='%s').click()
'''

appium_location_by_xpath_of_sendkeys_template_code = '''
# xpath定位
app.find_element(by=By.XPATH, value='%s').send_keys('#输入的内容#')
'''

appium_location_by_position_template_code = '''
# 点击坐标
app.swipe(%s, %s, 500)
'''
