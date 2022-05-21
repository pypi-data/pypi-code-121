from pynextflow import Channel
from pynextflow.entities.workflow import Workflow
from pynextflow.executors import Executor


class Local(Executor):

    def __init__(self):
        Executor.__init__(self)

    def run(self, workflow: Workflow, returns=False):

        if isinstance(workflow.args, tuple) and isinstance(workflow.args[0], Channel):
            results = []
            for i, a in enumerate(workflow.args[0]._generator(), start=1):
                if not isinstance(a, tuple):
                    a = (a,)
                print(f"[{i}] Running {workflow.func.__name__}{tuple(a)}")
                res = workflow.func(*a)
                results.append(res)
            return results

        return workflow.func(*workflow.args)


