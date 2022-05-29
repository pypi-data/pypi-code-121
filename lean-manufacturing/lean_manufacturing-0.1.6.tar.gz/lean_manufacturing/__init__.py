from .phases import process_until_completed, localdb, log

class Lean:

    def value_stream(value_stream, **decorator_kwargs):
        def wrapper(function):
            def applicator(*args, **function_kwargs):
                
                process_until_completed(value_stream, function, decorator_kwargs, function_kwargs)

            return applicator
        return wrapper

