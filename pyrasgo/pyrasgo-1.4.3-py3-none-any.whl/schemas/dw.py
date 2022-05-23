from typing import List, Optional

from pydantic import BaseModel


class SimpleColumn(BaseModel):
    columnName: str
    dataType: str


class SimpleTable(BaseModel):
    tableName: str
    databaseName: str
    schemaName: str
    fqtn: Optional[str]


class SimpleTableWithColumns(SimpleTable):
    columns: Optional[List[SimpleColumn]]
