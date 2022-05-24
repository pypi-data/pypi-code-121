"""
Functions for parsing a table of headers to extract information about the dataset
"""
from itertools import product
from collections import defaultdict, OrderedDict
from functools import cached_property

import numpy as np
from astropy.table import Table


class HeaderParser:
    """
    A class for parsing and inspecting a table of Headers.
    """
    def __init__(self, headers: Table):
        if not isinstance(headers, Table):
            raise TypeError("headers must be an astropy table.")

        dataset_axes = headers[0]["DNAXIS"]
        array_axes = headers[0]["DAAXES"]
        keys = [f"DINDEX{k}" for k in range(dataset_axes, array_axes, -1)][::-1]
        self.headers = headers
        self.headers.sort(keys)
        self.header = headers[0]

    @staticmethod
    def constant_columns(table, keys: list[str]):
        """
        Returns true if all columns given by keys have a constant value in table.
        """
        return all([np.allclose(table[0][k], table[k], rtol=1e-10) for k in keys])

    @staticmethod
    def compute_varying_axes_numbers(varying_axes):
        """
        Return the dataset pixel axes over which the spatial transform varies
        """
        if not varying_axes:
            return []
        if "pc" in varying_axes and "crval" in varying_axes:
            if varying_axes["pc"] != varying_axes["crval"]:
                raise ValueError(
                    "Both the pointing and the rotation vary over different"
                    " dimensions of the dataset. I don't know what to do here."
                )
            vaxes = varying_axes["crval"]
        elif "crval" in varying_axes:
            vaxes = varying_axes["crval"]
        elif "pc" in varying_axes:
            vaxes = varying_axes["pc"]
        else:
            raise ValueError("What is this varying_axes dict you have given me?!")
        return vaxes

    def slice_for_file_axes(self, *axes):
        """
        Slice the header array given an index for the file dimensions.
        """
        tslice = [0] * len(self.files_shape)
        for i in axes:
            tslice[i] = slice(None)
        return tuple(tslice)

    def slice_for_dataset_array_axes(self, *axes, indexing="python"):
        """
        Slice the header array based on dataset indicies.

        Parameters
        ----------
        *axes
            Axes numbers for the dataset
        indexing : {"fits", "python"}
            If ``indexing=="python"`` then the input is assumed to be the
            number of the dataset axes counted from zero. If
            ``indexing=="fits"`` then it is assumed to count from one.
        """
        file_axes = np.array(axes).flatten() - self.header["DAAXES"]
        # If the input is fits then we have to subtract one.
        if indexing == "fits":
            file_axes -= 1
        if any(file_axes < 0) or any(file_axes > len(self.files_shape)):
            raise ValueError("Some or all of the axes are out of bounds for the files dimensions.")
        return self.slice_for_file_axes(*file_axes)

    @property
    def files_shape(self):
        """
        The shape of the axes of the datasets not in the arrays.
        """
        DAAXES, DNAXIS = self.header["DAAXES"], self.header["DNAXIS"]
        return tuple(self.header[f"DNAXIS{d}"] for d in range(DAAXES + 1, DNAXIS + 1))

    @property
    def dataset_shape(self):
        """
        The shape of the axes of the datasets not in the arrays.
        """
        DNAXIS = self.header["DNAXIS"]
        return tuple(self.header[f"DNAXIS{d}"] for d in range(1, DNAXIS + 1))

    @property
    def axes_types(self):
        """
        The list of DTYPEn for the first header.
        """
        return [self.header[f"DTYPE{n}"] for n in range(1, self.header["DNAXIS"] + 1)]

    @cached_property
    def header_array(self):
        """
        The header table as a numpy recarray with the shape of the dataset axes.
        """
        return np.array(self.headers).reshape(self.files_shape)

    @cached_property
    def varying_spatial_daxes(self) -> dict[str, list[int]]:
        """
        The FITS pixel axes over which CRVAL or PC vary.
        """
        NAXIS, DAAXES = self.header["NAXIS"], self.header["DAAXES"]
        # Find which dataset axes the pointing varies along
        # If any of these keys vary along any of the dataset axes we want to know
        naxis_v = list(range(1, NAXIS + 1))
        crval_keys = [f"CRVAL{n}" for n in naxis_v]
        pc_keys = [f"PC{i}_{j}" for i, j in product(naxis_v, naxis_v)]
        varying_axes = defaultdict(list)
        for i in range(len(self.files_shape)):
            tslice = self.slice_for_file_axes(i)
            sliced_headers = self.header_array[tslice]
            if not self.constant_columns(sliced_headers, pc_keys):
                varying_axes["pc"].append(DAAXES + i + 1)
            if not self.constant_columns(sliced_headers, crval_keys):
                varying_axes["crval"].append(DAAXES + i + 1)

        return dict(varying_axes)

    @cached_property
    def varying_temporal_daxes(self) -> list[int]:
        """
        The FITS pixel axes over which time varies.
        """
        varying_daxes = []
        for i in range(len(self.files_shape)):
            tslice = self.slice_for_file_axes(i)
            sliced_headers = self.header_array[tslice]
            if not (sliced_headers[0]["DATE-AVG"] == sliced_headers["DATE-AVG"]).all():
                varying_daxes.append(self.header["DAAXES"] + i + 1)
        return varying_daxes

    @cached_property
    def pixel_axis_type_map(self) -> OrderedDict[str, list[int]]:
        """
        A dict which maps from DTYPE to the python array indices which contribute to that type.
        """
        axes_types = [self.header[f"DTYPE{n}"] for n in range(1, self.header["DNAXIS"] + 1)]
        axes_types = np.array(self.axes_types)
        type_map = defaultdict(list)
        if "STOKES" in self.axes_types:
            type_map["STOKES"] = np.argwhere(axes_types == "STOKES").flatten().tolist()
        if "SPECTRAL" in self.axes_types:
            type_map["SPECTRAL"] = np.argwhere(axes_types == "SPECTRAL").flatten().tolist()

        # Convert from FITS to Python
        vaxes = np.empty((0,), dtype=int)
        if self.varying_spatial_daxes:
            vaxes = np.array(self.compute_varying_axes_numbers(self.varying_spatial_daxes)) - 1
        type_map["SPATIAL"] = np.unique(
            np.concatenate((np.argwhere(axes_types == "SPATIAL").flatten(), vaxes))).tolist()
        ttypes = np.argwhere(axes_types == "TEMPORAL").flatten()
        taxes = np.array(self.varying_temporal_daxes) - 1
        type_map["TEMPORAL"] = np.unique(np.concatenate((ttypes, taxes))).tolist()

        # Just being really explicit that the ordering in this dict matters
        # By ordering like this we can use the order of the keys to order the transforms
        return OrderedDict(sorted(type_map.items(), key=lambda item: min(item[1])))
