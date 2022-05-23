import os
import time
from os import path

from common.data.handle_common import get_system_key, set_system_key

# 获取当前编译后的路径（编译路径）
PATH = path.dirname(path.abspath(__file__))
# 获取项目的路径（编译路径）
ROOT_PATH = path.dirname(PATH)
# 获取当前路径
CURRENT_PATH = path.dirname(os.path.abspath('.'))
if not os.path.exists(path.join(CURRENT_PATH, 'config')):
    CURRENT_PATH = path.dirname(os.path.abspath('..'))
if not os.path.exists(path.join(CURRENT_PATH , 'config')):
    CURRENT_PATH = path.dirname(os.path.abspath('../..'))
if not os.path.exists(path.join(CURRENT_PATH , 'config')):
    CURRENT_PATH = path.dirname(os.path.abspath('../../..'))
set_system_key('currentpath',CURRENT_PATH)
if get_system_key("JOB_NAME") is None:
    PROJECT_NAME = CURRENT_PATH
else:
    PROJECT_NAME = get_system_key("JOB_NAME")
if get_system_key("projectname") is not None:
    PROJECT_NAME = get_system_key("projectname")

if get_system_key("AllurePath") is None:
    allure_path_evn = ''
    ALLURE_PATH = os.sep.join([allure_path_evn])
else:
    ALLURE_PATH = get_system_key("AllurePath")
PROJECT_PATH = PATH[:PATH.find(PROJECT_NAME+"\\")+len(PROJECT_NAME+"\\")]
# 获取配置文件目录
CONFIG_PATH = path.join(CURRENT_PATH, "config",)
# 获取config.yaml文件
CONFIG_YAML_PATH = path.join(CONFIG_PATH, "config.yaml",)
# 获取config.ini
CONFIG_INI_PATH = path.join(CONFIG_PATH, "config.ini",)
#获取ApiSchemal.yaml
API_YAML_PATH = path.join(CONFIG_PATH, "ApiSchemal.yaml",)
# 获取测试数据
TEST_DATA_PATH = path.join(CURRENT_PATH, "data",)
# 获取测试文件
TEST_FILE_PATH = path.join(CURRENT_PATH, "file",)
# 获取测试报告路径
TEST_TARGET_PATH = path.join(CURRENT_PATH, "target",)
# 获取Allure测试报告
TEST_TARGET_REPORT_PATH = path.join(TEST_TARGET_PATH, "report",)
# 获取Allure测试报告
TEST_TARGET_RESULTS_PATH = path.join(TEST_TARGET_PATH, "results",)
# 获取测试用例路径
TEST_PATH = path.join(CURRENT_PATH, "test",)
# 获取日志路径
LOG_PATH=path.join(CURRENT_PATH, "log",)
# 获取日志文件
LOG_PATH_FILE=path.join(LOG_PATH, "log_"+time.strftime("%Y-%m-%d", time.localtime())+".log",)
# 获取场景用例路径
TEST_SCENE_PATH=path.join(TEST_PATH, "test_scene",)
# 获取单接口用例路径
TEST_SINGLE_PATH=path.join(TEST_PATH, "test_single",)










