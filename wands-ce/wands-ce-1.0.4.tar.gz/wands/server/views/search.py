# -*- coding: utf-8 -*-

"""
@author: onefeng
@time: 2022/5/23 11:29
"""

from flask import Blueprint, request, jsonify

from wands import AddressParse

search = Blueprint('search', __name__)

address_parse = AddressParse()


@search.route('/')
def index():
    return 'Welcome,wands!'


@search.route('/address')
def address():
    area = request.args.get("area")
    data = address_parse(area)
    result = {'code': 200, 'data': data, 'message': 'success'}
    return jsonify(result), 200
