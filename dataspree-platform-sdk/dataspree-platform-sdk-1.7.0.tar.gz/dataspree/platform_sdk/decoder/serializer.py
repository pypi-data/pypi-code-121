import time
import logging
import numpy as np
from typing import Any, Dict, Tuple, Optional, List, Iterator

logger = logging.getLogger(__name__)


def load_pcd(data: bytes, width: Optional[int] = None, height: Optional[int] = None) \
        -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    :brief: Load the entire content of the CPD file accessible via `filename` to the `item`.
            Retain types and dimensions indicated in PCD file.
    """
    times: List[Tuple[str, float]] = [('', time.time())]

    # Read header
    is_binary: bool
    property_dict: Dict[str, List[str]] = dict()
    while True:
        line, data = read_line(data)
        if len(line) == 0:
            raise ValueError(f'Corrupted PCD data. The file does not contain a header.')

        current_line: List[str] = line.decode('utf-8')[:-1].split(' ')
        if len(current_line):
            property_dict[current_line[0]] = current_line[1:]

            if current_line[0] == 'DATA':
                is_binary = current_line[1] == 'binary'
                break

    # Acquire relevant information.
    def get_scalar(target_type: type, key_in_property_dict: str, default: Optional[Any] = None) -> Any:
        # return scalar value from `property_dict`, check that it is a scalar and cast to the desired type.
        default = None if default is None else [default]
        pd: List[str] = property_dict.get(key_in_property_dict, default)
        if len(pd) != 1:
            raise ValueError('Error decoding Data!')
        return target_type(pd[0])

    width: int = get_scalar(int, 'WIDTH', width)
    height: int = get_scalar(int, 'HEIGHT', height)
    points: int = get_scalar(int, 'POINTS', width * height)
    viewpoint: List[str] = property_dict.get('VIEWPOINT', None)
    types: List[str] = property_dict['TYPE']
    sizes: List[int] = list(map(int, property_dict['SIZE']))
    fields: List[str] = property_dict['FIELDS']
    dtypes: List[np.dtype] = [np.dtype(f'{t.lower()}{sizes[i]}') for i, t in enumerate(types)]
    if width * height != points:
        raise ValueError('The number of points in the PCD file does not match width * height. '
                         'Error deconding Point Cloud.')
    times.append(('read header       ', time.time()))

    return read_point_cloud_data(data, is_binary=is_binary, width=width, height=height, sizes=sizes, dtypes=dtypes,
                                 fields=fields, times=times), dict(viewpoint=viewpoint)


def load_ply(data: bytes, width: int, height: int) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    :brief: Load the entire content of the PLY file accessible via `filename` to the `item`.
            Retain types and dimensions indicated in PCD file.
    """
    times: List[Tuple[str, float]] = [('', time.time())]

    # Read header
    dtypes: List[np.dtype] = []
    sizes: List[int] = []
    fields: List[str] = []
    is_binary: bool = False

    while True:
        line, data = read_line(data)
        current_line: List[str] = line.decode('utf-8')[:-1].split(' ')
        if len(current_line):
            if current_line[0] == 'property':
                dtype_str, lookup_name = current_line[1:]
                field_dtype: np.dtype = np.dtype(dtype_str)

                fields.append(lookup_name)
                dtypes.append(field_dtype)
                sizes.append(field_dtype.itemsize)

            elif current_line[0] == 'format':
                is_binary = current_line[1] != 'ascii'

            elif current_line[0] == 'end_header':
                break
    times.append(('read header       ', time.time()))

    # Read data payload
    return read_point_cloud_data(data, is_binary=is_binary, width=width, height=height, sizes=sizes, dtypes=dtypes,
                                 fields=fields, times=times), dict()


def read_point_cloud_data(data: bytes, is_binary: bool, width: int, height, sizes: List[int], dtypes: List[np.dtype],
                          fields: List[str], times) -> np.ndarray:
    npa: np.ndarray

    if is_binary:
        required_bytes: int = width * height * sum(sizes)

        # Read data payload bytes
        if len(data) < required_bytes:
            missing_bytes: int = required_bytes - len(data)
            logger.warning(f'Reading corrupted Point Cloud File! Padding {missing_bytes} bytes with zeros.')
            data += bytes([0, ] * missing_bytes)

        # Compose structured numpy array from arrays and target dtypes.
        npa = np.frombuffer(data, dtype=[(fields[i], dt) for i, dt in enumerate(dtypes)])

    else:
        lines = map(bytes.strip, read_lines(data))

        # lines = map(lambda a: a.decode('ASCII'), map(bytes.strip, file_handle.readlines())) # slows down proc.
        # npa = np.genfromtxt(lines, delimiter=' ', dtype=[(str(i), dt) for i, dt in enumerate(dtypes)]) # slow AF

        # Compose structured numpy array from arrays and target dtypes.
        npa = np.empty((height * width), dtype=[(fields[i], dt) for i, dt in enumerate(dtypes)])

        for i, line in enumerate(lines):
            npa[fields][i] = tuple(line.split(b' '))
        times.append(('generated array ', time.time()))

        missing_values: int = (width * height) - i
        if missing_values > 0:
            logger.warning(f'Reading corrupted Point Cloud File! Write {missing_values} values with zeros')
            npa[fields][i:] = 0

        missing_values: int = (width * height) - npa.shape[0]
        if missing_values > 0:
            shape = npa.shape
            npa = np.pad(npa, (0, missing_values), mode='constant', constant_values=0)
            logger.warning(f'Reading corrupted Point Cloud File! Padded {missing_values} values with zeros values '
                           f'extending {shape} to {npa.shape}.')

    npa = np.nan_to_num(npa, copy=False).reshape((height, width))
    times.append(('read   np.array   ', time.time()))

    # logger.debug('    '.join((f'{i + 1}/{len(times) - 1} {z} {(v2 - v1):2f}' for i, ((_, v1), (z, v2))
    #                          in enumerate(zip(times[:-1], times[1:])))) + f' total: {times[-1][1] - times[0][1]}')
    return npa


def read_line(buffer: bytes, size: Optional[int] = None) -> Tuple[bytes, bytes]:
    pos: int = buffer.find(b"\n") + 1

    if size is not None:
        pos = min(size, pos)

    return buffer[:pos], buffer[pos:]


def read_lines(buffer: bytes, size: Optional[int] = None) -> Iterator[bytes]:
    while buffer:
        line, buffer = read_line(buffer)
        yield line
