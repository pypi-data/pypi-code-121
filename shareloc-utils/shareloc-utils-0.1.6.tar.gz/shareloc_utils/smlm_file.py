#!/usr/bin/env python

"""shareloc_batch_download.py: Download datasets from shareloc.xyz website.
Author: Wei OUYANG
License: MIT
"""

import zipfile
import json
import struct
import io
import logging
import numpy as np

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

dtype2struct = {"uint8": "B", "uint32": "I", "float64": "d", "float32": "f"}
dtype2length = {"uint8": 1, "uint32": 4, "float64": 8, "float32": 4}


def read_smlm_file(file_path):
    zf = zipfile.ZipFile(file_path, "r")
    file_names = zf.namelist()
    if "manifest.json" in file_names:
        manifest = json.loads(zf.read("manifest.json"))
        assert manifest["format_version"] == "0.2"
        for file_info in manifest["files"]:
            if file_info["type"] == "table":
                logger.info("loading table...")
                format_key = file_info["format"]
                file_format = manifest["formats"][format_key]
                if file_format["mode"] == "binary":
                    try:
                        table_file = zf.read(file_info["name"])
                        logger.info(file_info["name"])
                    except KeyError:
                        logger.error(
                            "ERROR: Did not find %s in zip file", file_info["name"]
                        )
                        continue
                    else:
                        logger.info("loading table file: %s bytes", len(table_file))
                        logger.info("headers: %s", file_format["headers"])
                        headers = file_format["headers"]
                        dtype = file_format["dtype"]
                        shape = file_format["shape"]
                        cols = len(headers)
                        rows = file_info["rows"]
                        logger.info("rows: %s, columns: %s", rows, cols)
                        assert len(headers) == len(dtype) == len(shape)
                        rowLen = 0
                        for i, h in enumerate(file_format["headers"]):
                            rowLen += dtype2length[dtype[i]]

                        data = {}
                        byteOffset = 0
                        try:
                            import numpy as np

                            for i, h in enumerate(file_format["headers"]):
                                data[h] = np.ndarray(
                                    (rows,),
                                    buffer=table_file,
                                    dtype=dtype[i],
                                    offset=byteOffset,
                                    order="C",
                                    strides=(rowLen,),
                                )
                                byteOffset += dtype2length[dtype[i]]
                        except ImportError:
                            logger.warning(
                                "Failed to import numpy, performance will drop dramatically. Please install numpy for the best performance."
                            )
                            st = ""
                            for i, h in enumerate(file_format["headers"]):
                                st += str(shape[i]) + dtype2struct[dtype[i]]

                            unpack = struct.Struct(st).unpack
                            data = {h: [] for h in headers}
                            for i in range(0, len(table_file), rowLen):
                                unpacked_data = unpack(table_file[i : i + rowLen])
                                for j, h in enumerate(headers):
                                    data[h].append(unpacked_data[j])
                            data = {h: np.array(data[h]) for i, h in enumerate(headers)}
                        file_info["min"] = [data[h].min() for h in headers]
                        file_info["max"] = [data[h].max() for h in headers]
                        file_info["avg"] = [data[h].mean() for h in headers]
                        file_info["data"] = data
                        file_info["headers"] = headers
                        file_info["dtype"] = dtype
                        file_info["shape"] = shape
                        file_info["rows"] = rows
                        file_info["cols"] = cols
                        logger.info("table file loaded: %s", file_info["name"])
                else:
                    raise Exception(
                        "format mode {} not supported yet".format(file_format["mode"])
                    )
            elif file_info["type"] == "image":
                if file_format["mode"] == "binary":
                    try:
                        image_file = zf.read(file_info["name"])
                        logger.info("image file loaded: %s", file_info["name"])
                    except KeyError:
                        logger.error(
                            "ERROR: Did not find %s in zip file", file_info["name"]
                        )
                        continue
                    else:
                        from PIL import Image

                        image = Image.open(io.BytesIO(image_file))
                        file_info["image"] = image
                        logger.info("image file loaded: %s", file_info["name"])

            else:
                logger.info("ignore file with type: %s", file_info["type"])
    else:
        raise Exception("invalid file: no manifest.json found in the smlm file")
    return manifest


def plot_histogram(
    data,
    value_range=None,
    xy_range=None,
    pixel_size=20,
    sigma=None,
    target_size=None,
):
    x = data["x"][:]
    y = data["y"][:]
    if xy_range:
        xmin, xmax = xy_range[0]
        ymin, ymax = xy_range[1]
    else:
        xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()
    xedges = np.arange(xmin, xmax, pixel_size)
    yedges = np.arange(ymin, ymax, pixel_size)
    H, _, _ = np.histogram2d(y, x, bins=(yedges, xedges))
    if target_size is not None:
        if H.shape[0] < target_size[0] or H.shape[1] < target_size[1]:
            H = np.pad(
                H,
                ((0, target_size[0] - H.shape[0]), (0, target_size[1] - H.shape[1])),
                mode="constant",
                constant_values=0,
            )

    if value_range:
        H = H.clip(value_range[0], value_range[1])
    if sigma:
        import scipy

        H = scipy.ndimage.filters.gaussian_filter(H, sigma=(sigma, sigma))
    return H


if __name__ == "__main__":
    from PIL import Image

    # Download a file from: https://shareloc.xyz/#/repository by clicking the `...` button of the file and click the name contains `.smlm`
    manifest = read_smlm_file("output/Microtubules of COS7 cells/linear-Sc/data.smlm")
    tables = manifest["files"]
    histogram = plot_histogram(tables[0]["data"], value_range=(0, 255))
    im = Image.fromarray(histogram.astype("uint16"))
    im.save("output.png")
