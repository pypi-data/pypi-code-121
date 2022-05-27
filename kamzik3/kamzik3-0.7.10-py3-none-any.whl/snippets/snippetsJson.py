import json
import time
from base64 import b64encode, b64decode

import numpy as np

import kamzik3
from kamzik3.devices.device import Device
from kamzik3 import units


class JsonKamzikEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, units.Quantity):
            return {"pint-unit-quantity": o.to_tuple()}
        elif isinstance(o, np.ndarray):
            return {"numpy-array": o.tolist(), "dtype": o.dtype.name, "shape": o.shape}
        elif isinstance(o, bytes):
            return {"bytes": b64encode(o).decode()}
        elif isinstance(o, Device):
            return {"kamzik3-device": o.device_id}
        return json.JSONEncoder.default(self, o)


def JsonKamzikHook(dct):
    if "pint-unit-quantity" in dct:
        return units.Quantity.from_tuple(dct["pint-unit-quantity"])
    elif "numpy-array" in dct:
        return np.asarray(dct.get("numpy-array"), dtype=dct.get("dtype"))
    elif "bytes" in dct:
        return b64decode(dct.get("bytes"))
    elif "kamzik3-device" in dct:
        return kamzik3.session.get_device(dct.get("kamzik3-device"))
    return dct
