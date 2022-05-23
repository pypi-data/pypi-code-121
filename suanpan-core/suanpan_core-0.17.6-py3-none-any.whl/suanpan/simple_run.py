import sys
import inspect
from suanpan.app import app, MessageHandler
from suanpan.node import node


def simple_run():
    run_func = None
    initialize_func = None

    main = sys.modules['__main__']
    for name, func in inspect.getmembers(main):
        if name == 'run':
            run_func = func
        elif name == 'initialize':
            initialize_func = func

    if run_func:
        app.use(MethodHandler(run_func, initialize_func))
        app.start()


class MethodHandler(MessageHandler):
    def __init__(self, run_f, initialize_f=None):
        super().__init__()
        self._run_f = run_f
        self._initialize_f = initialize_f

    @property
    def inputs(self):
        return node.inargs

    @property
    def outputs(self):
        return node.outargs

    @property
    def params(self):
        return node.paramargs

    def initialize(self):
        if self._initialize_f:
            self._initialize_f(self.context)

    def run(self, context):
        # inputs = app.load(node.inargs)
        return self._run_f(context)
