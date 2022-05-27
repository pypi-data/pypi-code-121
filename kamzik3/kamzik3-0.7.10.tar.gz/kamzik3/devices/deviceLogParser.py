import time

import numpy as np
import pandas

from kamzik3.constants import STATUS_CONFIGURED
from kamzik3.devices.device import Device
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceLogParser(Device):
    def __init__(self, device_id=None, config=None):
        Device.__init__(self, device_id, config)
        self.connect()

    def _init_attributes(self):
        Device._init_attributes(self)

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        _finish_configuration()

    @expose_method({"path": "Path to the log file", "format": "Name of the format"})
    def parse(self, path, format, filter=None):
        if format == "mag_log":
            dtypes = {}
            header_rows = []
            row = 0
            data_frames = []
            # do we really want a system-dependent encoding here?
            # pylint: disable=unspecified-encoding
            with open(path, "r") as f:
                for row, line in enumerate(f):
                    if line[0] == "#":
                        header_rows.append((row, line))

            for index, (header_row, header) in enumerate(header_rows):
                try:
                    start_row, end_row = header_row, header_rows[index + 1][0] - 1
                except IndexError:
                    start_row, end_row = header_row, row

                nrows = end_row - start_row
                if nrows <= 0:
                    continue

                headers, _types = [], []
                raw_headers = header.strip().split(";")
                for raw_header in raw_headers:
                    header, meta = raw_header.split(" (")
                    dtype, unit = meta.split(",")
                    try:
                        dtype = np.dtype(dtype).name
                        if dtype in ("int32", "int64", "bool"):
                            dtype = "float64"
                    except TypeError:
                        dtype = "str"

                    header_name = "{} ({})".format(header, unit[:-1])
                    headers.append(header_name)
                    dtypes[header_name] = dtype
                df = pandas.read_csv(
                    path,
                    sep=";",
                    low_memory=True,
                    skiprows=start_row,
                    nrows=nrows,
                    header=0,
                    names=headers,
                    dtype=dtypes,
                    error_bad_lines=False,
                )
                data_frames.append(df)

        data_frame = pandas.concat(data_frames, copy=True)

        if filter is not None:
            for filter_column, filter_range in filter.items():
                data_frame = data_frame[
                    (data_frame[filter_column] >= float(filter_range[0]))
                    & (data_frame[filter_column] <= float(filter_range[1]))
                ]

        return data_frame
