# coding=utf-8
import json
import os
import sys
import pytest
from qrunner.utils.log import logger
from qrunner.utils.config import conf


class TestMain(object):
    """
    Support for app and web
    """
    def __init__(self,
                 platform='api',
                 serial_no=None,
                 pkg_name=None,
                 browser_name='chrome',
                 case_path='test_dir',
                 rerun=0,
                 concurrent=False,
                 base_url=None,
                 headers=None,
                 login_key=None,
                 timeout=30,
                 report_path='report'
                 ):
        """
        :param platform str: 平台，如web、android、ios、api
        :param serial_no str: 设备id，如UJK0220521066836、00008020-00086434116A002E
        :param pkg_name str: 应用包名，如com.qizhidao.clientapp、com.qizhidao.company
        :param browser_name str: 浏览器类型，如chrome、其他暂不支持
        :param case_path str: 用例路径
        :param rerun int: 失败重试次数
        :param concurrent bool: 是否需要并发执行，只支持platform为browser的情况
        :@param base_url str: 接口host
        "@param headers dict: 额外的请求头，{
            "accessToken": "xxxx",
            "signature": "xxxx"
        }
        :@param login_key list：headers中跟登录相关的key
        :@param timeout int: 接口请求超时时间
        :@param report_path str: 报告生成目录
        """

        self.platform = platform
        self.serial_no = serial_no
        self.pkg_name = pkg_name
        self.browser_name = browser_name
        self.case_path = case_path
        self.rerun = str(rerun)
        self.concurrent = concurrent
        self.base_url = base_url
        self.headers = headers
        self.login_key = login_key
        self.timeout = str(timeout)
        self.report_path = report_path

        # 将数据写入全局变量
        if self.platform is not None:
            conf.set_item('common', 'platform', self.platform)
        if self.serial_no is not None:
            conf.set_item('app', 'serial_no', self.serial_no)
        if self.pkg_name is not None:
            conf.set_item('app', 'pkg_name', self.pkg_name)
        if self.browser_name is not None:
            conf.set_item('web', 'browser_name', self.browser_name)
        if self.base_url is not None:
            conf.set_item('common', 'base_url', self.base_url)
        else:
            if self.platform == 'api' or self.platform == 'web':
                print('base_url未配置，请配置后重新执行~')
                sys.exit()
        if self.headers is not None:
            conf.set_item('common', 'headers', headers)
        if login_key is not None:
            conf.set_item('api', 'login_key', login_key)
        if self.timeout is not None:
            conf.set_item('common', 'timeout', self.timeout)
        conf.set_item('common', 'report_path', self.report_path)

        # 执行用例
        logger.info('执行用例')
        logger.info(f'平台: {self.platform}')
        cmd_list = [
            '-sv',
            '--reruns', self.rerun,
            '--alluredir', 'allure-results', '--clean-alluredir'
        ]
        if self.case_path:
            cmd_list.insert(0, self.case_path)
        if self.concurrent:
            if self.platform == 'web' or self.platform == 'api':
                cmd_list.insert(1, '-n')
                cmd_list.insert(2, 'auto')
                cmd_list.insert(3, '--dist=loadscope')
            else:
                logger.info(f'{self.platform}平台不支持并发执行')
                sys.exit()
        logger.info(cmd_list)
        pytest.main(cmd_list)

        # 用例完成后操作
        conf.set_item('common', 'headers', {})  # 清除登录态
        os.system(f'allure generate allure-results -o {self.report_path} --clean')  # 生成报告


main = TestMain


if __name__ == '__main__':
    main()

