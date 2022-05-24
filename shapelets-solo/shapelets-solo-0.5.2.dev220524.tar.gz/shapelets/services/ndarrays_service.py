# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import base64
from enum import Enum
import numpy as np
import pyarrow as pa
from pyarrow import RecordBatchFileReader

from shapelets.model import (
    NDArray
)
from shapelets.services import ShapeletsNDArrayException
from shapelets.services.base_service import BaseService


class Endpoint(Enum):
    NDARRAYS = "api/ndarrays"
    NDARRAY_BY_ID = f"{NDARRAYS}/###nd_array_id###"
    NDARRAY_DATA_BY_ID = f"{NDARRAY_BY_ID}/data"

    def replace(self, nd_array_id: str):
        template = str(self.value)
        return template.replace("###nd_array_id###", nd_array_id)


class NDArraysService(BaseService):

    def get_nd_array(self, nd_array_id: str) -> NDArray:
        nd_array = self.request_get(Endpoint.NDARRAY_BY_ID.replace(nd_array_id))
        return NDArray.from_dict(nd_array)

    def create_nd_array(self,
                        array: np.ndarray,
                        name: str = None,
                        description: str = None) -> NDArray:
        dtype = array.dtype
        dims = array.shape
        content = self.request_post(
            Endpoint.NDARRAYS.value,
            {
                "name": name if name else "",
                "description": description if description else "",
                "dtype": str(dtype),
                "dims": dims,
                "arrowData": _to_utf64_arrow_buffer(array)
            }
        )
        return NDArray.from_dict(content)

    def get_nd_array_data(self, nd_array: NDArray) -> np.ndarray:
        response = self.request_get(
            Endpoint.NDARRAY_DATA_BY_ID.replace(nd_array.nd_array_id),
            raw_content=True)
        reader = pa.ipc.open_file(response)
        return _to_numpy_array(reader).reshape(nd_array.dims)

    def update_nd_array(self, nd_array: NDArray, array: np.ndarray = None) -> NDArray:
        if array is not None:
            if not nd_array.dims == array.shape:
                raise ShapeletsNDArrayException("Dimensions not matching")
            if not nd_array.dtype == array.dtype:
                raise ShapeletsNDArrayException("Types not matching")
        content = self.request_put(
            Endpoint.NDARRAY_BY_ID.replace(nd_array.nd_array_id),
            {
                "name": nd_array.name,
                "description": nd_array.description,
                "dtype": str(nd_array.dtype),
                "dims": nd_array.dims,
                "arrowData": _to_utf64_arrow_buffer(array) if array is not None else None
            }
        )
        return NDArray.from_dict(content)

    def delete_nd_array(self, nd_array: NDArray) -> bool:
        return self.request_delete(Endpoint.NDARRAY_BY_ID.replace(nd_array.nd_array_id))


def _to_utf64_arrow_buffer(array: np.ndarray) -> str:
    parray = pa.array(array.flatten())
    batch = pa.record_batch([parray], names=["values"])
    sink = pa.BufferOutputStream()
    with pa.ipc.RecordBatchFileWriter(sink, batch.schema) as writer:
        writer.write(batch)
    buffer = sink.getvalue()
    return base64.b64encode(buffer).decode("utf-8")


def _to_numpy_array(reader: RecordBatchFileReader) -> np.ndarray:
    result = None
    for i in range(reader.num_record_batches):
        if i == 0:
            values = reader.get_batch(i)["values"]
            if values.type == pa.bool_():
                result = values.to_numpy(zero_copy_only=False)
            else:
                result = values.to_numpy()
        else:
            partial_array = reader.get_batch(i)["values"].to_numpy()
            result = np.concatenate((result, partial_array))
    return result
