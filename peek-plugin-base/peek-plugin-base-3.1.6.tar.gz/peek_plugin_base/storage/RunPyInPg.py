from logging import Logger
from typing import Any, Optional, Callable

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from vortex.DeferUtil import deferToThreadWrapWithLogger


def runPyInPg(
    logger: Logger,
    dbSessionCreator: DbSessionCreator,
    classMethodToRun: Callable,
    classMethodToImportTuples: Optional[Callable],
    *args,
    **kwargs
) -> Any:
    return deferToThreadWrapWithLogger(logger)(runPyInPgBlocking)(
        dbSessionCreator, classMethodToRun, classMethodToImportTuples, *args, **kwargs
    )


def runPyInPgBlocking(
    dbSessionCreator: DbSessionCreator,
    classMethodToRun: Any,
    classMethodToImportTuples: Optional[Callable],
    *args,
    **kwargs
) -> Any:
    from peek_storage_service.plpython.RunPyInPg import runPyInPgBlocking

    return runPyInPgBlocking(
        dbSessionCreator, classMethodToRun, classMethodToImportTuples, *args, **kwargs
    )
