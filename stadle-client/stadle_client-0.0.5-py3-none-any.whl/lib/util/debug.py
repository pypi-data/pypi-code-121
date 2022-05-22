def debug_with_stdout(clazz: str, func: str, msg: str):
    """
    A supporting debug function.
    Args:
        clazz (str): the class name which includes the function
        func (str): function name
        msg (str): message

    Examples
    --------
    >>> class A:
    ...     def __init__(self):
    ...         pass
    ...     def print_hello(self):
    ...         print("Hello")
    ...     @property
    ...     def name(self):
    ...         return self.__class__.__name__.__repr__()
    ...
    >>> a_instance = A()
    >>> from stadle import debug_with_stdout
    >>> debug_with_stdout(a_instance.name, "print_hello", "this is a test function")
            ================================================================================
            DEBUG MESSAGE : ['A']::<print_hello>
            this is a test function
            ================================================================================
    """
    print("=" * 80)
    print(f"DEBUG MESSAGE : [{clazz}]::<{func}>")
    print(msg)
    print("=" * 80)
