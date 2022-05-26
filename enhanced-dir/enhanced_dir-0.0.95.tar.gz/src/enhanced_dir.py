def enhanced_dir(arg, categorize=True, show_types=False, checks=False, collections_abc_list=False):
    from collections import defaultdict
    if not categorize:
        return_list = []
    passed = defaultdict(lambda: defaultdict(set))
    failed = defaultdict(set)
    passed_ = defaultdict(lambda: defaultdict(set))
    failed_ = defaultdict(lambda: defaultdict(set))
    x = arg

    for method in dir(arg):
        type_ = type(eval(f'x.{method}'))
        try:
            qualname = eval(f'x.{method}.__qualname__')
            qualname = qualname.split('.')
            passed[f'{arg}'][qualname[0]].add(qualname[1])
            passed_[f'{arg}'][type_].add(qualname[1])
        except:
            failed[f'{arg}'].add(method)
            failed_[f'{arg}'][type_].add(method)
    if categorize:
        return_list = [{'passed': passed}, {'failed': failed}]
    if show_types:
        return_list.extend(({'passed_types': passed_}, {'failed_types': failed_}))
    if collections_abc_list:
        import collections.abc
        collections_abc = {*()}
        for i in dir(collections.abc):
            try:
                if isinstance(arg, eval(f'collections.abc.{i}')):
                    collections_abc.add(i)
            except:
                pass
        return_list.append([collections_abc])
    if checks:
        checks_ = {}
        try:
            class A(x):
                pass

            checks_['inheritable'] = True
        except:
            checks_['inheritable'] = False

        try:
            a = defaultdict(arg)
            checks_['defaultdict_arg'] = True
        except:
            checks_['defaultdict_arg'] = False

        try:
            d = {arg: 1}
            checks_['dict_key'] = True
        except:
            checks_['dict_key'] = False

        try:
            for i in arg:
                pass
            checks_['iterable'] = True
        except:
            checks_['iterable'] = False
        return_list.append([checks_])

    return return_list

def two_way(operation, success=True, fail=False):
    import warnings
    warnings.filterwarnings("ignore")
    import re, keyword
    from collections import defaultdict
    failed, succeeded = defaultdict(set) * 2
    invalid = 'Error|Warning|__|ipython|display|execfile|dreload|help|license|open|get_ipython|credits|runfile' \
              '|copyright|breakpoint|input|print '
    for a, i in keyword.__builtins__.items():
        if not re.search(invalid, a):
            for b, j in keyword.__builtins__.items():
                if not re.search(invalid, b):
                    try:
                        x = eval(f'{a}() {operation} {b}()')
                        succeeded[a].add(b)
                    except:
                        failed[a].add(b)
    return_list = []

    if success:
        return_list.append({'succeeded': succeeded})
    if fail:
        return_list.append({'failed': failed})
    return return_list