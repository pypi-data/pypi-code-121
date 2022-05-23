"""Script that implement the class which correctly created a netCDF4 file and saves it."""

import datetime
import os
import sys
from abc import ABC, abstractmethod
from typing import List

import numpy as np
import xarray as xr

import volcano_cooking.modules.convert as convert
import volcano_cooking.modules.create as create


class Data:
    """Create data for a volcanic forcing file.

    Attributes
    ----------
    make_dataset: method
        Create the xarray data set with the numpy arrays provided to the class on
        initialisation.
    save_to_file: method
        Save the generated xarray data set as a netCDF4 file, and the defining numpy
        arrays to a .npz file.
    """

    def __init__(
        self,
        eruptions: np.ndarray,
        yoes: np.ndarray,
        moes: np.ndarray,
        does: np.ndarray,
        lats: np.ndarray,
        lons: np.ndarray,
        tes: np.ndarray,
        veis: np.ndarray,
        miihs: np.ndarray,
        mxihs: np.ndarray,
    ) -> None:
        """Initialise object by giving all variables that should be put in the .nc file.

        Parameters
        ----------
        eruptions: np.ndarray
            Eruption number
        yoes: np.ndarray
            Years (four digit number) that the volcanoes occurred
        moes: np.ndarray
            Months (two digit number) that the volcanoes occurred
        does: np.ndarray
            Days (two digit number) that the volcanoes occurred
        lats: np.ndarray
            Latitudinal coordinate
        lons: np.ndarray
            Longitudinal coordinate
        tes: np.ndarray
            Total emission from a volcano at corresponding date
        veis: np.ndarray
            VEI (Volcanic Explosivity Index) of a volcano at corresponding date
        miihs: np.ndarray
            Minimum injection height
        mxihs: np.ndarray
            Maximum injection height
        """
        self.eruptions = eruptions
        self.yoes = yoes
        self.moes = moes
        self.does = does
        self.lats = lats
        self.lons = lons
        self.tes = tes
        self.veis = veis
        self.miihs = miihs
        self.mxihs = mxihs
        self.__run_check()
        self.my_frc: xr.Dataset

    def __run_check(self) -> None:
        """Check the data type of each numpy array.

        The original netCDF file that is re-produced has specific data types on all data
        arrays. This method checks to see if the types are set correctly.

        Raises
        ------
        ValueError
            If any of the ten numpy arrays contain data of wrong type a ValueError is
            raised. ValueError is also raised if they do not have the same shape.
        """
        stack = [
            self.eruptions.shape,
            self.yoes.shape,
            self.moes.shape,
            self.does.shape,
            self.lats.shape,
            self.lons.shape,
            self.tes.shape,
            self.veis.shape,
            self.miihs.shape,
            self.mxihs.shape,
        ]
        if not (np.diff(np.vstack(stack).reshape(len(stack), -1), axis=0) == 0).all():
            raise ValueError(f"The arrays have different shapes:\n{stack}")
        else:
            del stack
        if (
            self.eruptions.dtype != np.int8
            or self.veis.dtype != np.int8
            or self.moes.dtype != np.int8
            or self.does.dtype != np.int8
        ):
            raise ValueError(
                f"self.eruptions.dtype = {self.eruptions.dtype}, "
                + f"self.veis.dtype = {self.veis.dtype}, "
                + f"self.moes.dtype = {self.moes.dtype}, "
                + f"self.does.dtype = {self.does.dtype}. All must be int8."
            )
        if self.yoes.dtype != np.int16:
            raise ValueError(f"{self.yoes.dtype} = . Need int16.")
        if (
            self.tes.dtype != np.float32
            or self.mxihs.dtype != np.float32
            or self.miihs.dtype != np.float32
            or self.lats.dtype != np.float32
            or self.lons.dtype != np.float32
        ):
            raise ValueError(
                f"self.tes.dtype = {self.tes.dtype}, "
                + f"self.mxihs.dtype = {self.mxihs.dtype}, "
                + f"self.miihs.dtype = {self.miihs.dtype}, "
                + f"self.lats.dtype = {self.lats.dtype}"
                + f"self.lons.dtype = {self.lons.dtype}. All must be float32."
            )

    def make_dataset(self) -> None:
        """Make an xarray Dataset object where all variables are stored."""
        self.my_frc = xr.Dataset(
            data_vars=dict(
                Eruption=(["Eruption_Number"], self.eruptions),
                VEI=(["Eruption_Number"], self.veis),
                Year_of_Emission=(["Eruption_Number"], self.yoes),
                Month_of_Emission=(["Eruption_Number"], self.moes),
                Day_of_Emission=(["Eruption_Number"], self.does),
                Latitude=(["Eruption_Number"], self.lats),
                Longitude=(["Eruption_Number"], self.lons),
                Total_Emission=(["Eruption_Number"], self.tes),
                Maximum_Injection_Height=(["Eruption_Number"], self.mxihs),
                Minimum_Injection_Height=(["Eruption_Number"], self.miihs),
            ),
            # Global attributes
            attrs=dict(
                Creator="Eirik R. Enger",
                DOI="#####",
                Citation="#####",
                Notes="All emissions are created from a filtered Poisson process (FPP).",
            ),
        )

        size = len(self.yoes)
        # Names are unimportant. The real data set would list the name of the volcano
        # here, e.g. Mt. Pinatubo.
        names = "".join("N, " for _ in range(size))
        names = names[:-2]  # Removing the last comma and whitespace
        self.my_frc.Longitude.encoding["_FillValue"] = False
        self.my_frc["Eruption"] = self.my_frc.Eruption.assign_attrs(
            # The volcano number is a reference to the geographical location of the
            # eruption. The volcano name is its name and the note/reference is where in
            # the literature you can find the values related to the eruption. All this is
            # unimportant given that this is just made up data.
            Volcano_Number=np.ones(size) * 123456,
            Volcano_Name=names,
            Notes_and_References=names,
        )
        self.my_frc["VEI"] = self.my_frc.VEI.assign_attrs(
            Notes="Volcanic_Explosivity_Index_based_on_Global_Volcanism_Program"
        )
        self.my_frc["Latitude"] = self.my_frc.Latitude.assign_attrs(Units="-90_to_+90")
        self.my_frc["Longitude"] = self.my_frc.Longitude.assign_attrs(
            Units="Degrees_East"
        )
        self.my_frc["Total_Emission"] = self.my_frc.Total_Emission.assign_attrs(
            Units="Tg_of_SO2"
        )
        self.my_frc[
            "Maximum_Injection_Height"
        ] = self.my_frc.Maximum_Injection_Height.assign_attrs(
            Units="km_above_mean_sea_level"
        )
        self.my_frc[
            "Minimum_Injection_Height"
        ] = self.my_frc.Minimum_Injection_Height.assign_attrs(
            Units="km_above_mean_sea_level"
        )

    def save_to_file(self) -> None:
        """Save the xarray Dataset object to a .nc file using the netCDF4 format.

        For easier access to the forcing data, dates and total emissions are also saved to
        a .npz file.
        """
        self.__save_to_nc_file()
        self.__save_to_npz_file()

    def __save_to_npz_file(self) -> None:
        """Save the original forcing data to a .npz file."""
        out_file = self.check_dir("npz")
        np.savez(out_file, yoes=self.yoes, moes=self.moes, does=self.does, tes=self.tes)

    def __save_to_nc_file(self) -> None:
        """Save the xarray Dataset object to a .nc file using the netCDF4 format.

        Raises
        ------
        ValueError
            If the attribute `my_frc` has not been filled yet, `ValueError` is raised
            telling the user to first call the `make_dataset` method.
        """
        if not hasattr(self, "my_frc"):
            raise ValueError("You must make the dataset with 'make_dataset' first.")
        out_file = self.check_dir("nc")
        # The format is important for when you give the .nc file to the .ncl script that
        # creates the final forcing file.
        self.my_frc.to_netcdf(out_file, "w", format="NETCDF4")
        # self.my_frc.to_netcdf(out_file, "w", format="NETCDF4_CLASSIC")

    @staticmethod
    def check_dir(ext: str, name: str = "synthetic_volcanoes") -> str:
        """Check if the directory exist and there is no other file with the same name.

        Parameters
        ----------
        ext: str
            The file ending
        name: str
            The file name. Defaults to 'synthetic_volcanoes'.

        Returns
        -------
        str
            The path and name of the file that can be created
        """
        if ext[0] == ".":
            ext = ext[1:]
        d = os.path.join("data", "output")
        if not os.path.isdir(d):
            os.makedirs(d)
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = os.path.join(d, f"{name}_{now}.{ext}")
        if os.path.isfile(out_file):
            sys.exit(f"The file {out_file} already exists.")
        return out_file


class Generate(ABC):
    """ABC for generating data with different properties."""

    def __init__(self, size: int, init_year: int) -> None:
        """Initialise object by giving all variables that should be put in the .nc file.

        Parameters
        ----------
        size: int
            The total number of volcanoes
        init_year: int
            The first possible year for a volcanic eruption
        """
        self.eruptions: np.ndarray = np.array([])
        self.yoes: np.ndarray = np.array([])
        self.moes: np.ndarray = np.array([])
        self.does: np.ndarray = np.array([])
        self.lats: np.ndarray = np.array([])
        self.lons: np.ndarray = np.array([])
        self.tes: np.ndarray = np.array([])
        self.veis: np.ndarray = np.array([])
        self.miihs: np.ndarray = np.array([])
        self.mxihs: np.ndarray = np.array([])
        self.size = size
        self.init_year = init_year

    @abstractmethod
    def gen_dates_totalemission_vei(self) -> None:
        """Generate dates, total emission and VEI."""

    def _gen_rest(self) -> None:
        """Generate the rest with default settings.

        The rest refer to `eruptions`, the eruption number, `lats`, `lons` and `miihs` and
        `mxihs`, the minimum and maximum heights of injection which are both assumed
        functions of `veis`, the Volcanic Explosivity Index.
        """
        # This only (in the real data set) store a number for each volcanic event,
        # increasing as new events occur. If a volcanic eruption have several emissions
        # listed in the forcing file the number is repeated, giving a list similar to [1,
        # 2, 3, 4, 4, 4, 5, 5, 6, 7, ...].  Here, the fourth and fifth eruptions lasted
        # long enough and to get more samples in the forcing file. Anyway, its most likely
        # not important, so I just put gibberish in it.
        self.eruptions = np.random.randint(1, high=20, size=self.size, dtype=np.int8)

        # Place all volcanoes at equator
        self.lats = np.zeros(self.size, dtype=np.float32)  # Equator
        self.lons = np.ones(self.size, dtype=np.float32)

        self.miihs, self.mxihs = convert.vei_to_injectionheights(self.veis)

    def generate(self) -> None:
        """Generate all data arrays needed in the volcanic forcing netCDF file.

        Ten arrays of equal shape are created; eruption number, year-month-day,
        latitude-longitude, total emission, volcanic explosivity index and minimum &
        maximum injection heights.
        """
        self.gen_dates_totalemission_vei()
        # Shift first eruption to occur before initial year
        self.yoes -= abs(self.init_year - self.yoes[0]) + 1
        if len(self.veis) != self.size:
            self.size = len(self.veis)
        self._gen_rest()

    def get_arrays(self) -> List[np.ndarray]:
        """Return all generated data.

        Returns
        -------
        list
            A list of all arrays. Order is the same as the input to the Data class

        Raises
        ------
        AttributeError
            If any one array has not been set, i.e. is still a 'type' object
        """
        arrs = [
            self.eruptions,
            self.yoes,
            self.moes,
            self.does,
            self.lats,
            self.lons,
            self.tes,
            self.veis,
            self.miihs,
            self.mxihs,
        ]
        if any(len(a) == 0 for a in arrs):
            raise AttributeError(
                "Attribute(s) do not exist. Run the 'generate' method."
            )
        return arrs


class GenerateRandomNormal(Generate):
    def gen_dates_totalemission_vei(self):
        self.yoes, self.moes, self.does = create.random_dates(self.size, self.init_year)
        # We don't want eruptions that have a VEI greater than 6.
        self.veis = np.random.normal(4, 1, size=self.size).round().astype(np.int8) % 7
        self.tes = convert.vei_to_totalemission(self.veis)


class GenerateFPP(Generate):
    def gen_dates_totalemission_vei(self):
        self.yoes, self.moes, self.does, self.tes = create.fpp_dates_and_emissions(
            self.size, self.init_year
        )
        self.veis = convert.totalemission_to_vei(self.tes)


class GenerateRegularIntervals(Generate):
    def gen_dates_totalemission_vei(self) -> None:
        self.yoes, self.moes, self.does, self.tes = create.regular_intervals()
        self.veis = convert.totalemission_to_vei(self.tes)


class GenerateSingleVolcano(Generate):
    def gen_dates_totalemission_vei(self) -> None:
        self.yoes, self.moes, self.does, self.tes = create.single_date_and_emission(
            self.init_year
        )
        self.veis = convert.totalemission_to_vei(self.tes)
