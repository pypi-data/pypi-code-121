import time
import warnings
from functools import wraps

from helper.rule import Utilities


class TimeLogger:
    def __init__(self):
        self._total_time_call_stack = [0]

    def timeLog(self):
        def _timeLog(fn):
            @wraps(fn)
            def wrapped_fn(*args, **kwargs):
                self._total_time_call_stack.append(0)

                start_time = time.time()

                try:
                    result = fn(*args, **kwargs)
                finally:
                    elapsed_time = time.time() - start_time

                    self._total_time_call_stack[-1] += elapsed_time

                    hours, rem = divmod(time.time() - start_time, 3600)
                    minutes, seconds = divmod(rem, 60)
                    elapsed_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

                    # log the result
                    self.log_trigger(message={
                        'function_name': fn.__name__,
                        'total_time': elapsed_time,
                    })

                return result

            return wrapped_fn

        return _timeLog

    def log_trigger(self, message):
        self.timing_save_as_log_format(message)

    def timing_save_as_log_format(self, message):
        # TODO read PATH from config
        PATH = 'TimingResult.log'
        tLf = Utilities.file_exist_check_and_open(PATH)

        L = '[TimeTracker >] {function_name} {total_time}'.format(**message)
        tLf.writelines(L + '\n')
        tLf.close()


class Logger:

    @staticmethod
    def disable_warnings():
        # remove all the annoying warnings from tf v1.10 to v1.13
        import logging

        logging.getLogger('tensorflow').disabled = True

        def warn(*args, **kwargs):
            pass

        warnings.warn = warn


time_tracker = TimeLogger()
disable_warnings = Logger.disable_warnings()