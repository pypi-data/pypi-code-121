#!/usr/bin/env python3
# coding: utf-8

from os.path import splitext

import flask

bp = flask.Blueprint('_ctxmap', __name__)


@bp.route('/')
@bp.route('/<path:path>')
def ctxmap_render(path='index'):
    ctxmap = getattr(flask.current_app, 'ctxmap')
    name, ext = splitext(path)
    if ext and ext != '.html':
        return flask.abort(404)
    try:
        context = ctxmap[name]
        template_path = context['_prot'] + '.html'
    except KeyError:
        return flask.abort(404)
    return flask.render_template(template_path, **context)
