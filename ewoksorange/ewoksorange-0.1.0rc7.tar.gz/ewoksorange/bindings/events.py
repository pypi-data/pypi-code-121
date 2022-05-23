from contextlib import ExitStack
from ewokscore import events
from ewokscore.events.contexts import ExecInfoType
from ewokscore.events.contexts import RawExecInfoType


def scheme_ewoks_events(scheme, execinfo: RawExecInfoType = None) -> ExecInfoType:
    scheme_execinfo = getattr(scheme, "ewoks_execinfo", None)
    if scheme_execinfo is not None:
        return scheme_execinfo
    exitstack = ExitStack()
    stack = exitstack.__enter__()
    ctx = events.job_context(execinfo)
    execinfo = stack.enter_context(ctx)
    ctx = events.workflow_context(execinfo, workflow=scheme.title)
    execinfo = stack.enter_context(ctx)
    scheme.ewoks_execinfo = execinfo

    def ewoks_finalize():
        # TODO: job and workflow end event will never capture
        #       node exceptions because they are absorbed by orange.
        exitstack.close()

    scheme.ewoks_finalize = ewoks_finalize
    scheme.destroyed.connect(ewoks_finalize)
    return execinfo
