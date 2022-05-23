import logging
from typing import Dict

from peek_plugin_eventdb._private.server.controller.EventDBImportEventsInPgTask import (
    EventDBImportEventsInPgTask,
)
from peek_plugin_eventdb.tuples import loadPublicTuples
from peek_plugin_eventdb.tuples.EventDBPropertyTuple import EventDBPropertyTuple
from vortex.Payload import Payload
from vortex.Tuple import TUPLE_TYPES_BY_NAME

logger = logging.getLogger(__name__)


class EventDBImportPropertiesInPgTask:
    """EventDB Import In PostGreSQL Tasks

    The methods in this class are run in the databases plpython extension.
    """

    @classmethod
    def replaceProperties(
        cls, plpy, modelSetKey: str, propertiesEncodedPayload: bytes
    ) -> None:

        if EventDBPropertyTuple.tupleName() not in TUPLE_TYPES_BY_NAME:
            loadPublicTuples()

        # Reconstruct the data
        properties = Payload().fromEncodedPayload(propertiesEncodedPayload).tuples
        if not properties:
            return

            # Get the model set id
        modelSetId = EventDBImportEventsInPgTask.getModelSetId(
            plpy, modelSetKey, createIfMissing=True
        )

        # Now insert the events
        cls._deleteProperties(plpy, modelSetId)

        # Now insert the events
        cls._insertProperties(plpy, modelSetId, properties)

        # Now insert the events
        cls._insertPropertieValues(plpy, modelSetId, properties)

    @classmethod
    def _insertProperties(cls, plpy, modelSetId: int, properties):

        plan = plpy.prepare(
            """INSERT INTO pl_eventdb."EventDBProperty"
                        ("modelSetId",
                          key, name, "order", comment,
                         "useForFilter", "useForDisplay", "useForPopup", "showFilterAs",
                         "displayByDefaultOnSummaryView",
                         "displayByDefaultOnDetailView")
                        VALUES ($1,
                                $2, $3, $4, $5,
                                $6, $7, $8, $9,
                                $10,
                                $11)""",
            [
                "integer",
                "text",
                "text",
                "integer",
                "text",
                "boolean",
                "boolean",
                "boolean",
                "integer",
                "boolean",
                "boolean",
            ],
        )
        for p in properties:
            plpy.execute(
                plan,
                [
                    modelSetId,
                    p.key,
                    p.name,
                    p.order,
                    p.comment,
                    p.useForFilter,
                    p.useForDisplay,
                    p.useForPopup,
                    p.showFilterAs,
                    p.displayByDefaultOnSummaryView,
                    p.displayByDefaultOnDetailView,
                ],
            )

    @classmethod
    def _insertPropertieValues(cls, plpy, modelSetId: int, properties):
        propIdByKey = cls._loadPropKeyById(plpy, modelSetId)

        plan = plpy.prepare(
            """INSERT INTO pl_eventdb."EventDBPropertyValue"
                            (name, "value", color, comment,
                            "propertyId")
                            VALUES ($1, $2, $3, $4,
                                    $5);""",
            ["text", "text", "text", "text", "integer"],
        )
        for p in properties:
            if p.values:
                for v in p.values:
                    plpy.execute(
                        plan, [v.name, v.value, v.color, v.comment, propIdByKey[p.key]]
                    )

    @classmethod
    def _loadPropKeyById(cls, plpy, modelSetId: int) -> Dict[str, int]:
        sql = """SELECT id, key
                 FROM pl_eventdb."EventDBProperty"
                 WHERE "modelSetId" = %s;"""
        sql %= modelSetId
        rows = plpy.execute(sql, 500)
        return {r["key"]: r["id"] for r in rows}

    @classmethod
    def _deleteProperties(cls, plpy, modelSetId: int):
        sql = """DELETE FROM pl_eventdb."EventDBProperty"
                 WHERE "modelSetId" = %s;"""
        sql %= modelSetId
        plpy.execute(sql)
