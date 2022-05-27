from typing import Optional, List

from pydantic import BaseModel, Field


class DataColumn(BaseModel):
    """
    Contract to nest in a DataTable
    """

    id: int
    column_name: str = Field(alias='columnName')
    data_type: str = Field(alias='dataType')

    class Config:
        allow_population_by_field_name = True


class DataTable(BaseModel):
    """
    Contract to nest in a Dataset
    """

    id: int
    table_name: str = Field(alias='tableName')
    database_name: str = Field(alias='databaseName')
    schema_name: str = Field(alias='schemaName')
    fqtn: Optional[str]
    table_type: str = Field(alias='tableType')

    class Config:
        allow_population_by_field_name = True


class DataTableWithColumns(DataTable):
    """
    Contract to nest in an OperationSet
    """

    columns: Optional[List[DataColumn]]
