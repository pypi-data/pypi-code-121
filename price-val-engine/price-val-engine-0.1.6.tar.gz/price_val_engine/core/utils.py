from importlib import import_module

def is_number(value):
    try:
        float(value)
        return True
    except:
        return False
    
    
def import_model(name:str):
    components = name.split('.')
    Klass = components.pop()
    module = import_module(".".join(components))
    return getattr(module, Klass)