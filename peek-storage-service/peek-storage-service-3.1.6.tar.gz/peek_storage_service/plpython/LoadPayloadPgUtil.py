import sys
from collections import namedtuple
from typing import Callable, Dict, Optional

import json
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Select

from peek_plugin_base.storage.DbConnection import DbSessionCreator

_LoadPayloadTupleResult = namedtuple(
    "_LoadPayloadTupleResult", ["count", "encodedPayload"]
)

__sysPathsJson = json.dumps(sys.path)


def callPGLoadPayloadTuplesBlocking(
    dbSessionCreator: DbSessionCreator,
    sql: Select,
    sqlCoreLoadTupleClassmethod: Callable,
    payloadFilt: Optional[Dict] = None,
    fetchSize=50,
) -> _LoadPayloadTupleResult:
    payloadFileJson = json.dumps(payloadFilt if payloadFilt else {})

    sqlStr = str(
        sql.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )

    loaderModuleClassMethodStr = ".".join(
        [
            sqlCoreLoadTupleClassmethod.__self__.__module__,
            sqlCoreLoadTupleClassmethod.__self__.__name__,
            sqlCoreLoadTupleClassmethod.__name__,
        ]
    )

    session = dbSessionCreator()
    try:
        sqlFunc = func.peek_storage_service.load_paylaod_tuples(
            sqlStr,
            payloadFileJson,
            loaderModuleClassMethodStr,
            __sysPathsJson,
            fetchSize,
        )

        resultJsonStr: str = next(session.execute(sqlFunc))[0]

        resultJson: Dict = json.loads(resultJsonStr)
        if resultJson["encodedPayload"]:
            resultJson["encodedPayload"] = resultJson["encodedPayload"].encode()

        return _LoadPayloadTupleResult(**resultJson)

    finally:
        session.close()
