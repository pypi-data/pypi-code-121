_notebook_check_logger = __import__('logging').getLogger('notebook-checker')
_notebook_module_type = __import__('types').ModuleType
_notebook_get_traceback = __import__('traceback')
_notebook_log_store = set()

def _notebook_log_error(message):
    if message not in _notebook_log_store:
        _notebook_log_store.add(message)
        _notebook_check_logger.error(message)

