def import_object(name):
    components = name.split('.')
    mod = __import__(components[0])
    parts = [components[0]]
    for comp in components[1:]:
        parts.append(comp)
        try:
            mod = __import__('.'.join(parts), fromlist=[''])
        except (ImportError, ModuleNotFoundError):
            mod = getattr(mod, comp)
    return mod


def instantiate_object(descriptor):
    return import_object(descriptor['class'])(**descriptor.get('kwargs', {}))


def class_fullname(o):
    klass = o.__class__
    module = klass.__module__
    if module == 'builtins':
        return klass.__qualname__
    return module + '.' + klass.__qualname__
