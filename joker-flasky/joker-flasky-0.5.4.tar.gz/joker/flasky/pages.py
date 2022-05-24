#!/usr/bin/env python3
# coding: utf-8
from __future__ import annotations

import flask
from joker.flasky.environ import JokerInterface
from joker.flasky.viewutils import ViewEntry

ji = JokerInterface()


def respond_login_page(
        username='', password='',
        title='Login', usejson=False) -> str:
    tpl = ji.jinja2_env.get_template('login.html')
    return tpl.render(
        username=username,
        password=password,
        title=title,
        usejson=usejson,
    )


def respond_upload_page(
        label='Choose a file to upload', title='Upload') -> str:
    tpl = ji.jinja2_env.get_template('upload.html')
    return tpl.render(label=label, title=title)


def respond_help_page(entry: ViewEntry):
    ctx = {
        'captions': list(entry.iter_captions()),
        'endpoint': entry.endpoint,
    }
    ctx.update(entry.help)
    ctx['docstring'] = entry.docstring
    tpl = ji.jinja2_env.get_template('help.html')
    return tpl.render(ctx)


def respond_helplist_page(url_prefix: str, *view_entries: ViewEntry):
    if not view_entries:
        view_entries = ViewEntry.get_all(flask.current_app).values()
    view_entries = list(view_entries)
    view_entries.sort(key=lambda ent: ent.endpoint)
    tpl = ji.jinja2_env.get_template('helplist.html')
    return tpl.render(entries=view_entries, url_prefix=url_prefix)
