# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/23 11:41
"""

from flask_script import Manager,Server

from wands.server import create_app


def manage():
    app = create_app(__name__)
    manager = Manager(app)

    manager.run()


if __name__ == "__main__":
    manage()
