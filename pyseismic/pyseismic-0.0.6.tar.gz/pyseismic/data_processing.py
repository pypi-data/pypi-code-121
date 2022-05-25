import numpy as np


def read_bin(path: str, shape=None, dtype='float32'):
    if not shape:
        shape = get_shape(path)
    dat = np.fromfile(path, dtype=dtype)
    dat = np.reshape(dat, shape)
    return dat


def write_bin(data: np.ndarray, fn: str, add_shape=True, dtype='float32'):
    data = np.array(data, dtype=dtype)
    if fn.endswith('.bin'):
        fn = fn[:-4]
    if add_shape:
        data.tofile(f'{fn}_{"x".join(map(str, data.shape))}.bin')
    else:
        data.tofile(f'{fn}.bin')


def get_shape(fname: str):
    # 'xxx_5x3.bin' --> (5, 3)
    fname_len = len(fname)
    fname_inverse = fname[::-1]
    width_right = fname_len - 4
    depth_left = fname_len - fname_inverse.find('_')
    shape = tuple(map(int, fname[depth_left:width_right].split('x')))
    return shape
