# coding=utf-8
# pip v10.0.0以上版本需要导入下面的包
from subprocess import call

from pip._internal.utils.misc import get_installed_distributions

'''
用于升级python的扩展包一次性升级所有另外提供命令行方式
pip install pip-review
pip-review --local --interactive

环境迁移
pip freeze > requirements.txt

pip uninstall -ry requirements.txt

pip install -r requirements.txt
'''
for dist in get_installed_distributions():
    call("pip install --upgrade " + dist.project_name, shell=True)

