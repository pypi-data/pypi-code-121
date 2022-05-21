# error - Contains base exception
class SfcparseError(Exception):
    """
    sfcparse base exception
    """
    __PARENT_EXCEPTION_NAME = 'sfcparse'

    def __init__(self, msg: str, item: str='') -> None:
        self.msg = str(msg)
        self.item = str(item)

    def __str__(self) -> str:
        return f'[Error] {self.msg} {self.item}'
    
    def set_module_name(module_name: str=__PARENT_EXCEPTION_NAME):
        return module_name