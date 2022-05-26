import dataclasses
import pickle
from pathlib import Path

import numpy as np


@dataclasses.dataclass
class MatrixObject(object):
    def to_pickle(self, path_pickle: Path):
        dict_obj = dataclasses.asdict(self)
        with path_pickle.open('wb') as f:
            pickle.dump(dict_obj, f)

    def to_npz(self, path_npz: Path):
        dict_obj = dataclasses.asdict(self)
        np.savez(path_npz, **dict_obj)
