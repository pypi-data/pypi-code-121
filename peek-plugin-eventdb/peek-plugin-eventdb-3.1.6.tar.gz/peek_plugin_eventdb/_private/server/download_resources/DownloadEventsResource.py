import json
import logging
from typing import Dict

from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from txhttputil.site.BasicResource import BasicResource
from vortex.TupleSelector import TupleSelector

from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_base.storage.RunPyInPg import runPyInPg
from peek_plugin_eventdb._private.server.tuple_providers.EventDBEventTupleProvider import (
    EventDBEventTupleProvider,
)

logger = logging.getLogger(__name__)


class _Prop:
    def __init__(self, name: str):
        self.name = name
        self.nameByValueMap = {}


class DownloadEventsResource(BasicResource):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        Resource.__init__(self)
        self._dbSessionCreator = dbSessionCreator

    def render_GET(self, request):
        tupleSelectorStr = request.args[b"tupleSelector"][0].decode()

        request.responseHeaders.setRawHeaders("content-type", ["text/csv"])
        logger.info("Received download request for events.")
        logger.debug(
            "Download request received with TupleSelector = %s.", tupleSelectorStr
        )

        def good(data):
            request.write(data.encode())
            request.finish()
            logger.info("Finished download of events")

        def bad(failure):
            request.setResponseCode(500)
            e = failure.value
            logger.exception(e)

            request.finish()

        d = runPyInPg(
            logger,
            self._dbSessionCreator,
            self._loadInPg,
            EventDBEventTupleProvider._importTuples,
            tupleSelectorStr=tupleSelectorStr,
        )

        d.addCallbacks(good, bad)

        def closedError(failure):
            logger.error("Got closedError %s" % failure)

        request.notifyFinish().addErrback(closedError)

        return NOT_DONE_YET

    @classmethod
    def _loadInPg(cls, plpy, tupleSelectorStr: str):
        tupleSelector = TupleSelector.fromJsonStr(tupleSelectorStr)
        columnPropKeys = tupleSelector.selector["columnPropKeys"]

        modelSetId = EventDBEventTupleProvider.getModelSetId(
            plpy, tupleSelector.selector["modelSetKey"]
        )

        propByKey = cls._getPropertyByKey(plpy, modelSetId)

        tuples = EventDBEventTupleProvider.loadTuples(plpy, tupleSelector)

        data = ""

        # Write the heading
        cols = ["Date", "Time", "Milliseconds", "UTC Offset"]
        for columnPropKey in columnPropKeys:
            cols.append('"%s"' % propByKey[columnPropKey].name)

        data += ",".join(cols) + "\r\n"

        # Write the data of the table
        for row in tuples:
            value = json.loads(row.value)
            tz = str(row.dateTime.strftime("%z"))
            cols = [
                row.dateTime.strftime("%d-%b-%Y"),
                row.dateTime.strftime("%H:%M:%S"),
                str(int(row.dateTime.microsecond / 1000)),
                "%s:%s" % (tz[:-2], tz[-2:]),
            ]

            for columnPropKey in columnPropKeys:
                prop = propByKey[columnPropKey]
                val = value.get(columnPropKey)

                if val is None:
                    cols.append("")
                else:
                    # Map the value if it has one.
                    valKey = str(val).replace("null", "none").lower()
                    val = prop.nameByValueMap.get(valKey, val)

                    if isinstance(val, int):
                        cols.append(str(val))
                    else:
                        cols.append('"%s"' % val)

            data += ",".join(cols) + "\r\n"

        return data

    @classmethod
    def _getPropertyByKey(cls, plpy, modelSetId) -> Dict[str, _Prop]:
        # Load in the ModelSet ID
        sql = (
            """
              SELECT id, key, name
              FROM pl_eventdb."EventDBProperty"
              where "modelSetId" = %s
              """
            % modelSetId
        )
        rows = plpy.execute(sql, 10000)

        if not len(rows):
            raise Exception("No properties exist with modelSetId %s" % modelSetId)

        propByKey = {}
        propById = {}
        for row in rows:
            prop = _Prop(row["name"])
            propByKey[row["key"]] = prop
            propById[row["id"]] = prop

        # Load in the Property Values

        sql = (
            """
              SELECT v."propertyId", v.name, v.value
              FROM pl_eventdb."EventDBPropertyValue" as v
                  JOIN pl_eventdb."EventDBProperty" as p on v."propertyId"=p.id
              where "modelSetId" = %s
              """
            % modelSetId
        )
        rows = plpy.execute(sql, 10000)

        for row in rows:
            prop = propById[row["propertyId"]]
            key = str(row["value"]).replace("null", "none").lower()
            prop.nameByValueMap[key] = row["name"]

        return propByKey
