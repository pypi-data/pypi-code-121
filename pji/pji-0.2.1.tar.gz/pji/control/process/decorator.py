import os
from functools import wraps
from typing import Optional

import where

from ..model import ResourceLimit, Identification
from ...utils import args_split


def _do_nothing():
    pass


def _attach_preexec_fn(preexec_fn=None, pre_attach=None, post_attach=None):
    preexec_fn = preexec_fn or _do_nothing
    pre_attach = pre_attach or _do_nothing
    post_attach = post_attach or _do_nothing

    @wraps(preexec_fn)
    def _new_preexec_fn():
        pre_attach()
        preexec_fn()
        post_attach()

    return _new_preexec_fn


def workdir_setter(func):
    @wraps(func)
    def _func(*args, cwd: Optional[str] = None, preexec_fn=None, **kwargs):
        cwd = cwd or os.getcwd()
        if not os.path.exists(cwd):
            raise FileNotFoundError('Path {cwd} not found.'.format(cwd=repr(cwd)))
        if not os.path.isdir(cwd):
            raise NotADirectoryError('{cwd} is not a directory.'.format(cwd=repr(cwd)))

        def _change_dir_func():
            os.chdir(cwd)

        preexec_fn = _attach_preexec_fn(preexec_fn, pre_attach=_change_dir_func)
        return func(*args, preexec_fn=preexec_fn, **kwargs)

    return _func


_REAL_TIME_LIMIT_KEY = 'real_time_limit'


def resources_setter(func):
    @wraps(func)
    def _func(*args, resources=None, preexec_fn=None, **kwargs):
        resources = ResourceLimit.loads(resources)

        def _apply_resource_limit_func():
            resources.apply()

        preexec_fn = _attach_preexec_fn(preexec_fn, post_attach=_apply_resource_limit_func)
        return func(*args, preexec_fn=preexec_fn, resources=resources, **kwargs)

    return _func


def users_setter(func):
    @wraps(func)
    def _func(*args, identification=None, preexec_fn=None, **kwargs):
        identification = Identification.loads(identification)

        def _apply_user_func():
            identification.apply()

        preexec_fn = _attach_preexec_fn(preexec_fn, post_attach=_apply_user_func)
        return func(*args, preexec_fn=preexec_fn, **kwargs)

    return _func


def shell_setter(func):
    @wraps(func)
    def _func(*args_, args, shell: bool = False, **kwargs):
        if shell:
            if isinstance(args, str):
                if where.first('sh'):
                    args = [where.first('sh'), '-c', args]
                elif where.first('cmd'):
                    args = [where.first('cmd'), '/c', args]
                else:
                    raise EnvironmentError('Neither shell nor cmd found in this environment.')
            else:
                raise ValueError(
                    'When shell is enabled, args should be str but {actual} found.'.format(actual=repr(type(args))))
        else:
            args = args_split(args)

        return func(*args_, args=args, **kwargs)

    return _func


def process_setter(func):
    @wraps(func)
    @users_setter
    @resources_setter
    @workdir_setter
    @shell_setter
    def _func(*args, **kwargs):
        return func(*args, **kwargs)

    return _func
