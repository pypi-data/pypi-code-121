# coding: utf-8
import flask
from ...common import pb_root
from ...util import api_base
from ..ops import common
from ...user.ops import user_base


@pb_root.route('/auth/api/debug/dump', methods=['GET'])
def dump():
    result = {'sid': getattr(flask.session, 'sid', ''),
              'is_logined': common.is_logined(flask.request, flask.session)}
    return api_base.send_json_result("SUCC", result=result)


@pb_root.route('/auth/api/debug/login', methods=['GET'])
def debug_login():
    if common.is_logined(flask.request, flask.session):
        return api_base.send_json_result("USER_LOGIN")
    user = None
    for k, v in flask.request.args.items():
        user = user_base.query_by_info(k, v).first()
        if user:
            break
    if user:
        common.login(user, flask.request, flask.session)
        common.record_login(str(user.id), 'debug', **flask.request.headers)
        return api_base.send_json_result("SUCC")
    else:
        return api_base.send_json_result("AUTH")
