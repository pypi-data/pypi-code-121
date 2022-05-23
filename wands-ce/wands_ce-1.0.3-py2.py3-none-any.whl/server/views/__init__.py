# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/23 11:28
"""

from .search import search

BLUEPRINT = (
    search,
)


def register_api(app):
    for blueprint in BLUEPRINT:
        app.register_blueprint(blueprint)
