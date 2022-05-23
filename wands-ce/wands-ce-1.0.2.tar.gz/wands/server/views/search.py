# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/23 11:29
"""

from flask import Blueprint

search = Blueprint('search', __name__)


@search.route('/address')
def address():
    return 'address'
