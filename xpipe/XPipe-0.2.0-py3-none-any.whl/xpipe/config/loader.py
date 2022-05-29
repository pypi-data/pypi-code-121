import importlib 

def parse_path(class_path, aliases=None):
    """
    Get the path of a class from a given path using importlib library.
    """
    if aliases is not None:
        for alias, path in aliases.items():
            n = len(alias)
            if class_path[:n] == alias:
                class_path = path + class_path[n:]
    return class_path

def load_class(class_path, aliases=None):
    """
    Load a class from a given path using importlib library.
    """
    class_path = parse_path(class_path, aliases)
    module_path, class_name = class_path.rsplit('.', 1)
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError('Could not import module %s: %s' % (module_path, e))
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise AttributeError('Module "%s" does not have an element "%s"' % (module_path, class_name))
