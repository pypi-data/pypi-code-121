# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/23 11:41
"""

from wands.server import create_app


def manage(host='0.0.0.0', port=9989):
    app = create_app(__name__)
    app.run(host, port)


if __name__ == "__main__":
    manage()
