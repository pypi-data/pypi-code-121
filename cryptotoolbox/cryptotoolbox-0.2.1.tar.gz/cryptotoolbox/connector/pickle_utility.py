import pickle
import os.path
import pandas as pd

n_bytes = 2**31
max_bytes = 2**31 - 1


## write bigger than 4 gigas pickle
def write_pickle(data=None,file_path=None):
    bytes_out = pickle.dumps(data)
    with open(file_path, 'wb') as f_out:
        for idx in range(0, len(bytes_out), max_bytes):
            f_out.write(bytes_out[idx:idx+max_bytes])

## read bigger than 4 gigas pickle
def read_pickle(file_path=None):
    bytes_in = bytearray(0)
    input_size = os.path.getsize(file_path)
    with open(file_path, 'rb') as f_in:
        for _ in range(0, input_size, max_bytes):
            bytes_in += f_in.read(max_bytes)
    data = pickle.loads(bytes_in)
    return data

def common_merge_index(*args):
    assert len(args) >= 2
    X = args[0]
    for i in range(1,len(args)):
        if args[i] is not None:
            X = pd.merge(left=X, right=args[i], how='inner', left_index=True, right_index=True)
    return X
