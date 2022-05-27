"""Module containing the main Data Analyzer"""
import logging
from datetime import datetime
import sys

import numpy as np
import pandas as pd

import nmrquant.logger

from nmrquant.engine.utilities import read_data, is_empty, append_value

mod_logger = logging.getLogger("RMNQ_logger.engine.calculator")


# noinspection PyBroadException
class Quantifier:
    """
    RMNQ main class to quantify and visualize data
    """

    def __init__(self, verbose=False):

        self.verbose = verbose
        # When True, Strd concentration will be used to calculate concentration
        self.use_strd = False
        # Initialize child logger for class instances
        self.logger = logging.getLogger(f"RMNQ_logger.engine.calculator.Quantifier")
        # fh = logging.FileHandler(f"{self.run_name}.log")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        # For debugging purposes
        if verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        # Data attributes (future DataFrames)
        self.data = None
        self.mdata = None
        self.database = None
        self.metadata = None
        self.cor_data = None
        self.calc_data = None
        self.conc_data = None
        self.mean_data = None
        self.std_data = None
        self.plot_data = None
        self.ind_plot_data = None
        self.mean_plot_data = None
        # Lists with template info
        self.metabolites = []
        self.conditions = []
        self.time_points = []
        # Dictionary that will contain H+ count for each metabolite
        self.proton_dict = {}
        # List for missing metabolites in db
        self.missing_metabolites = []
        # For generating template
        self.spectrum_count = 0
        # Should be over 1
        self.dilution_factor = 1.11

    def __len__(self):
        """ Length of object is equal to number of
        metabolites in dataset"""

        return f" There are {len(self.metabolites)} metabolites in data set"

    def __repr__(self):
        return "Quantifier object to calculate concentrations from 1D " \
               "NMR data and visualize results"

    def get_data(self, data, excel_sheet=0):
        """Get data from path or excel file"""

        if isinstance(data, str):
            try:
                self.data = read_data(data, excel_sheet)
            except TypeError as tperr:
                self.logger.error(f"Error while reading data:{tperr}")
        else:
            self.data = data
        try:
            if self.data.at[1, "Strd"] == 9:
                self.use_strd = True
            self.data.drop("Strd", axis=1, inplace=True)
        except KeyError:
            self.logger.error("Strd not found in columns")
        except Exception:
            self.logger.exception(f"Unexpected error")
        self.spectrum_count = self.data["# Spectrum#"].max()
        self.logger.info("Data has been loaded")

    def get_db(self, database):
        """
        Get database from file or path

        :param database: Can be a file directly or a str containing the path to the file
        """

        if isinstance(database, str):
            self.database = read_data(database)
            if "Metabolite" not in self.database.columns or "Heq" not in self.database.columns:
                self.logger.error("'Metabolite' and/or 'Heq' columns not found in file. Please check your database "
                                  "file headers")
        else:
            self.database = database
        try:
            self.database.sort_values(by="Metabolite", inplace=True)
            if self.database["Heq"].dtypes != np.float64:
                self.database["Heq"] = self.database["Heq"].apply(
                    lambda x: x.replace(',', '.'))
                self.database["Heq"] = pd.to_numeric(self.database["Heq"])
            for _, met, H in self.database[["Metabolite", "Heq"]].itertuples():
                self.proton_dict.update({met: H})
        except KeyError:
            self.logger.exception('DataFrame error, are you sure you imported the right file?')
        except Exception:
            self.logger.exception(f'Unexpected error')
        else:
            self.logger.info("Database has been loaded")

    def generate_metadata(self, path):
        """Generate template in excel format"""

        self.logger.info("Generating Template...")
        md = pd.DataFrame(columns=["Conditions", "Time_Points", "Replicates"])
        md["# Spectrum#"] = range(1, self.spectrum_count + 1)
        md.Conditions = ""
        md.Time_Points = ""
        md.Replicates = ""
        md.to_excel(rf'{path}/template.xlsx', index=False)
        self.logger.info("Template generated")

    def import_md(self, md):
        """Import metadata file after modification from path or file

        :param md: Can be a file directly or a str containing the path to the file
        """

        self.logger.info("Reading metadata...")
        if isinstance(md, str):
            try:
                self.metadata = read_data(md)
                headers = ["Conditions", "Time_Points", "Replicates", "# Spectrum#"]
                for head in headers:
                    if head not in self.metadata.columns:
                        raise RuntimeError(f'The column "{head}" was not found in file. Please check your template '
                                           f'file headers')
            except Exception:
                self.logger.exception(f"Error while reading template")
            else:
                self.conditions = self.metadata["Conditions"].unique()
                self.time_points = self.metadata["Time_Points"].unique()
        else:
            self.metadata = md
        self.logger.info("Metadata has been loaded")

    def _merge_md_data(self):
        """Merge user-defined metadata with dataset"""

        self.logger.info("Merging...")
        self.mdata = self.metadata.merge(self.data, on="# Spectrum#")
        self.mdata.set_index(["Conditions", "Time_Points",
                              "Replicates", "# Spectrum#"], inplace=True)
        self.mdata.replace(0, np.nan, inplace=True)
        self.logger.info("Merge done!")

    def _clean_cols(self):
        """Sum up double metabolite columns"""

        self.logger.info("Cleaning up columns...")
        tmp_dict = {}
        # Get rid of columns containing + sign because only
        # useful to calculate other cols (ex: LEU+ILE)
        cols = [c for c in self.mdata.columns if "+" not in c]
        self.logger.debug(f"Columns: {cols}")
        self.mdata = self.mdata[cols]
        del cols  # cleanup
        # Sort index so that numbered metabolites are together
        # which helps with the n_counting
        self.cor_data = self.mdata
        self.cor_data.sort_index(axis=1, inplace=True)
        self.logger.debug(f"Beginning cor_data = {self.cor_data}")
        # Get indices where metabolites are double
        for ind, col in enumerate(self.cor_data.columns):
            split = col.split("_")
            if len(split) > 1:  # Else there is no double metabolite
                append_value(tmp_dict, split[0], ind)
        self.logger.debug(f"Temp dict = {tmp_dict}")
        ncount = 0  # Counter for substracting from indices
        if is_empty(tmp_dict):
            return self.logger.info("No double metabolites in data set. Columns are clean")
        else:
            for key, val in tmp_dict.items():
                dropval = [x - ncount for x in val]  # Real indices after drops
                self.logger.debug(f"Dropvals = {dropval}")
                self.cor_data[key] = self.cor_data.iloc[:, dropval[0]] + self.cor_data.iloc[:, dropval[1]]
                self.cor_data.drop(self.cor_data.columns[dropval],
                                   axis=1, inplace=True)
                ncount += 2  # Not 1 because the new cols are added at the end of df
            self.logger.debug(f"End cor_data = {self.cor_data}")
        self.metabolites = list(self.cor_data.columns)
        return self.logger.info("Data columns have been cleaned")

    def _prepare_db(self):
        """Prepare database for concentration calculations"""

        tmp_dict = {}
        removed_values = []
        # Prepare to split on spaces for where there are
        # spaces there are numbers after (as for clean_cols).
        for key, val in self.proton_dict.items():
            split = key.split("_")
            self.logger.debug(f"Split = {split}")
            # Here we check the len of the split. If it is
            # over 1, we get the name of the metabolite
            # and put it in the tmp_dict. The Key is then
            # put in list to remove later
            if len(split) > 1:
                append_value(tmp_dict, split[0], val)
                removed_values.append(key)
        self.logger.debug(f"Temp dict = {tmp_dict}")
        self.logger.debug(f"Removed values = {removed_values}")
        if is_empty(tmp_dict):
            return self.logger.info(
                "No double metabolites in data set. Database entries are clean")
        else:
            self.logger.debug(tmp_dict)
            # We sum up the values for keys in the tmp dict because they
            # are the total protons for the concerned metabolite.
            tmp_dict = {key: sum(vals) for key, vals in tmp_dict.items()}
            self.logger.debug(f"Summed temp dict = {tmp_dict}")
            self.logger.debug(f"Proton dict before del = {self.proton_dict}")
            # We remove the keys with numbers in the original proton dict
            for key in removed_values:
                del self.proton_dict[key]
            # We merge the dicts to have the final proton dict (thank you
            # python 3.9)
            if sys.version_info[0] >= 3.9:
                self.proton_dict = self.proton_dict | tmp_dict
            else:
                self.logger.warning("Python version different from 3.9. Please consider "
                                    "upgrading for compatibility reasons in the future")
                self.proton_dict = {**self.proton_dict, **tmp_dict}
            self.logger.debug(f"Proton dict after del = {self.proton_dict}")
        return self.logger.info("Database ready!")

    def calculate_concentrations(self, strd_conc=1):
        """
        Calculate concentrations using number of
        protons and dilution factor

        :param strd_conc: Standard concentration for external calibration. If calibration is internal, concentration
                         is equal to one.
        :return self.conc_data: Dataframe containing calculated concentrations
        """

        self.logger.info("Calculating concentrations...")
        # Check for NA and prepare dataframe
        self.cor_data.fillna(0, inplace=True)
        self.conc_data = pd.DataFrame(columns=self.cor_data.columns)
        # Multiply areas by dilution factor and standard concentration (equal to 1 if internal calibration)
        self.logger.debug(f"Dilution factor: {self.dilution_factor}")
        self.logger.debug(f"Standard Concentration: {strd_conc}")
        self.logger.debug(f"Dataframe before multiplications: \n {self.cor_data}")
        self.conc_data = self.cor_data.apply(lambda x: (x * self.dilution_factor * strd_conc))
        self.logger.debug(f"Dataframe after multiplications: \n {self.conc_data}")
        self.logger.debug(f"Proton dict before del = {self.proton_dict}")
        # Divide for each metabolite the values by proton number to get concentrations
        for col in self.conc_data.columns:
            missing_from_db = False  # To check if value is missing. If true then add a star in front of met name
            if col not in self.proton_dict.keys():
                self.missing_metabolites.append(col)
                proton_val = 1
                missing_from_db = True
                self.logger.debug(f"Renamed column: {col}")
                self.conc_data.rename(columns={col: col + "_Area"}, inplace=True)
            else:
                for key, val in self.proton_dict.items():
                    if key == col:
                        proton_val = val
                        break
            if missing_from_db:
                self.conc_data[col + "_Area"] = self.conc_data[col + "_Area"].apply(lambda x: x / proton_val)
                self.metabolites = list(self.conc_data.columns)
            else:
                self.logger.debug(f"Proton value for {col}: {proton_val}")
                self.logger.debug(f"{col} before division by proton_number: {self.conc_data[col]}")
                self.conc_data[col] = self.conc_data[col].apply(lambda x: x / proton_val)
                self.logger.debug(f"{col} after division by proton_number: {self.conc_data[col]}")
                self.metabolites = list(self.conc_data.columns)
        if self.missing_metabolites:
            self.logger.warning(f"The following metabolites have no correspondence in the database: "
                                f"\n{self.missing_metabolites}")
        self.logger.info("Concentrations have been calculated")

    def _get_mean(self):
        """Make dataframe meaned on replicates"""

        self.mean_data = self.conc_data.droplevel("# Spectrum#")
        self.mean_data = self.conc_data.groupby(
            ["Conditions", "Time_Points"]).mean()
        self.std_data = self.conc_data.groupby(
            ["Conditions", "Time_Points"]).std()
        return self.logger.info("Means and standard deviations have been calculated")

    def export_data(self, destination, file_name='', fmt="excel", export_mean=False):
        """Export final data in desired format"""

        # Get current date & time
        date_time = datetime.now().strftime("%d%m%Y %Hh%Mmn")
        name = file_name + '_' + date_time
        # Output to multi-page excel file
        if fmt == "excel":
            with pd.ExcelWriter(r"{}/{}.xlsx".format(destination, name)) as writer:
                self.mdata.to_excel(writer, sheet_name='Raw Data')
                self.conc_data.to_excel(writer, sheet_name='Concentrations Data')
                if export_mean:
                    self.mean_data.to_excel(writer, sheet_name='Meaned Data')
                    self.std_data.to_excel(writer, sheet_name='Stds')
        return self.logger.info("Data Exported")

    def compute_data(self, strd_conc=None, mean=False):
        """
        Run data preparation and computation of concentrations (if strd_conc is not None, else just prepare data)

        :param strd_conc: Concentration of standard molecule used (1 if concentration is not needed). Set to None if
        concentrations must not be calculated
        :param mean: should means be computed
        """
        for data in [self.database, self.data, self.metadata]:
            if not isinstance(data, pd.DataFrame):
                raise ValueError(f"Data is missing for computation. Missing data: {data}")
        self._merge_md_data()
        self._clean_cols()
        self._prepare_db()
        if strd_conc:
            self.calculate_concentrations(strd_conc)
        if mean:
            self._get_mean()
