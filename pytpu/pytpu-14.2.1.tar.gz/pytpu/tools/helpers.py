import copy
import json
import logging
import os
import re
import shutil
import tempfile
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from zipfile import ZipFile

import numpy as np
from tpu_tlm_is.base import TpuParameters
from tpu_tlm_is.base import get_hw_params
from tpu_tlm_is.base.number_types import STR_TO_NUMPY


__all__ = [
    'get_tpu_devices',
    'get_tpu_parameters',
    'STR_TO_BYTES',
    'STR_TO_DTYPE',
    'to_raw',
    'to_nhwc_program',
]

LOGGER = logging.getLogger(__name__)


def get_tpu_devices() -> List[str]:
    return [os.path.join('/dev', f) for f in os.listdir('/dev') if re.match(r'tpu.', f) and len(f) == 4]


def get_tpu_parameters(hw_par: Dict[str, Any]) -> TpuParameters:
    if hw_par['cache_word_len'] == 128 and hw_par['ddr_word_len'] == 32:
        return get_hw_params('128x128').tpu_parameters
    if hw_par['cache_word_len'] == 64 and hw_par['ddr_word_len'] == 16:
        return get_hw_params('64x64').tpu_parameters
    if hw_par['cache_word_len'] == 64 and hw_par['ddr_word_len'] == 64:
        return get_hw_params('64x64_fpga').tpu_parameters

    raise NotImplementedError('Translation of such platform does not supported!')


def _to_raw_old(io_: Dict[str, Any], name: str) -> Dict[str, Any]:
    LOGGER.debug(f'IO description: {io_}')

    size = io_['size']
    io_out = {
        'address': io_['address'],
        'size': size,
        'user_shape': [1, size, ],
        'user_order': ['N', 'C', ],
        'user_dtype': 'int8',
        'tpu_shape': [1, size, ],
        'tpu_order': ['N', 'C', ],
        'tpu_dtype': 'int8',
        'padding': [[0, 0], [0, 0]],
        'scales': [1.0, ],
        'anchor': io_.get('anchor', name),
    }
    LOGGER.debug(f'RAW IO description: {io_out}')

    return io_out


def to_raw(metadata: Dict[str, Any]) -> Dict[str, Any]:
    raw_metadata = copy.copy(metadata)
    for idx, region in raw_metadata['inputs'].items():
        for name, _ in region.items():
            raw_metadata['inputs'][idx][name] = _to_raw_old(metadata['inputs'][idx][name], name)

    for idx, region in raw_metadata['outputs'].items():
        for name, _ in region.items():
            raw_metadata['outputs'][idx][name] = _to_raw_old(metadata['outputs'][idx][name], name)

    return raw_metadata


def _to_nhwc_descriptor(io_: Dict[str, Any], name: str) -> Dict[str, Any]:
    LOGGER.debug(f'IO description: {io_}')

    assert io_['user_order'][-1] == 'C'

    user_shape = io_['user_shape']
    user_order = io_['user_order']
    tpu_order = io_['tpu_order']
    tpu_order_replace = [user_order[-1], *user_order[1:-1], user_order[0]]
    tpu_shape = io_['tpu_shape']

    # print(tpu_shape)

    channels = tpu_shape[tpu_order.index('C')] * tpu_shape[tpu_order.index('B')]
    batch = tpu_shape[tpu_order.index('N')]
    tpu_shape_replace = [batch, *tpu_shape[1:-2], channels]

    # print(tpu_shape_replace)

    size = io_['size']
    io_out = {
        'address': io_['address'],
        'size': size,
        'user_shape': user_shape,
        'user_order': user_order,
        'user_dtype': io_['user_dtype'],
        'tpu_shape': tpu_shape_replace,
        'tpu_order': tpu_order_replace,
        'tpu_dtype': io_['tpu_dtype'],
        'padding': io_['padding'],
        'scales': io_['scales'],
        'anchor': io_.get('anchor', name),
    }
    LOGGER.debug(f'RAW IO description: {io_out}')

    return io_out


def to_nhwc_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    nhwc_metadata = copy.copy(metadata)
    for idx, region in nhwc_metadata['inputs'].items():
        for name, _ in region.items():
            nhwc_metadata['inputs'][idx][name] = _to_nhwc_descriptor(metadata['inputs'][idx][name], name)

    for idx, region in nhwc_metadata['outputs'].items():
        for name, _ in region.items():
            nhwc_metadata['outputs'][idx][name] = _to_nhwc_descriptor(metadata['outputs'][idx][name], name)

    return nhwc_metadata


def to_nhwc_program(source_path: str, store_path: str) -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        with ZipFile(source_path, 'r') as zip_obj:
            zip_obj.extractall(tempdir)

        with open(os.path.join(tempdir, 'metadata.json'), 'r') as metadata_file:
            metadata = json.load(metadata_file)

        with open(os.path.join(tempdir, 'metadata.json'), 'w') as metadata_file:
            nhwc_metadata = to_nhwc_metadata(metadata)
            json.dump(nhwc_metadata, metadata_file)

        with tempfile.NamedTemporaryFile() as temp_file:
            shutil.make_archive(temp_file.name, 'zip', tempdir)
            os.rename(temp_file.name + '.zip', store_path)
            LOGGER.debug(f'NHWC program saved to {store_path}')


def get_io_from_bin(program_path: str, io_paths: Optional[List[str]], io_type: str
                    ) -> Tuple[Dict[str, np.ndarray], List[str]]:
    with tempfile.TemporaryDirectory() as tempdir:
        with ZipFile(program_path, 'r') as zip_obj:
            zip_obj.extractall(tempdir)

        with open(os.path.join(tempdir, 'metadata.json'), 'r', encoding='utf8') as metadata_file:
            metadata = json.load(metadata_file)

    io_data = {}
    io_names = []
    idx = 0
    for _, region in metadata[io_type].items():
        for name, io_ in region.items():
            io_names.append(name)
            if io_paths is not None:
                with open(io_paths[idx], 'r') as io_file:
                    tmp = np.fromfile(io_file, STR_TO_NUMPY[io_.get('user_dtype', 'int8')])
                    io_data[name] = tmp.reshape(io_.get('user_shape', (1, -1)))
                    LOGGER.debug(f'Read {io_type} from files: {name}, {io_data[name].shape}, {io_data[name].dtype}')
            idx += 1

    return io_data, io_names


STR_TO_DTYPE = {
    'int8': np.int8,
    'float16': np.float16,
    'float32': np.float32,
}

STR_TO_BYTES = {
    'int8': 1,
    'float16': 2,
    'float32': 4,
}
