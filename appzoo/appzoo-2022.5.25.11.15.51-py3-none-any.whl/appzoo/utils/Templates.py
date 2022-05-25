#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-App.
# @File         : template_loader
# @Time         : 2019-08-15 13:19
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from jinja2 import Environment, PackageLoader, select_autoescape, Template

from pathlib import Path


class Templates(object):

    def __init__(self):
        # Load the template environment with async support
        self.template_env = Environment(
            loader=PackageLoader('appzoo'),  # 所需文件
            autoescape=select_autoescape(),
            enable_async=True
        )

    def load(self):
        _ = {html.name[:-5]: self.template_env.get_template(html.name) for html in self.htmls}
        return _

    @property
    def htmls(self):
        return Path().absolute().parent.joinpath("templates").glob("*.html")


if __name__ == '__main__':
    print(Templates().load())
