# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
import os
import time
import uuid
import threading
from melon import ROOT_DIR
from melon.settings import get_config

allure_data = os.path.abspath(os.path.join(ROOT_DIR, get_config('melon.pytest.allure_dir')))
report_dir = os.path.abspath(os.path.join(ROOT_DIR, get_config('melon.allure.report_dir')))
cases_path = os.path.abspath(os.path.join(ROOT_DIR, get_config('melon.pytest.cases_dir')))


allure_data_path = os.path.join(allure_data, str(uuid.uuid4()))
allure_report_path = os.path.join(report_dir, str(uuid.uuid4()))


def __run_pytest():
    """运行pytest"""
    args = get_config('melon.pytest.args')
    os.system(f'pytest -{" -".join(args)} {cases_path} --alluredir {allure_data_path}')


def __run_allure(auto_open):
    """运行allure"""
    os.system(f'allure generate {allure_data_path} -o {allure_report_path} --clean')
    if auto_open:
        os.system(f'allure open {allure_report_path}')


def run(auto_open_report=True):
    """运行测试"""
    __run_pytest()
    time.sleep(3)
    threading.Thread(
        target=__run_allure,
        args=(auto_open_report,),
        name='allure-report'
    ).start()
