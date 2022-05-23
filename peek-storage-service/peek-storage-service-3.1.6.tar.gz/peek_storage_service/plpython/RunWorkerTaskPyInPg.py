import json
import sys
from typing import Callable, Any

import json
from sqlalchemy import func
from vortex.Tuple import Tuple, addTupleType

from peek_plugin_base.storage.DbConnection import DbSessionCreator

__sysPathsJson = json.dumps(sys.path)


@addTupleType
class _RunPyInWorkerArgsTuple(Tuple):
    __tupleType__ = "peek_storage_service." + "_RunPyInWorkerArgsTuple"
    __slots__ = ("args", "kwargs")


@addTupleType
class _RunPyInWorkerResultTuple(Tuple):
    __tupleType__ = "peek_storage_service." + "_RunPyInWorkerResultTuple"
    __slots__ = ("result",)


def runPyWorkerTaskInPgBlocking(
    dbSessionCreator: DbSessionCreator,
    sqlaUrl: str,
    moduleMethodToRun: Callable,
    *argsTuple,
    **kwargs
) -> Any:
    argsTuple = _RunPyInWorkerArgsTuple(args=argsTuple, kwargs=kwargs)

    funcPath = moduleMethodToRun.__repr__().strip("<>").split(" ")[1]

    session = dbSessionCreator()
    try:
        sqlFunc = func.peek_storage_service.run_worker_task_python(
            sqlaUrl, json.dumps(argsTuple.toJsonDict()), funcPath, __sysPathsJson
        )

        resultJsonStr: str = next(session.execute(sqlFunc))[0]
        session.commit()

        resultTuple = _RunPyInWorkerResultTuple().fromJsonDict(
            json.loads(resultJsonStr)
        )

        return resultTuple.result

    finally:
        session.close()
