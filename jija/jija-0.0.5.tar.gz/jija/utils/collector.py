import inspect


def collect_subclasses(module, instance):
    members = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, instance) and obj != instance:
            line = inspect.getsourcelines(obj)[1]
            members.append((line, obj))

    return map(lambda item: item[1], sorted(members, key=lambda item: item[0]))
