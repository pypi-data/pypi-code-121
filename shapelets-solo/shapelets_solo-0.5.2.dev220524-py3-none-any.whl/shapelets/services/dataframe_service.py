# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import base64
from enum import Enum
import pandas as pd
import pyarrow as pa

from shapelets.model.dataframe import Dataframe
from shapelets.services import ShapeletsNDArrayException
from shapelets.services.base_service import BaseService


class Endpoint(Enum):
    DATAFRAMES = "api/dataframes"
    DATAFRAME_BY_ID = f"{DATAFRAMES}/###dataframe_id###"
    DATAFRAME_DATA_BY_ID = f"{DATAFRAME_BY_ID}/data"

    def replace(self, dataframe_id):
        template = str(self.value)
        if isinstance(dataframe_id, dict):
            dataframe_id = dataframe_id.get("id")
        return template.replace("###dataframe_id###", dataframe_id)


class DataframeService(BaseService):

    def get_dataframe(self, dataframe_id: str) -> Dataframe:
        dataframe = self.request_get(Endpoint.DATAFRAME_BY_ID.replace(dataframe_id))
        return Dataframe.from_dict(dataframe)

    def create_dataframe(self,
                         dataframe: pd.DataFrame,
                         name: str = None,
                         description: str = None) -> Dataframe:
        n_cols = dataframe.shape[1]
        n_rows = dataframe.shape[0]
        col_names = [str(x) for x in dataframe.columns]
        col_types = [str(x) for x in dataframe.dtypes]
        has_index = True if len(dataframe.index) > 0 else False
        index_type = str(dataframe.index.dtype) if len(dataframe.index) > 0 else None
        content = self.request_post(
            Endpoint.DATAFRAMES.value,
            {
                "name": name if name else "",
                "description": description if description else "",
                "nCols": n_cols,
                "nRows": n_rows,
                "colNames": col_names,
                "colTypes": col_types,
                "hasIndex": has_index,
                "indexType": index_type,
                "arrowData": _to_utf64_arrow_buffer(dataframe)
            }
        )
        return Dataframe.from_dict(content)

    def get_dataframe_data(self, dataframe: Dataframe) -> pd.DataFrame:
        response = self.request_get(
            Endpoint.DATAFRAME_DATA_BY_ID.replace(dataframe.dataframe_id),
            raw_content=True)
        data = pa.ipc.RecordBatchFileReader(response).read_pandas()
        return data

    def update_dataframe(self, dataframe: Dataframe, new_data: pd.DataFrame = None) -> Dataframe:
        if new_data is not None:
            n_cols = new_data.shape[1]
            n_rows = new_data.shape[0]
            col_names = [str(x) for x in new_data.columns]
            col_types = [str(x) for x in new_data.dtypes]
            has_index = True if len(new_data.index) > 0 else False
            index_type = str(new_data.index.dtype) if len(new_data.index) > 0 else None
        else:
            n_cols = dataframe.n_cols
            n_rows = dataframe.n_rows
            col_names = dataframe.col_names
            col_types = dataframe.col_types
            has_index = dataframe.has_index
            index_type = dataframe.index_type
        content = self.request_put(
            Endpoint.DATAFRAME_BY_ID.replace(dataframe.dataframe_id),
            {
                "name": dataframe.name,
                "description": dataframe.description,
                "nCols": n_cols,
                "nRows": n_rows,
                "colNames": col_names,
                "colTypes": col_types,
                "hasIndex": has_index,
                "indexType": index_type,
                "arrowData": _to_utf64_arrow_buffer(new_data) if new_data is not None else None
            }
        )
        return Dataframe.from_dict(content)

    def delete_dataframe(self, dataframe: Dataframe) -> bool:
        return self.request_delete(Endpoint.DATAFRAME_BY_ID.replace(dataframe.dataframe_id))


def _to_utf64_arrow_buffer(dataframe: pd.DataFrame) -> str:
    table = pa.Table.from_pandas(dataframe, preserve_index=True)
    sink = pa.BufferOutputStream()
    with pa.ipc.RecordBatchFileWriter(sink, table.schema) as writer:
        writer.write(table)
    buffer = sink.getvalue()
    return base64.b64encode(buffer).decode("utf-8")
