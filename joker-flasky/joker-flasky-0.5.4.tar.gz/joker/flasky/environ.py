#!/usr/bin/env python3
# coding: utf-8

"""
For internal use within `joker-flasky`.
"""

from functools import cached_property

import volkanic


class JokerInterface(volkanic.GlobalInterface):
    package_name = 'joker.flasky'

    @cached_property
    def jinja2_env(self):
        # noinspection PyPackageRequirements
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        env = Environment(
            loader=FileSystemLoader(self.under_package_dir('templates')),
            autoescape=select_autoescape(['html', 'xml']),
            **self.conf.get('_jinja2_env', {})
        )
        env.policies["json.dumps_kwargs"]['ensure_ascii'] = False
        return env
