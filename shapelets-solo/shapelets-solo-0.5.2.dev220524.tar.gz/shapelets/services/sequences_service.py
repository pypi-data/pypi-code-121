# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import base64
import datetime
from enum import Enum
import numpy as np
import pandas as pd
import pyarrow as pa

from shapelets.model import (
    Collection,
    Sequence,
    SequenceDensityEnum,
    SequenceBaseTypeEnum,
    SequenceColumnInfoEnum,
    SequenceColumnDataTypeEnum,
    SequenceRegularityEnum
)
from shapelets.services.base_service import BaseService
from shapelets.services.collections_service import (
    Endpoint as CollectionsEndpoint,
    create_axis
)


class Endpoint(Enum):
    SEQUENCES = "api/sequences"
    SEQUENCE_BY_ID = f"{SEQUENCES}/###sequence_id###"
    SEQUENCE_DATA_BY_ID = f"{SEQUENCE_BY_ID}/data"

    def replace(self, sequence_id: str):
        template = str(self.value)
        return template.replace("###sequence_id###", sequence_id)


class SequencesService(BaseService):

    def get_sequence(self, sequence_id: str) -> Sequence:
        sequence = self.request_get(Endpoint.SEQUENCE_BY_ID.replace(sequence_id))
        return Sequence.from_dict(sequence)

    def create_sequence(self,
                        dataframe: pd.DataFrame,
                        name: str,
                        starts: np.datetime64,
                        every: int,
                        collection: Collection) -> Sequence:
        length = len(dataframe.index)
        density = SequenceDensityEnum.DENSE.value
        regularity = SequenceRegularityEnum.REGULAR.value
        axis = create_axis(dataframe, starts, every)
        base_type = SequenceBaseTypeEnum.NUMERICAL.value
        # column_info = {
        #     "type": SequenceColumnInfoEnum.UNIDIMENSIONAL.value,
        #     "columns": [{"name": "column1", "dataType": SequenceColumnDataTypeEnum.NUMERICAL.value}]
        # }
        values_info = {
            "type": SequenceColumnInfoEnum.UNIDIMENSIONAL.value,
            "columns": [
                {
                    "name": str(column_name),
                    "dataType": SequenceColumnDataTypeEnum.NUMERICAL.value
                } for column_name in dataframe.columns.values
            ]
        }
        content = self.request_post(
            Endpoint.SEQUENCES.value,
            {
                "name": name,
                "length": length,
                "density": density,
                "regularity": regularity,
                "axis": axis.to_dict(),
                "baseType": base_type,
                # "axisColumnInfo": column_info,
                "valuesColumnInfo": values_info,
                "arrowFile": _to_utf64_arrow_buffer(dataframe),
                "units": ""
            }
        )
        seq_id = content["id"]
        self.request_put(
            CollectionsEndpoint.COLLECTION_SEQUENCES.replace(collection.collection_id),
            {
                "sequenceIds": [
                    {"id": seq_id}
                ]
            }
        )
        return self.get_sequence(seq_id)

    def update_sequence(self, sequence: Sequence, dataframe: pd.DataFrame) -> None:
        self.request_put(
            Endpoint.SEQUENCE_BY_ID.replace(sequence.sequence_id),
            {
                "arrowFile": _to_utf64_arrow_buffer(dataframe)
            })

    def get_sequence_data(self, sequence) -> pd.Series:
        response = self.request_get(
            Endpoint.SEQUENCE_DATA_BY_ID.replace(sequence.sequence_id),
            raw_content=True)
        # response is a pyarrow
        data = pa.ipc.RecordBatchFileReader(response).read_pandas()
        # in the next line, axis.every does not necessarily need to be 1000 (millis)
        # it is whatever the user wants it to be, thus the following line might or
        # might not work... I suggest a more restrictive API for timeseries, with
        # minimum resolution of 1 milli second. Created clickup:
        # https://app.clickup.com/t/fpzdty
        if sequence.axis.every:
            # Dense Sequences
            freq = pd.tseries.offsets.DateOffset(microseconds=sequence.axis.every * 1e3)
            starts = datetime.datetime.utcfromtimestamp(sequence.axis.starts / 1e3).strftime('%c')
            index = pd.date_range(start=starts, periods=sequence.length, freq=freq)
        else:
            # Sparse or Irregular Sequences
            freq = data.iloc[:, 0]
            freq = freq.astype("int64")
            data = data.drop(columns=[data.columns[0]])
            index = pd.to_datetime(freq,unit='ms')

        return data.set_index(index).iloc[:, 0]


def _to_utf64_arrow_buffer(dataframe: pd.DataFrame) -> str:
    table = pa.Table.from_pandas(dataframe, preserve_index=False)
    sink = pa.BufferOutputStream()
    with pa.ipc.RecordBatchFileWriter(sink, table.schema) as writer:
        writer.write(table)
    buffer = sink.getvalue()
    return base64.b64encode(buffer).decode("utf-8")
