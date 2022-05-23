class AlphaProcess():
    def __init__(self):
        pass
    

PROCESSES = {}

PROCESS_METHOD_NAME = "process_alpha_in"
def process(name: str=None, thread:bool=False):
    def process_alpha_in(func):
        def process_wrapper(*args,**kwargs):
            return func(*args, **kwargs)

        if hasattr(func,'__name__'):
            process_wrapper.__name__ = func.__name__
        else:
            pass
        
        return process_wrapper
    return process_alpha_in