from time import time, sleep
import pandas as pd
import requests

def table_head(df):
        return df.head()

class Vizual:
    def __init__(self, server_ip='http://0.0.0.0:8080', live_post=False):
        sleep(1)
        self._ip = server_ip
        self._channel_context = ''
        self._context_stack = []
        self._is_test = True
        self.message_q = []
        self.live_post = live_post

    def post(self, url, msg=None):
        if self.live_post:
            requests.post(self._ip + url, json=msg)
        else:
            self.message_q.append([url, msg])

    def _post_messages(self):
        while len(self.message_q) > 0:
            url, msg = self.message_q.pop(0)
            requests.post(self._ip + url, json=msg)

    def entry_point(self):
        def entry_wrapper(entry_func):
            def modified_func(*args, **kwargs):
                # Run Test Mode
                entry_func(*args, **kwargs)
                self._is_test = False

                # Run Dev Mode
                res = entry_func(*args, **kwargs)
                
                # Transmit all messages once programme has ended
                self._post_messages()
                return res
            return modified_func
        return entry_wrapper

    def _apply_decorators(self, f, d_fns):
        f_prime = f
        
        for i in range(len(d_fns) - 1,-1,-1):
            decorator = d_fns[i]
            f_prime = decorator(f_prime)

        return f_prime

    def decorate(self, test = [], dev = [], universal = []):
        def decorate_inner(f):
            _test_f = self._apply_decorators(f, test)
            _dev_f = self._apply_decorators(f, dev)

            def modified_function(*args, **kwargs):
                if self._is_test:
                    return _test_f(*args, **kwargs)
                else:
                    return _dev_f(*args, **kwargs)

            return self._apply_decorators(modified_function, universal)

        return decorate_inner

    def _register_channel(self, channel):
        self.post('/channels/%s' % channel, None)

    def _send_debug_message(self, channel, msg):
        self.post('/channels/%s' % channel, msg)

    def _set_channel_context(self, channel):
        self._context_stack.append(channel)

    def _get_channel_context(self):
        return self._context_stack[-1]

    def _pop_channel_context(self):
        self._context_stack.pop(-1)

    def label(self, channel):
        self._register_channel(channel)

        def label_decorator(func):
            def modified_func(*args, **kwargs):
                self._set_channel_context(channel)
                evaluation = func(*args, **kwargs)
                self._pop_channel_context()

                return evaluation
            return modified_func
        return label_decorator

    def table(self, table_name, color='#fff', summary_fn = table_head):
        def table_decorator(func):
            def wrapper(*args, **kwargs):
                table_eval = func(*args, **kwargs)
                
                msg = {
                    'timestamp': time(),
                    'table': summary_fn(table_eval).to_html(border=0),
                    'table_name': table_name,
                    'format': {'color': color}
                }

                self._send_debug_message(self._get_channel_context(), msg)
                
                return table_eval
            return wrapper
        return table_decorator

    def debug(self, template, color='#fff', display_output=True): 
        def debug_decorator(func):
            def wrapper(*args, **kwargs):
                # Frist set the context
                evaluation = func(*args, **kwargs)
                content = template % evaluation if display_output else template

                msg = {
                    'timestamp': time(),
                    'message': content,
                    'format': {'color': color}
                }

                self._send_debug_message(self._get_channel_context(), msg)
                
                return evaluation
            
            return wrapper

        return debug_decorator

    def task(self, task_name, total_iters): 
        def task_decorator(func):
            def wrapper(*args, **kwargs):
                msg = {
                    'task_name': task_name,
                    'total_iters': total_iters,
                }

                self.post('/task/new', msg)

                # Pass thru the intercepted value
                return func(*args, **kwargs)
            
            return wrapper

        return task_decorator

    def task_progress(self, increment): 
        def task_progress_decorator(func):
            def wrapper(*args, **kwargs):
                msg = {
                    'increment': increment,
                }

                self.post('/task/update', msg)

                # Pass thru the intercepted value
                return func(*args, **kwargs)
            
            return wrapper

        return task_progress_decorator

    def ping(self, color='rgb(211,183,124)'):
        # Note pings must be run inside a @debug scope
        # Pings must wrap functions which return boolean expr.
        def ping_decorator(func):
            def wrapper(*args, **kwargs):
                criteria_met = func(*args, **kwargs)

                if criteria_met:
                    msg = {
                        'timestamp': time(),
                        'message': 'Ping!',
                        'format': {'color': color}
                    }
                    
                    self.post('/channels/%s' % self._get_channel_context(), msg)

                return criteria_met
            return wrapper
        return ping_decorator

    def unit_test(self, unit_test_fns):
        # unit_test_fns: list of functions which accept the decorated function
        # as the only argument and returns a boolean true = passed

        def unit_test_decorator(func):
            tests = [] # Trick to ensure we only run the tests once.
            # Only wrapper gets called on each call of func()

            def wrapper(*args, **kwargs):
                if len(tests) == 0:
                    for test_fn in unit_test_fns:
                        msg = {
                            'function': func.__name__,
                            'test_name': test_fn.__name__,
                            'is_passing': test_fn(func)
                        }

                        tests.append(msg)

                    self.post('/tests/%s' % self._get_channel_context(), tests)

                return func(*args, **kwargs)

            return wrapper
        return unit_test_decorator

    def time(self):
        def time_decorator(func):
            def wrapper(*args, **kwargs):
                channel = self._get_channel_context()
                
                a = time()
                eval = func(*args, **kwargs)
                b = time()

                msg = {
                    'function': func.__name__,
                    'duration': b - a,
                }
                    
                self.post('/timing/%s' % channel, msg)

                return eval
            return wrapper
        return time_decorator