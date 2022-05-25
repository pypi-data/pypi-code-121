"""Move SQL to script.txt file in Oracle Steps

Revision ID: 58b1656aac40
Revises: 16e34a42a9a1
Create Date: 2022-03-16 15:27:49.806832

"""
import json
from pathlib import Path

from attune_project_api import ObjectStorageContext
from attune_project_api._private.utils import makeStorageKey
from attune_project_api.items.step_tuples.step_sql_oracle_tuple import (
    StepSqlOracleTuple,
)
from attune_project_api.items.step_tuples.step_tuple import StepTuple

# revision identifiers, used by Alembic.
revision = "58b1656aac40"
down_revision = "16e34a42a9a1"
branch_labels = None
depends_on = None


def upgrade(storageContext: ObjectStorageContext):
    try:
        stepsTree = storageContext._getTree(Path("steps"))
    except FileNotFoundError:
        return

    BaseClass = StepTuple

    for itemTree in stepsTree:
        itemPath = Path(
            f"{BaseClass.storageGroup.value}/{makeStorageKey(itemTree.name)}"
        )

        try:
            data = storageContext._readFile((itemPath / "metadata.json"))
            metadataStr = data.decode()
            metadata = json.loads(metadataStr)
        except FileNotFoundError:
            continue

        if metadata["type"] != StepSqlOracleTuple.tupleType():
            continue

        sql = metadata.pop("sql", "")

        # Rewrite the metadata.json
        storageContext._writeFile(
            (itemPath / "metadata.json").as_posix(),
            json.dumps(
                metadata,
                indent=4,
                sort_keys=True,
                separators=(", ", ": "),
            ).encode(),
        )

        # Rewrite the script.txt
        storageContext._writeFile(
            (itemPath / "script.txt").as_posix(), sql.encode()
        )

    storageContext.commit("Moved SQL to script.txt")


def downgrade(storageContext: ObjectStorageContext):
    pass
