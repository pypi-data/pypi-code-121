import sys
from typing import Callable, Any, Optional

import json
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from sqlalchemy import func
from vortex.Tuple import addTupleType, TupleField, Tuple

__sysPathsJson = json.dumps(sys.path)


@addTupleType
class _RunPyInPgArgTuple(Tuple):
    __tupleType__ = "peek_storage_service._RunPyInPgArgTuple"
    args = TupleField()
    kwargs = TupleField()


@addTupleType
class _RunPyInPgResultTuple(Tuple):
    __tupleType__ = "peek_storage_service._RunPyInPgResultTuple"
    result = TupleField()


def runPyInPgBlocking(
    dbSessionCreator: DbSessionCreator,
    classMethodToRun: Callable,
    classMethodToImportTuples: Optional[Callable],
    *args,
    **kwargs
) -> Any:
    # noinspection PyProtectedMember
    argTupleJson = _RunPyInPgArgTuple(args=args, kwargs=kwargs)._toJson()

    loaderModuleClassMethodToRunStr = ".".join(
        [
            classMethodToRun.__self__.__module__,
            classMethodToRun.__self__.__name__,
            classMethodToRun.__name__,
        ]
    )

    loaderModuleClassMethodToImportStr = (
        ".".join(
            [
                classMethodToImportTuples.__self__.__module__,
                classMethodToImportTuples.__self__.__name__,
                classMethodToImportTuples.__name__,
            ]
        )
        if classMethodToImportTuples
        else "None"
    )

    session = dbSessionCreator()
    try:
        sqlFunc = func.peek_storage_service.run_generic_python(
            argTupleJson,
            loaderModuleClassMethodToRunStr,
            loaderModuleClassMethodToImportStr,
            __sysPathsJson,
        )

        resultJsonStr: str = next(session.execute(sqlFunc))[0]
        session.commit()

        # noinspection PyProtectedMember
        resultTuple = _RunPyInPgResultTuple()._fromJson(resultJsonStr)

        return resultTuple.result

    finally:
        session.close()
