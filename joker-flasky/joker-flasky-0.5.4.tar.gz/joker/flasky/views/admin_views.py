#!/usr/bin/env python3
# coding: utf-8

import flask
from flask import Blueprint, current_app

from joker.redis.loggers import ErrorInterface
from joker.flasky.viewutils import respond, respond_plain_text

bp = Blueprint('_admin', __name__)


class _EIWrapper:
    def __init__(self, error_interface: ErrorInterface):
        self.ei = error_interface

    def respond_error_list(self):
        error_keys = self.ei.query_recent_error_keys()
        tags = []
        for ek in error_keys:
            url = flask.url_for(flask.request.url_rule.endpoint, error_key=ek)
            tags.append(
                f'<pre><a href="{url}">{ek}</a></pre>'
            )
        return ''.join(tags)

    def respond_error_info(self, error_key: str):
        if 'i' in flask.request.args:
            return self.ei.query(error_key, human=True)
        url = flask.url_for(
            flask.request.url_rule.endpoint,
            error_key=error_key, i='',
        )
        return self.ei.query_html(error_key, url)


def _echo():
    return {
        # '_': vars(flask.request),
        'method': flask.request.method,
        'headers': dict(flask.request.headers),
        'args': flask.request.args,
        'json': flask.request.json,
        'form': flask.request.form,
    }


@bp.route('/r')
def admin_raise_error():
    raise RuntimeError('error raised intentionally')


@bp.route('/g')
def admin_g():
    return vars(flask.g)


@bp.route('/echo', methods=['GET', 'POST'])
def admin_echo():
    return _echo()


@bp.route('/site-map')
def admin_site_map():
    """
    site-map
    """
    urls = [r.rule for r in current_app.url_map.iter_rules()]
    urls.sort()
    if flask.request.args.get('fmt') == 'text':
        text = '\n'.join(urls)
        return respond_plain_text(text)
    return respond(urls)


@bp.route('/e/')
@bp.route('/e/<error_key>')
@bp.route('/err/')
@bp.route('/err/<error_key>')
def admin_query_error(error_key: str = None):
    ei = getattr(current_app, 'error_interface')
    if not ei:
        return '<pre>current_app.error_interface is not available.</pre>'
    eiw = _EIWrapper(ei)
    if not error_key:
        return eiw.respond_error_list()
    return eiw.respond_error_info(error_key)
