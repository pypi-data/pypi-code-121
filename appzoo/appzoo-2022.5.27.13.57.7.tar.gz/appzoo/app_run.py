#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : app_run
# @Time         : 2020/11/5 4:48 下午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :
"""
'console_scripts': [
    'app-run=appzoo.app_run:cli'
]
"""
from meutils.pipe import *
from meutils.path_utils import get_module_path


class AppRun(object):
    """doc"""

    def __init__(self, **kwargs):
        pass

    def apps_list(self, apps='apps'):
        """
        apps/apps_streamlit
        """
        return list(Path(get_module_path(f'../{apps}', __file__)).glob('*'))

    def fastapi(self, app_file='demo.py', nohup=0):
        if '/' not in app_file:
            for app_file in Path(get_module_path('../apps', __file__)).glob(f'*{app_file}*'):
                break

        cmd = f"python {app_file}"
        logger.debug(cmd)

        self._run_cmd(cmd, nohup)

    def streamlit(self, app_file='demo.py', port=9955, nohup=0):
        if '/' not in app_file:
            for app_file in Path(get_module_path('../apps_streamlit', __file__)).glob(f'*{app_file}*'):
                break

        cmd = f"  {app_file} --server.baseUrlPath web --server.port {port}"
        logger.debug(cmd)

        self._run_cmd(cmd, nohup)

    def _run_cmd(self, cmd, nohup=0):
        cmd = f"nohup {cmd} &" if nohup else cmd
        return os.system(cmd)


def cli():
    fire.Fire(AppRun)


if __name__ == '__main__':
    print(AppRun().apps_list())
