"""Script to change the volcanic forcing used in CESM.

Need to reset the time dimension, and the variables date, datesec and stratvolc.

`time` is easy, doesn't even contain any coordinates
- Set to `np.arange(N)`
`date` are ints and formatted in YYYYMMDD
- Choose using implementation from `volcano-cooking`
`datesec` are ints with seconds since midnight info
- Choose noon (43200), for example

`stratvolc` is a bit more tricky, but not too bad. Set all events to some lat/lon (0, 0),
and find a suitable altitude (perhaps from `volcano-cooking`). Then the values are set
using the implementations from `volcano-cooking`.
"""
import os
from datetime import datetime

import numpy as np
import xarray as xr

# from volcano_cooking import helper_scripts
from volcano_cooking.modules import convert
from volcano_cooking.modules.create.create_data import Data


class ReWrite(Data):
    def make_dataset(self) -> None:
        """Re-writes the original netCDF file with new variables.

        Raises
        ------
        IndexError
            If the loaded dataset does not include needed dimensions and variables.
        FileNotFoundError
            If the original forcing file cannot be found.
        """
        file = os.path.join(
            "data",
            "originals",
            "VolcanEESMv3.11_SO2_850-2016_Mscale_Zreduc_2deg_c191125",
        )
        if not os.path.exists(file + ".nc"):
            raise FileNotFoundError(
                f"{file} not found. Consult README on how to download."
            )
        f_orig = xr.open_dataset(file + ".nc", decode_times=False)
        # Check that the file contain crucial data.
        needed_dims = ["time", "altitude", "lat", "lon"]
        if any(d not in f_orig.dims for d in needed_dims):
            raise IndexError(f"Need dimensions {needed_dims}, found {f_orig.dims}")
        if "stratvolc" not in f_orig.data_vars:
            raise IndexError("Could not find 'stratvolc' variable.")
        if f_orig["stratvolc"].dims != ("time", "altitude", "lat", "lon"):
            raise IndexError(
                "'stratvolc' variable do not contain all needed dimensions, "
                + "or they are in incorrect order."
            )
        size = len(self.yoes)
        _, d_alt, d_lat, d_lon = f_orig["stratvolc"].shape
        new_eruptions = np.zeros((size, d_alt, d_lat, d_lon), dtype=np.float32)
        # We keep all spatial dimensions the same, but delete and re-sets the temporal
        # dimension.
        self.my_frc = xr.Dataset()
        self.miihs: np.ndarray
        self.mxihs: np.ndarray
        self.tes: np.ndarray
        # NOTE: which altitudes should we choose? Use bound from min and max injection
        # height, and the same emission on all altitudes. The emission at a given time
        # changes with altitude, but is generally of the same magnitude. Probably okay.
        zero_lat = np.abs(f_orig.lat.data).argmin()  # Find index closest to lat = 0
        zero_lon = np.abs(f_orig.lon.data).argmin()  # Find index closest to lon = 0
        self.miihs, self.mxihs = convert.adjust_altitude_range(
            self.miihs, self.mxihs, self.tes
        )
        self.tes = convert.adjust_emissions(
            self.miihs,
            self.mxihs,
            self.tes,
            np.array([zero_lon]),
            np.array([zero_lat]),
        )
        ai_dim = "altitude_int"
        self.my_frc = self.my_frc.expand_dims(**{ai_dim: f_orig[ai_dim]})
        self.my_frc = self.my_frc.assign_attrs(**f_orig.attrs)
        self.my_frc[ai_dim] = self.my_frc[ai_dim].assign_attrs(**f_orig[ai_dim].attrs)
        self.my_frc.attrs["data_summary"] = ""
        # Loops over time to set all spatial dimensions
        reset = False
        for i, emission in enumerate(self.tes):
            alt_range = f_orig.altitude.where(
                (f_orig.altitude <= self.mxihs[i]) & (f_orig.altitude >= self.miihs[i]),
                drop=True,
            ).astype(int)
            if not any(alt_range.data):
                if not reset:
                    txt_0 = "Re-setting alt. range for eruption at time:\n"
                    self.my_frc.attrs["data_summary"] += txt_0
                    reset = True
                alt_range = f_orig.altitude[-10:].astype(int)
                nd = (
                    10000 * self.yoes[i].astype(np.float32)
                    + 100 * self.moes[i].astype(np.float32)
                    + self.does[i].astype(np.float32)
                )
                d = "0" * (8 - len(str(int(nd)))) + str(int(nd))
                amin_0 = f"{self.miihs[i]:.3f}"
                amax_0 = f"{self.mxihs[i]:.3f}"
                amin_1 = f"{alt_range[0].data}"
                amax_1 = f"{alt_range[-1].data}"
                txt = f"{d}: ({amin_0}, {amax_0}) -> ({amin_1}, {amax_1})\n"
                self.my_frc.attrs["data_summary"] += txt
                self.mxihs[i] = alt_range[-1]
                self.miihs[i] = alt_range[0]
            new_eruptions[i, alt_range, zero_lat, zero_lon] = emission
        new_dates = (
            10000 * self.yoes.astype(np.float32)
            + 100 * self.moes.astype(np.float32)
            + self.does.astype(np.float32)
        )
        new_datesecs = np.array([43200.0 for _ in range(size)])  # Noon

        for v in f_orig.data_vars:
            # Place variables in the new Dataset that are taken from the original. This
            # way, all meta data is also used in the new Dataset as in the old, which is
            # needed.
            if v == "stratvolc":
                input = xr.DataArray(
                    new_eruptions,
                    dims=["time", "altitude", "lat", "lon"],
                    coords={
                        "altitude": f_orig.altitude,
                        "lat": f_orig.lat,
                        "lon": f_orig.lon,
                    },
                )
            elif v == "date":
                input = xr.DataArray(new_dates.astype(np.int32), dims="time")
            elif v == "datesec":
                input = xr.DataArray(new_datesecs.astype(np.int32), dims="time")
            else:
                raise IndexError(
                    f"'{v}' is an unknown variable that I do not have an implementation for."
                )
            input = input.assign_attrs(**f_orig[v].attrs)
            self.my_frc = self.my_frc.assign({v: input})

        # helper_scripts.compare_datasets(self.my_frc, f_orig)

    def __set_global_attrs(self, file) -> None:
        for a in self.my_frc.attrs:
            if a == "filename":
                self.my_frc.attrs[a] = file
            elif a == "title":
                start = f"{self.yoes[0]}.{self.moes[0]}.{self.does[0]}"
                end = f"{self.yoes[-1]}.{self.moes[-1]}.{self.does[-1]}"
                self.my_frc.attrs[a] = (
                    "SO2 emissions from synthetic stratospheric "
                    + f"volcanoes, {start}-{end}"
                )
            elif a == "data_creator":
                self.my_frc.attrs[
                    a
                ] = "Eirik Rolland Enger, University of Tromsø, eirik.r.enger@uit.no"
            elif a == "data_doi":
                self.my_frc.attrs[a] = "No doi yet"
            elif a == "data_source_url":
                self.my_frc.attrs[a] = "https://github.com/engeir/volcano-cooking"
            elif a == "data_reference":
                self.my_frc.attrs[a] = "No reference yet"
            elif a == "data_source_files":
                self.my_frc.attrs[a] = "https://github.com/engeir/volcano-cooking"
            elif a == "creation_date":
                if datetime.today().strftime("%Z"):
                    this_day = datetime.today().strftime("%a %b %d %X %Z %Y")
                else:
                    this_day = datetime.today().strftime("%a %b %d %X %Y")
                self.my_frc.attrs[a] = this_day
            elif a == "cesm_contact":
                self.my_frc.attrs[a] = "None"
            elif a == "data_script":
                self.my_frc.attrs[
                    a
                ] = "Generated with the 'volcano-cooking' CLI with the re-write option."
            elif a == "data_summary":
                nd = (
                    10000 * self.yoes.astype(np.float32)
                    + 100 * self.moes.astype(np.float32)
                    + self.does.astype(np.float32)
                )
                tot_width = 40
                w_1, w_23, w_4, w_5 = 8, 7, 3, 11
                summary = "\nThis file is for the following volcanoes:\n"
                summary += "=" * tot_width + "\n"
                summary += "YYYYMMDD AltMin  AltMax  VEI Em(cm-3s-1)\n"
                for d, amin, amax, v, e in zip(
                    nd, self.miihs, self.mxihs, self.veis, self.tes
                ):
                    d_ = "0" * (w_1 - len(str(int(d)))) + str(int(d)) + " "
                    amin_ = f"{amin:.3f}".rjust(w_23) + " "
                    amax_ = f"{amax:.3f}".rjust(w_23) + " "
                    v_ = str(v).center(w_4) + " "
                    e_ = f"{e:.5e}".rjust(w_5)
                    nl = d_ + amin_ + amax_ + v_ + e_ + "\n"
                    summary += nl
                self.my_frc.attrs[a] += summary
                self.my_frc.attrs[a] = self.my_frc.attrs[a]

    def save_to_file(self) -> None:
        """Save the re-written forcing file with the date at the end.

        Raises
        ------
        ValueError
            If a dataset have not yet been created.
        """
        if not hasattr(self, "my_frc"):
            raise ValueError("You must make the dataset with 'make_dataset' first.")
        file = "VolcanEESMv3.11_SO2_850-2016_Mscale_Zreduc_2deg_c191125_edit"
        out_file = self.check_dir("nc", name=file)
        self.__set_global_attrs(file=out_file)
        encoding = {
            "lat": {"_FillValue": None},
            "lon": {"_FillValue": None},
            "altitude": {"_FillValue": None},
            "altitude_int": {"_FillValue": None},
            "stratvolc": {"_FillValue": 9.96921e36},
            "date": {"_FillValue": -2147483647},
            "datesec": {"_FillValue": -2147483647},
        }
        self.my_frc.to_netcdf(out_file, "w", format="NETCDF3_64BIT", encoding=encoding)
