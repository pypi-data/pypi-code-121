import logging
import pathlib

from area_detector_handlers import HandlerBase
from fabio import cbfimage

logger = logging.getLogger(__name__)


class PilatusHandlerMX(HandlerBase):
    spec = "AD_PILATUS_MX"

    def __init__(self, fpath):
        # self._seq_id = seq_id
        self._fpath = pathlib.Path(f"{fpath}").absolute()
        if not self._fpath.is_file():
            raise RuntimeError(f"File {self._fpath} does not exist")

    def __call__(self):
        self._file = cbfimage.CbfImage(fname=self._fpath)
        return self._file.data

        # if data_key == "data":
        #     return self._file.BINARY_SECTION

        # elif data_key == "omega":
        #     return self._file.PilatusHeader["Start_angle"]

        # elif data_key == "bit_mask":
        #     ...
        #     # code to pull out bit mask
        #     raise NotImplementedError()

        # elif data_key in self._file.PilatusHeader:
        #     return self._file.PilatusHeader[data_key]

        # else:
        #     raise RuntimeError(f"Unknown key: {data_key}")
