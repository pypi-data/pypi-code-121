import os
import sys
import importlib


def import_fun(obj, mod, m=[], modename=""):
    """
    这个方法只能在类里面设置属性
    :param obj:
    :param mod:
    :param m:
    :return:
    """
    if m:
        for item in m:
            module = getattr(mod, item)
            setattr(obj, item, module)
    elif modename:
        setattr(obj, modename, mod)
    else:
        raise ValueError("m 和　modename必须存在一个")


def import_to_val(mod, m=[], globals=None, locals=None):
    """
     设置到变量,在你调用的文件中使用
    :param mod: 一个模块对象
    :param m: 一个列表　mod 里面的变量类和函数
    :param globals: 传入　globals()
    :param locals: 传入　locals()
    :return:
    """
    dicts = {}
    for item in m:
        # module = getattr(mod, item)
        exec("{}=getattr(mod, '{}')".format(item, item))
        dicts[item] = eval(item)
        if globals:
            globals.update({item: eval(item)})
        if locals:
            locals.update({item: eval(item)})
    return dicts


def import_model(name):
    """
    import 模块
    """
    return importlib.import_module(name)


def symbol_by_name(name, aliases=None, imp=None, package=None,
                   sep='.', default=None, **kwargs):
    """Get symbol by qualified name.

    The name should be the full dot-separated path to the class::

        modulename.ClassName

    Example::

        celery.concurrency.processes.TaskPool
                                    ^- class name

    or using ':' to separate module and symbol::

        celery.concurrency.processes:TaskPool

    If `aliases` is provided, a dict containing short name/long name
    mappings, the name is looked up in the aliases first.

    Examples:
        >>> symbol_by_name('celery.concurrency.processes.TaskPool')
        <class 'celery.concurrency.processes.TaskPool'>

        >>> symbol_by_name('default', {
        ...     'default': 'celery.concurrency.processes.TaskPool'})
        <class 'celery.concurrency.processes.TaskPool'>

        # Does not try to look up non-string names.
        from celery.concurrency.processes import TaskPool
        symbol_by_name(TaskPool) is TaskPool
        True
    """
    from re_common.baselibrary.utils.baseexcept import reraise
    aliases = {} if not aliases else aliases
    if imp is None:
        imp = importlib.import_module

    if not isinstance(name, str):
        return name  # already a class

    name = aliases.get(name) or name
    sep = ':' if ':' in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name
    try:
        try:
            # 这里的  **kwargs 是为了兼容 传入的 imp
            module = imp(module_name, package=package, **kwargs)
        except ValueError as exc:
            reraise(ValueError,
                    ValueError(f"Couldn't import {name!r}: {exc}"),
                    sys.exc_info()[2])
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default


def set_topdir_to_path(file, top_name):
    """

    :param file:  请传入 __file__
    :param top_name: 顶层目录的名字如 本项目为re-common
    :return:
    """
    pathlist = os.path.dirname(os.path.abspath(file)).split(os.sep)
    root_path = os.sep.join(pathlist[:pathlist.index(top_name) + 1])
    sys.path.insert(0, root_path)
    sys.path = list(set(sys.path))
