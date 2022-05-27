# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 15:44:00 2020

@author: Carlos Rodero, Raul Bardaji, Jaume Piera

Module to analyze data from the KdUINO

"""
import pandas as pd
import numpy as np
import mooda as md
import glob
import yaml
import re
import os
from io import StringIO
import matplotlib.pyplot as plt
from matplotlib import style
from scipy import stats, interpolate
import plotly.graph_objects as go
import matplotlib.dates as mdates


class KduinoDataAnalysis:
    """
    Class to analyse different versions of KdUINO.
    It needs a properties file with all the information

    Parameters
    ----------
        properties_fname: str
            Name of properties file without extension. By default, "properties".

    """

    def __init__(self, doc):

        #properties_file = properties_fname + ".yaml"
        # Get properties from properties file
        self.doc = doc


    def __file_kdupro_rgb_to_wf(self, path):
        """
        It creates a WaterFrame with the data of the Kdupro file.

        Parameters
        ----------
            path: str
                Path to the file.

        Returns
        -------
            wf: WaterFrame
        """
        # Open the file
        with open(path) as reader:
            content = reader.read()

        # Definitions for regular expression paterns
        start_string_metadata = r"METADATA"
        stop_string_metadata = r"DATA"
        # start_string_data = r"\bDATA\b"
        # stop_string_data = r"METADATA"
        last_start_string_data = r'\bDATA\b'
        end_string_data = r'$(?![\r\n])'

        metadata_patron = re.compile(r'{}(?P<length>)\s*(?P<table>[\s\S]*?){}'.format(
            start_string_metadata, stop_string_metadata))

        data_patron = re.compile(r'{}(?P<length>)\s*(?P<table>[\s\S]*?){}'.format(
            last_start_string_data, end_string_data))

        selected_info = ""
        metadata_list = []
        metadata = {}

        if re.search(start_string_metadata, content) and re.search(last_start_string_data, content):
            pass
        else:
            print(f"File {path} not well formatted for Kdupro analysis")
            return

        # Regular expression to find the metadata patron
        for m in re.finditer(metadata_patron, content):
            selected_info = m.group('table')
            lines = selected_info.splitlines()
            # metadata = {}

            for line in lines:
                key = line.split(":")[0]
                # print(line)

                if line.count(":") > 1:
                    date_splitted = (line.rsplit(":")[-3:])
                    date_splitted = " ".join(date_splitted)
                    value = date_splitted
                    metadata[key] = value
                else:
                    value = line.split(":")[1]
                    metadata[key] = value.strip()

            # metadata_list.append(metadata)

        # Regular expression to find the last data patron
        for m in re.finditer(data_patron, content):
            selected_info_data = m.group('table')
            data = StringIO(selected_info_data)

            if self.doc['device'] == "kdupro_rgb":
                try:
                    df = pd.read_csv(data, skipinitialspace=True, skiprows=1, header=None, delimiter=' ',
                                     parse_dates={'TIME': [0, 1]}).set_index('TIME')

                except pd.errors.ParserError as er:
                    print(f"File {path} not well formatted for Kdupro analysis. Error: {er}")
                    return

            if self.doc['device'] == "kdupro_rgb_v1":
                try:
                    df = pd.read_csv(data, skipinitialspace=True, skiprows=1, header=None, delimiter=' ',
                                     parse_dates={'TIME': [0]}).set_index('TIME')
                    # print(df)

                except pd.errors.ParserError as er:
                    print(f"File {path} not well formatted for Kdupro analysis. Error: {er}")
                    return

        df.columns = range(df.shape[1])

        # Delete unused columns
        if self.doc['cumulative'] is False:
            if len(df.columns) > 4:
                df_copy = df.copy()
                ncol = len(df.columns)
                x = range(4, ncol)
                df = df.drop(x, axis=1)

        df.columns = range(df.shape[1])

        # Creation of WaterFrame
        wf = md.WaterFrame()

        # Copy metadata to waterframe
        wf.metadata = metadata

        depth = wf.metadata["depth"]

        # Set name of parameters
        param_red = f'RED_{depth}'
        param_green = f'GREEN_{depth}'
        param_blue = f'BLUE_{depth}'
        param_clear = f'CLEAR_{depth}'

        # Set name of QC parameters
        param_red_qc = f'RED_{depth}_QC'
        param_green_qc = f'GREEN_{depth}_QC'
        param_blue_qc = f'BLUE_{depth}_QC'
        param_clear_qc = f'CLEAR_{depth}_QC'

        # Init data of waterframe
        wf.data[param_red] = df[0]
        wf.data[param_green] = df[1]
        wf.data[param_blue] = df[2]
        wf.data[param_clear] = df[3]

        # Create vocabulary
        wf.vocabulary[param_red] = {'units': "counts",
                                    'long_name': "digital return of red light sensing values"}
        wf.vocabulary[param_green] = {'units': "counts",
                                      'long_name': "digital return of green light sensing values"}
        wf.vocabulary[param_blue] = {'units': "counts",
                                     'long_name': "digital return of blue light sensing values"}
        wf.vocabulary[param_clear] = {'units': "counts",
                                      'long_name': "digital return of clear light sensing values"}

        # If we do cumulative analysis
        if self.doc['cumulative'] is True:
            for i in range(len(df.columns)):
                if i < 4:
                    continue
                if i % 4 == 0:
                    wf.data[param_red] += df[i]
                    wf.data[param_green] += df[i+1]
                    wf.data[param_blue] += df[i+2]
                    wf.data[param_clear] += df[i+3]
        else:
            # Resample to seconds
            try:
                wf.resample('S')
            except TypeError as er:
                print(f"File {path} not well formatted for Kdupro analysis. Error: {er}")
                return

            # Delete last index because it is a minute that we are not going to use
            wf.data.drop(wf.data.tail(1).index, inplace=True)

            # Extract data of the dataframe df. Put all counts in the proper column
            red_list = []
            green_list = []
            blue_list = []
            clear_list = []
            for j in range(len(df_copy.index)-1):
                for i in range(len(df_copy.columns)):
                    if i % 4 == 0:
                        red_list.append(df_copy[i][j])
                        green_list.append(df_copy[i+1].iloc[j])
                        blue_list.append(df_copy[i+2].iloc[j])
                        clear_list.append(df_copy[i+3].iloc[j])
            red_array = np.array(red_list)
            green_array = np.array(green_list)
            blue_array = np.array(blue_list)
            clear_array = np.array(clear_list)

            try:
                wf.data[param_red] = red_array
                wf.data[param_green] = green_array
                wf.data[param_blue] = blue_array
                wf.data[param_clear] = clear_array
            except ValueError as er:
                print(f"Error doing waterframe at depth {depth}")

        # Init waterframe QC data
        wf.data[param_red_qc] = 0
        wf.data[param_green_qc] = 0
        wf.data[param_blue_qc] = 0
        wf.data[param_clear_qc] = 0

        return wf

    def __file_kdupro_multispectral_to_wf(self, path):
        """
        It creates a WaterFrame with the data of the Kdupro multispectral file.

        Parameters
        ----------
            path: str
                Path to the file.

        Returns
        -------
            wf: WaterFrame
        """
        # Open the file
        df = pd.read_csv(path, sep=",")

        df.rename(columns={"time": "TIME", "depth": "DEPTH"}, inplace=True)
        df["TIME"] = pd.to_datetime(df["TIME"])
        # df.set_index(["TIME", "DEPTH"], inplace=True)
        df.set_index("TIME", inplace=True)

        # Delete Unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Creation of WaterFrame
        wf = md.WaterFrame()

        wf.data = df

        # Resample time
        try:
            wf.resample(self.doc["resample"])
        except ValueError as er:
            print("Incorrect frequency of resample. Check your properties file")
            exit()

        return wf

    def __file_kdustick_to_wf(self, path):
        """
        It creates a WaterFrame with the data of the Kdustick file.

        Parameters
        ----------
            path: str
                Path to the file.

        Returns
        -------
            wf: WaterFrame
        """
        # Open the file
        """ df = pd.read_csv(path, skipinitialspace=True, skiprows=1, header=None, delimiter=' ',
                         parse_dates={'TIME': [0, 1]}).set_index('TIME') """
        df = pd.read_csv(path, sep=",", index_col="datetime")
        df.index = pd.to_datetime(df.index)
        df.index = df.index.rename("TIME")

        for column in df.columns:
            new_column = column.replace(" ", "_")
            df.rename(columns={column: new_column}, inplace=True)
            if "#" in column:
                new_column = column.replace("#", "")
                df.rename(columns={column: new_column}, inplace=True)

        # Delete Unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # Creation of WaterFrame
        wf = md.WaterFrame()

        wf.data = df

        return wf

    def __merge_metadata(self, dict1, dict2):
        '''
        Private method.
        Merge dictionaries and keep values of common keys in list
        Parameters
        ----------
            dict1: dict
                Dictionary with waterframe metadata

            dict2: dict
                Dictionary with waterframe metadata

        Returns
        ----------
            dict3: dict
                Dictionary with merged dictionaries of metadata
        '''
        # Merge dictionaries
        dict3 = {**dict1, **dict2}

        # Iterate over items in new dictionary
        for key, value in dict3.items():
            # If keys are in both dictionaries
            if key in dict1 and key in dict2:
                # If dictionary contains list of elements
                if isinstance(value, list):
                    # If values of new dict and values from parameter dict are different,
                    # and not included in the new dict
                    if (dict1[key] not in value) and (set(dict1[key]) != set(value)):
                        dict3[key].append(dict1[key])
                    elif (dict2[key] not in value) and (set(dict2[key]) != set(value)):
                        dict3[key].append(dict2[key])

                # If dictionary not contains list of elements
                else:
                    if value != dict1[key]:
                        dict3[key] = [value, dict1[key]]
                    elif value != dict2[key]:
                        dict3[key] = [value, dict2[key]]
        return dict3

    def __save_data(self, data_fname, wf):
        """
        Private method.
        Save data in different formats

        Parameters
        ----------
            data_fname: str
                Name of file without extension

            wf: Mooda waterframe object
                Waterframe with data
        """
        # Create directory to save files
        # If we do cumulative analysis
        if self.doc['cumulative'] is True:
            path = os.path.join(self.doc["path"], 'files', 'cumulative/')
        else:
            path = os.path.join(self.doc["path"], 'files', 'non_cumulative/')
        # Check whether the specified path is an existing directory or not
        is_dir = os.path.isdir(path)
        if not is_dir:
            try:
                os.makedirs(path)
            except OSError as er:
                print(f"Cannot save files in /files directory. {er}")
                exit()

        # Before save it in .nc, we have to pass list of values in metadata to string
        for key, value in wf.metadata.items():
            if isinstance(value, list):
                wf.metadata[key] = ', '.join(map(str, value))

        wf.to_nc(path=os.path.join(path, f'{data_fname}.nc'))
        wf.to_csv(path=os.path.join(path, f'{data_fname}.csv'))
        # wf.data.to_csv(os.path.join(path, f'{data_fname}.csv'), sep=';', float_format='%.5f')
        wf.data.to_json(os.path.join(path, f'{data_fname}.json'))
        wf.to_nc(path=os.path.join(path, f'{data_fname}.nc'))
        wf.to_pkl(path_pkl=os.path.join(path, f'{data_fname}.pkl'))

    def __create_columns_Kd(self, wf):
        """
        Private method.
        Create parameters in WaterFrame

        Parameters
        ----------
            wf: Mooda waterframe object
                Waterframe with data

        """
        wf.data['KD_CLEAR'] = np.nan
        wf.vocabulary['KD_CLEAR'] = {'units': "1/m",
                                     'long_name': "diffuse attenuation coefficient"}
        wf.data['KD_CLEAR_QC'] = 0
        wf.data['KD_RED'] = np.nan
        wf.vocabulary['KD_RED'] = {'units': "1/m",
                                   'long_name': "diffuse attenuation coefficient"}
        wf.data['KD_RED_QC'] = 0
        wf.data['KD_GREEN'] = np.nan
        wf.vocabulary['KD_GREEN'] = {'units': "1/m",
                                     'long_name': "diffuse attenuation coefficient"}
        wf.data['KD_GREEN_QC'] = 0
        wf.data['KD_BLUE'] = np.nan
        wf.vocabulary['KD_BLUE'] = {'units': "1/m",
                                    'long_name': "diffuse attenuation coefficient"}
        wf.data['KD_BLUE_QC'] = 0
        wf.data['R2_CLEAR'] = np.nan
        wf.vocabulary['R2_CLEAR'] = {'units': "None",
                                     'long_name': "coefficient of determination"}
        wf.data['R2_CLEAR_QC'] = 0
        wf.data['R2_RED'] = np.nan
        wf.vocabulary['R2_RED'] = {'units': "None",
                                   'long_name': "coefficient of determination"}
        wf.data['R2_RED_QC'] = 0
        wf.data['R2_GREEN'] = np.nan
        wf.vocabulary['R2_GREEN'] = {'units': "None",
                                     'long_name': "coefficient of determination"}
        wf.data['R2_GREEN_QC'] = 0
        wf.data['R2_BLUE'] = np.nan
        wf.vocabulary['R2_BLUE'] = {'units': "None",
                                    'long_name': "coefficient of determination"}
        wf.data['R2_BLUE_QC'] = 0

    def __create_columns_Kd_multispectral(self, wf):
        """
        Private method.
        Create parameters in WaterFrame

        Parameters
        ----------
            wf: Mooda waterframe object
                Waterframe with data

        """
        wf.data['KD_CLEAR'] = np.nan
        wf.vocabulary['KD_CLEAR'] = {'units': "1/m"}
        wf.data['KD_CLEAR_QC'] = 0
        wf.data['KD_RED'] = np.nan
        wf.vocabulary['KD_RED'] = {'units': "1/m"}
        wf.data['KD_RED_QC'] = 0
        wf.data['KD_ORANGE'] = np.nan
        wf.vocabulary['KD_ORANGE'] = {'units': "1/m"}
        wf.data['KD_ORANGE_QC'] = 0
        wf.data['KD_YELLOW'] = np.nan
        wf.vocabulary['KD_YELLOW'] = {'units': "1/m"}
        wf.data['KD_YELLOW_QC'] = 0
        wf.data['KD_GREEN'] = np.nan
        wf.vocabulary['KD_GREEN'] = {'units': "1/m"}
        wf.data['KD_GREEN_QC'] = 0
        wf.data['KD_BLUE'] = np.nan
        wf.vocabulary['KD_BLUE'] = {'units': "1/m"}
        wf.data['KD_BLUE_QC'] = 0
        wf.data['KD_VIOLET'] = np.nan
        wf.vocabulary['KD_VIOLET'] = {'units': "1/m"}
        wf.data['KD_VIOLET_QC'] = 0
        wf.data['R2_CLEAR'] = np.nan
        wf.data['R2_CLEAR_QC'] = 0
        wf.data['R2_RED'] = np.nan
        wf.data['R2_RED_QC'] = 0
        wf.data['R2_ORANGE'] = np.nan
        wf.data['R2_ORANGE_QC'] = 0
        wf.data['R2_YELLOW'] = np.nan
        wf.data['R2_YELLOW_QC'] = 0
        wf.data['R2_GREEN'] = np.nan
        wf.data['R2_GREEN_QC'] = 0
        wf.data['R2_BLUE'] = np.nan
        wf.data['R2_BLUE_QC'] = 0
        wf.data['R2_VIOLET'] = np.nan
        wf.data['R2_VIOLET_QC'] = 0

    def __calculate_kd(self, wf, match, index, depths, column_name_Kd, column_name_R2):
        """
        Private method.
        Calculate Kd and R2 from waterframe data

        Parameters
        ----------
            wf: Mooda waterframe object
                Waterframe with data

            match: list
                Lists with parameters name

            index: Pandas Timestamp
                The index of the row

            depths: numpy array
                Array with depths needed to calculate Kd

            column_name_Kd: str
                Name of Kd column

            column_name_R2: str
                Name of R2 column

        """
        # Get elements of row
        row = wf.data.loc[index, match].tolist()
        # Calulate log of values
        with np.errstate(divide='ignore'):
            row = np.log(row)
        # Get indices where element is Nan or Infinite
        indices = [i for i, s in enumerate(row) if np.isnan(s) or np.isinf(s)]

        # Delete null elements from lists
        row = np.delete(row, indices).tolist()
        depths_row = np.delete(depths, indices).tolist()

        # Calculate Kd from linear regression
        try:
            slope, intercept, r_value, _p_value, _std_err = stats.linregress(
                depths_row, row)

            if self.doc['r2'] is not None:
                if r_value**2 >= self.doc['r2']:
                    wf.data.at[index, column_name_Kd] = slope * (-1)
                    wf.data.at[index, column_name_R2] = r_value**2

                else:
                    wf.data.at[index, column_name_Kd] = np.nan
                    wf.data.at[index, column_name_R2] = np.nan
            else:
                wf.data.at[index, column_name_Kd] = slope * (-1)
                wf.data.at[index, column_name_R2] = r_value**2

        except ValueError as er:
            wf.data.at[index, column_name_Kd] = np.nan
            wf.data.at[index, column_name_R2] = np.nan

    def __multiindex_wf(self, wf, depths):
        """
        Private method.
        Create multiindex in WaterFrame

        Parameters
        ----------
            wf: Mooda WaterFrame object
                WaterFrame with data

            depths: numpy array
                Lists with depths needed to create index
        Returns
        -------
            wf_mi: Mooda WaterFrame object
                New WaterFrame with multiindex
        """
        # Create index with depth and time. Convert time and depths to list
        times = wf.data.index.tolist()
        # Convert numpy array of depths in correct format
        depths_list = ['%.2f' % i for i in depths]

        # Create parameters
        param_red = 'RED'
        param_green = 'GREEN'
        param_blue = 'BLUE'
        param_clear = 'CLEAR'

        # Set name of QC parameters
        param_red_qc = 'RED_QC'
        param_green_qc = 'GREEN_QC'
        param_blue_qc = 'BLUE_QC'
        param_clear_qc = 'CLEAR_QC'

        time_column = "TIME"
        depth_column = "DEPTH"
        parameters = [param_red, param_green, param_blue, param_clear]
        parameters_qc = [param_red_qc, param_green_qc, param_blue_qc, param_clear_qc]

        # Create Pandas Multiindex
        multi_index = pd.MultiIndex.from_product([depths_list, times], names=['DEPTH', 'TIME'])
        df = pd.DataFrame(index=multi_index, columns=parameters + parameters_qc)

        # Creation of new WaterFrame
        wf_mi = md.WaterFrame()

        # Copy data to WaterFrame
        wf_mi.data = df

        # Copy metadata to WaterFrame
        wf_mi.metadata = wf.metadata

        # Create vocabulary
        wf_mi.vocabulary[param_red] = {'units': "counts"}
        wf_mi.vocabulary[param_green] = {'units': "counts"}
        wf_mi.vocabulary[param_blue] = {'units': "counts"}
        wf_mi.vocabulary[param_clear] = {'units': "counts"}

        # Create columns Kd
        # self.__create_columns_Kd(wf_mi)

        # Iterate over each row of data from waterframe
        for index, _row in wf.data.iterrows():
            for depth in depths_list:
                for param in parameters:
                    col = f"{param}_{depth}"
                    wf_mi.data.loc[(depth, index), param] = _row[col]

        return wf_mi

    def analysis_kduino(self, path):
        """
        Function to read configuration in properties file and
        analyse data from KdUINO to get Kd and r2
        """
        # TODO names of files in data:
        # kduino(always)_country_place_description(test,fieldcampaign,lake,shore,sea,deployment_number)_device-name_data
        # script to obtain mooda waterframe, with all the columns, metadata. Save this waterframe as pickle
        # finally to upload in zenodo
        if self.doc["device"] == "kdupro_rgb" or self.doc["device"] == "kdupro_rgb_v1":
            print("KduPRO")

            # Get all the starts - ends configured in properties
            starts = [starts for starts in self.doc["starts"]]
            ends = [ends for ends in self.doc["ends"]]

            # Get path from properties

            #path = self.doc["path"]

            if len(starts) == len(ends):

                # Obtain all files from path
                filename_list = [
                    filename for filename in glob.glob(
                        os.path.join(path, '*.txt'))]
                #import pdb; pdb.set_trace()

                if not filename_list:
                    print("Path contains 0 files to analyse. Check your properties file")
                    exit()

                # Convert all files to waterframes and save it in a list
                waterframe_list = [
                    self.__file_kdupro_rgb_to_wf(filename) for filename in filename_list]

                if all(wf is None for wf in waterframe_list):
                    print("Path contains 0 files well formated to analyse. Check your files")
                    exit()

                # for each start and end time
                for start, end in zip(starts, ends):

                    print('')
                    print('New period')
                    print('----------')
                    print(f'Start: \t{start}')
                    print(f'End: \t{end}')

                    # Declare lists
                    names = []
                    depths = []

                    # Create unique waterframe
                    wf_all = md.WaterFrame()

                    # Concat all waterframes
                    for index, wf in enumerate(waterframe_list):
                        if index == 0:
                            wf_all = wf.copy()
                        else:
                            # Concat data
                            try:
                                wf_all.data = pd.concat([wf_all.data, wf.data], axis=1)
                                # Add metadata
                                wf_all.metadata = self.__merge_metadata(wf.metadata, wf_all.metadata)
                                # Add vocabulary
                                for param in wf.parameters:
                                    wf_all.vocabulary[param] = wf.vocabulary[param]
                            except ValueError as er:
                                print(f"Problems in concat wf with this wf: {wf.parameters}")
                                pass
                            except AttributeError as er:
                                print(f"Problems in concat wf. {er}")
                                pass

                    # Append names and depths to each list
                    for wf in waterframe_list:
                        if wf is None:
                            pass
                        else:
                            name = wf.metadata["name"]
                            names.append(name)
                            depth = wf.metadata["depth"]
                            depths.append(depth)

                    # Resample time
                    try:
                        wf_all.resample(self.doc["resample"])
                    except ValueError as er:
                        print("Incorrect frequency of resample. Check your properties file")
                        exit()

                    # Slice time
                    mask = (wf_all.data.index >= start) & (wf_all.data.index <= end)
                    wf_all.data = wf_all.data.loc[mask]

                    if wf_all.data.empty:
                        print("Incorrect starts and ends. Check your properties file")
                        exit()

                    # Shift time
                    shift = self.doc["shift"]
                    # Check if all values are None in shift dictionary. If not, shift time
                    is_None_shift = all(x is None for x in shift.values())

                    if is_None_shift:
                        pass
                    else:
                        # Shift time in data of waterframe
                        try:
                            wf_all.data.shift(shift['time'], freq=shift['freq'])
                        except TypeError:
                            print("Incorrect shift time. Check your properties file")
                            exit()

                    # Discard elements from data
                    disc_elem = self.doc["discard_items"]
                    if disc_elem is not None:
                        try:
                            wf_all.data = wf_all.data.mask(wf_all.data < disc_elem, 0)
                        except TypeError as er:
                            print("Incorrect discard elements. Check your properties file")
                            exit()

                    # Convert depths list elements to float, and save it as a numpy array
                    depths = np.array(list(map(float, depths)))

                    # Save all data
                    #self.__save_data(f"all_data_{start}_{end}", wf_all)

                    # Save CLEAR data in one new waterframe
                    wf_clear = md.WaterFrame()
                    wf_clear.metadata = wf_all.metadata
                    wf_clear.vocabulary = wf_all.vocabulary
                    match_CLEAR = [s for s in wf_all.data if ("CLEAR_" in s) and ("QC" not in s)]
                    wf_clear.data = wf_all.data.filter(match_CLEAR)
                    #self.__save_data(f"clear_data_{start}_{end}", wf_clear)

                    # Create columns Kd and R2
                    wf_all.vocabulary = {}
                    self.__create_columns_Kd(wf_all)

                    # Create lists with parameters name
                    match_CLEAR = [s for s in wf_all.data if ("CLEAR_" in s) and ("QC" not in s)]
                    match_RED = [s for s in wf_all.data if ("RED_" in s) and ("QC" not in s)]
                    match_GREEN = [s for s in wf_all.data if ("GREEN_" in s) and ("QC" not in s)]
                    match_BLUE = [s for s in wf_all.data if ("BLUE_" in s) and ("QC" not in s)]

                    # Iterate over each row of data
                    for index, _row in wf_all.data.iterrows():
                        # Call function to calculate Kd
                        # CLEAR
                        self.__calculate_kd(
                            wf_all, match_CLEAR, index, depths, column_name_Kd='KD_CLEAR', column_name_R2='R2_CLEAR')
                        # RED
                        self.__calculate_kd(
                            wf_all, match_RED, index, depths, column_name_Kd='KD_RED', column_name_R2='R2_RED')
                        # GREEN
                        self.__calculate_kd(
                            wf_all, match_GREEN, index, depths, column_name_Kd='KD_GREEN', column_name_R2='R2_GREEN')
                        # BLUE
                        self.__calculate_kd(
                            wf_all, match_BLUE, index, depths, column_name_Kd='KD_BLUE', column_name_R2='R2_BLUE')

            else:
                print("Different number of starts and ends. Check your properties file")
                exit()

            # Save all data with values, Kd and R2
            #self.__save_data(f"data_{start}_{end}", wf_all)

            # Create new waterframe to save Kd and R2
            wf_kd = md.WaterFrame()
            wf_kd.metadata = wf_all.metadata
            wf_kd.vocabulary = wf_all.vocabulary
            match_Kd = [s for s in wf_all.data if (("KD_" in s) or ("R2_" in s)) and ("QC" not in s)]
            wf_kd.data = wf_all.data.filter(match_Kd)
            #self.__save_data(f"Kd_{start}_{end}", wf_kd)
            
            return wf_all, wf_kd

            """# Create new waterframe with multiindex: Time and Depth
            wf_mi = self.__multiindex_wf(wf_all, depths)
            # Save new WaterFrame with multiindex
            self.__save_data(f"multiindex_data_{start}_{end}", wf_mi)"""

        if self.doc["device"] == "kdustick":

            # Get all the starts - ends configured in properties
            starts = [starts for starts in self.doc["starts"]]
            ends = [ends for ends in self.doc["ends"]]

            # Get path from properties
            # path = self.doc["path"]

            if len(starts) == len(ends):

                # Obtain all files from path
                #import pdb; pdb.set_trace()
                
                filename = glob.glob(os.path.join(path, 'data.txt'))[0]

                if not filename:
                    print("Path contains 0 files to analyse. Check your properties file")
                    exit()

                # Convert all files to waterframes and save it in a list
                wf = self.__file_kdustick_to_wf(filename)

                # for each start and end time
                for start, end in zip(starts, ends):

                    print('')
                    print('New period')
                    print('----------')
                    print(f'Start: \t{start}')
                    print(f'End: \t{end}')

                    # Slice time
                    mask = (wf.data.index >= start) & (wf.data.index <= end)
                    wf.data = wf.data.loc[mask]

                    if wf.data.empty:
                        print("Incorrect starts and ends. Check your properties file")
                        exit()

                if wf is None:
                    print("Path contains 0 files well formated to analyse. Check your files")
                    exit()

                # Save all data
                #self.__save_data(f"all_data_{start}_{end}", wf)
                return wf

        if self.doc["device"] == "kdupro_multispectral":

            # Get all the starts - ends configured in properties
            starts = [starts for starts in self.doc["starts"]]
            ends = [ends for ends in self.doc["ends"]]

            # Get path from properties
            #path = self.doc["path"]

            if len(starts) == len(ends):

                # Obtain all files from path
                filename_list = [
                    filename for filename in glob.glob(
                        os.path.join(path, '*.txt'))]

                if not filename_list:
                    print("Path contains 0 files to analyse. Check your properties file")
                    exit()

                # Convert all files to waterframes and save it in a list
                waterframe_list = [
                    # self.__file_kdupro_rgb_to_wf(filename) for filename in filename_list]
                    self.__file_kdupro_multispectral_to_wf(filename) for filename in filename_list]

                if all(wf is None for wf in waterframe_list):
                    print("Path contains 0 files well formated to analyse. Check your files")
                    exit()

                # for each start and end time
                for start, end in zip(starts, ends):

                    print('')
                    print('New period')
                    print('----------')
                    print(f'Start: \t{start}')
                    print(f'End: \t{end}')

                    # Declare lists
                    names = []
                    depths = []

                    # Create unique waterframe
                    wf_all = md.WaterFrame()

                    # Concat all waterframes
                    for index, wf in enumerate(waterframe_list):
                        if index == 0:
                            wf_all = wf.copy()
                        else:
                            # Concat data
                            try:
                                wf_all.data = pd.concat([wf_all.data, wf.data], axis=0)
                                # Add metadata
                                wf_all.metadata = self.__merge_metadata(wf.metadata, wf_all.metadata)
                                # Add vocabulary
                                for param in wf.parameters:
                                    wf_all.vocabulary[param] = wf.vocabulary[param]
                            except ValueError as er:
                                print(f"Problems in concat wf with this wf: {wf.parameters}")
                                pass
                            except AttributeError as er:
                                print(f"Problems in concat wf. {er}")
                                pass

                    # Rename columns
                    wf_all.data.rename(columns={"450": "RED", "500": "ORANGE",
                                                "550": "YELLOW",  "570": "GREEN",
                                                "600": "BLUE", "650": "VIOLET"}, inplace=True)

                    # Slice time
                    mask = (wf_all.data.index >= start) & (wf_all.data.index <= end)
                    wf_all.data = wf_all.data.loc[mask]

                    if wf_all.data.empty:
                        print("Incorrect starts and ends. Check your properties file")
                        exit()

                    # Set multiindex
                    wf_all.data.reset_index(inplace=True)
                    wf_all.data.set_index(["TIME", "DEPTH"], inplace=True)

                    # Obtain depths
                    depths = wf_all.data.index.get_level_values('DEPTH').unique()

                    # Discard elements from data
                    disc_elem = self.doc["discard_items"]
                    if disc_elem is not None:
                        try:
                            wf_all.data = wf_all.data.mask(wf_all.data < disc_elem, 0)
                        except TypeError as er:
                            print("Incorrect discard elements. Check your properties file")
                            exit()

                    # Create parameters
                    param_red = 'RED'
                    param_orange = 'ORANGE'
                    param_yellow = 'YELLOW'
                    param_green = 'GREEN'
                    param_blue = 'BLUE'
                    param_violet = 'VIOLET'

                    # Set name of QC parameters
                    param_red_qc = 'RED_QC'
                    param_orange_qc = 'ORANGE_QC'
                    param_yellow_qc = 'YELLOW_QC'
                    param_green_qc = 'GREEN_QC'
                    param_blue_qc = 'BLUE_QC'
                    param_violet_qc = 'VIOLET_QC'

                    parameters = [param_red, param_orange, param_yellow, param_green, param_blue, param_violet]
                    parameters_qc = [param_red_qc, param_orange_qc, param_yellow_qc, param_green_qc, param_blue_qc,
                                     param_violet_qc]

                    wf_all.data[[parameters_qc]] = 0

                    # Create vocabulary
                    wf_all.vocabulary[param_red] = {'units': "counts"}
                    wf_all.vocabulary[param_orange] = {'units': "counts"}
                    wf_all.vocabulary[param_yellow] = {'units': "counts"}
                    wf_all.vocabulary[param_green] = {'units': "counts"}
                    wf_all.vocabulary[param_blue] = {'units': "counts"}
                    wf_all.vocabulary[param_violet] = {'units': "counts"}

                    # Create columns Kd
                    self.__create_columns_Kd_multispectral(wf_all)

                    # Save all data
                    #self.__save_data(f"all_data_{start}_{end}", wf_all)
                    return wf_all

                    wf_all.data.reset_index().pivot('TIME', 'DEPTH').plot()
                    # wf_all.data.plot()
                    # plt.show()

                    """ fig = wf_all.iplot_timeseries(parameters_to_plot="RED")
                    go.Figure(fig).show()
                    wf_all.data[["RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "VIOLET"]].plot()
                    plt.show()

                    # Save CLEAR data in one new waterframe
                    wf_clear = md.WaterFrame()
                    wf_clear.metadata = wf_all.metadata
                    wf_clear.vocabulary = wf_all.vocabulary
                    match_CLEAR = [s for s in wf_all.data if ("CLEAR" in s) and ("QC" not in s)]
                    wf_clear.data = wf_all.data.filter(match_CLEAR)
                    self.__save_data(f"clear_data_{start}_{end}", wf_clear)

                    # Create columns Kd and R2
                    self.__create_columns_Kd(wf_all)

                    # Create lists with parameters name
                    match_CLEAR = [s for s in wf_all.data if ("CLEAR" in s) and ("QC" not in s)]
                    match_RED = [s for s in wf_all.data if ("RED" in s) and ("QC" not in s)]
                    match_GREEN = [s for s in wf_all.data if ("GREEN" in s) and ("QC" not in s)]
                    match_BLUE = [s for s in wf_all.data if ("BLUE" in s) and ("QC" not in s)]

                    # Iterate over each row of data
                    for index, _row in wf_all.data.iterrows():
                        # Call function to calculate Kd
                        # CLEAR
                        self.__calculate_kd(
                            wf_all, match_CLEAR, index, depths, column_name_Kd='KD_CLEAR', column_name_R2='R2_CLEAR')
                        # RED
                        self.__calculate_kd(
                            wf_all, match_RED, index, depths, column_name_Kd='KD_RED', column_name_R2='R2_RED')
                        # GREEN
                        self.__calculate_kd(
                            wf_all, match_GREEN, index, depths, column_name_Kd='KD_GREEN', column_name_R2='R2_GREEN')
                        # BLUE
                        self.__calculate_kd(
                            wf_all, match_BLUE, index, depths, column_name_Kd='KD_BLUE', column_name_R2='R2_BLUE') """

            else:
                print("Different number of starts and ends. Check your properties file")
                exit()

    def __plot_timeseries(self, parameters_to_plot=None, qc_flags=None, rolling_window=None, ax=None,
                          average_time=None, secondary_y=None, color=None):
        """
        Plot the input parameters with time on X and the parameters on Y. It calculates the
        standar deviation of a rolling window and plot it.

        Parameters
        ----------
            parameters_to_plot: list of str, str, optional (parameters_to_plot = None)
                Parameters of the WaterFrame to plot. If parameters_to_plot is None, all parameters
                will be ploted.
            qc_flags: list of int, optional (qc_flags = None)
                QC flags of the parameters to plot. If qc_flags in None, all QC flags will be used.
            rolling_window: int, optional (rolling_window = None)
                Size of the moving window. It is the number of observations
                used for calculating the statistic.
            ax: matplotlib.axes object, optional (ax = None)
                It is used to add the plot to an input axes object.
            average_time: str, optional (average_time = None)
                It calculates an average value of a time interval. You can find
                all of the resample options here:
                http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
            secondary_y: bool, optional (secondary_y = False)
                Plot on the secondary y-axis.
            color: str or list of str, optional (color = None)
                Any matplotlib color. It will be applied to the traces.
        Returns
        -------
            ax: matplotlib.AxesSubplot
                Axes of the plot.
        """
        # to comment
        self = self.wf

        def make_plot(df_in, parameter_name, ax_in, color_in, rolling_in):
            """
            It makes the graph.

            Parameters
            ----------
                df_in: pandas.DataFrame
                    It contains the info to plot.
                parameter_name: str
                    Name of the parameter to plot.
                ax_in: matplotlib.axes
                    Axes to add the plot.
                color_in: str
                    Color of the line.
                rolling_in: int
                    Size of the rolling window to calculate the mean and standar deviation.

            Returns
            -------
                ax_out: matplotlib.axes
                    Axes with the plot.
            """
            # Calculation of the std and the mean
            roll = df_in[parameter_name].rolling(rolling_in, center=True)
            m = roll.agg(['mean', 'std'])
            # rename 'mean' column
            m.rename(columns={'mean': parameter_name}, inplace=True)
            m.dropna(inplace=True)
            ax_out = m[parameter_name].plot(ax=ax_in, secondary_y=secondary_y, legend=True,
                                            color=color_in)
            ax_out.fill_between(m.index, m[parameter_name] - m['std'], m[parameter_name] + m['std'],
                                alpha=.25, color=color_in)
            ax_out.legend([f"{parameter_name} at depth: {df_in['DEPTH'].mean()}"])
            # Write axes
            try:
                ax_out.set_ylabel(self.vocabulary[parameter_name]['units'])
            except KeyError:
                # No units
                pass

            return ax_out

        if parameters_to_plot is None:
            parameters_to_plot = self.parameters
        elif isinstance(parameters_to_plot, str):
            parameters_to_plot = [parameters_to_plot]

        # Extract data
        # Dropna is necessary?
        df = self.data[parameters_to_plot].dropna().reset_index()
        # df = self.data[parameters_to_plot].dropna().reset_index().set_index('TIME')
        # Float type
        df[parameters_to_plot] = df[parameters_to_plot].astype(np.float)
        df['DEPTH'] = df['DEPTH'].astype(np.float)
        # Group by
        df = df.groupby(['DEPTH', 'TIME'])[parameters_to_plot].mean()
        df.reset_index(inplace=True)
        df.set_index('TIME', inplace=True)

        for _, df_depth in df.groupby('DEPTH'):
            df_depth.index.rename("Date", inplace=True)
            df_depth.sort_index(inplace=True)

            # Resample data
            if average_time is None:
                pass
            else:
                df_depth = df_depth.resample(average_time).mean()

            # Calculation of the rolling value
            if rolling_window is None:
                if df_depth.size <= 100:
                    rolling_window = 1
                elif df_depth.size <= 1000:
                    rolling_window = df_depth.size//10
                elif df_depth.size <= 10000:
                    rolling_window = df_depth.size // 100
                else:
                    rolling_window = df_depth.size // 1000

            if color is None:
                for parameter_to_plot in parameters_to_plot:
                    ax = make_plot(df_depth, parameter_to_plot, ax, "blue", rolling_window)
            else:
                for parameter_to_plot, color_to_plot in zip(parameters_to_plot, color):
                    ax = make_plot(df_depth, parameter_to_plot, ax, color_to_plot, rolling_window)

        return ax

    def plot_kduino(self, path):
        """
        Private method.
        Function to plot KdUINO analysis
        """
        plot_list = self.doc["analysis"]["plot"]

        # If there is any plot
        if plot_list:

            if self.doc["device"] == "kdupro_rgb" or self.doc["device"] == "kdupro_rgb_v1":

                # If we do cumulative analysis
                if self.doc['cumulative'] is True:
                    path = os.path.join(path, 'files', 'cumulative/')
                # If we don't do cumulative analysis
                else:
                    path = os.path.join(path, 'files', 'non_cumulative/')

                # Get data.pkl file
                pkl_files = [f for f in os.listdir(path) if (f.endswith('.pkl')) and (f.startswith('Kd'))]

                for data_file in pkl_files:
                    # Load waterframe
                    wf = md.read_pkl(os.path.join(path, data_file))

                    wf_plot = md.WaterFrame()
                    wf_plot.metadata = wf.metadata
                    wf_plot.vocabulary = wf.vocabulary

                    wf.data = wf.data.rolling(3).mean()

                    match_CLEAR = [s for s in wf.data if ("CLEAR" in s) and ("QC" not in s)]
                    wf_plot.data[match_CLEAR] = wf.data.filter(match_CLEAR)

                    match_RED = [s for s in wf.data if ("RED" in s) and ("QC" not in s)]
                    wf_plot.data[match_RED] = wf.data.filter(match_RED)

                    match_GREEN = [s for s in wf.data if ("GREEN" in s) and ("QC" not in s)]
                    wf_plot.data[match_GREEN] = wf.data.filter(match_GREEN)

                    match_BLUE = [s for s in wf.data if ("BLUE" in s) and ("QC" not in s)]
                    wf_plot.data[match_BLUE] = wf.data.filter(match_BLUE)

                    avgKd = wf.data.loc[wf_plot.data['R2_CLEAR'] > 0.9, 'KD_CLEAR'].mean()
                    #print("Average Kd PAR for samples with r2 > 0.9: {}".format(np.around(avgKd, 3)))

                    avgKd = wf.data.loc[wf_plot.data['R2_RED'] > 0.9, 'KD_RED'].mean()
                    #print("Average Kd RED for samples with r2 > 0.9: {}".format(np.around(avgKd, 3)))

                    avgKd = wf.data.loc[wf_plot.data['R2_GREEN'] > 0.9, 'KD_GREEN'].mean()
                    #print("Average Kd GREEN for samples with r2 > 0.9: {}".format(np.around(avgKd, 3)))

                    avgKd = wf.data.loc[wf_plot.data['R2_BLUE'] > 0.9, 'KD_BLUE'].mean()
                    #print("Average Kd BLUE for samples with r2 > 0.9: {}".format(np.around(avgKd, 3)))

                    fig, ax = plt.subplots()
                    twin1 = ax.twinx()

                    twin1.set_ylabel('$r^2$')
                    ax.set_ylabel('$K_d$ ($m^{-1}$)')

                    ax.set_xlabel("Time (minutes)")

                    ax.tick_params(axis='x', labelsize=8)

                    p1, = ax.plot(wf_plot.data['KD_CLEAR'], color="black", linestyle='-',
                                  label="$K_d$ PAR")

                    p1R, = ax.plot(wf_plot.data['KD_RED'], color="red", linestyle='-',
                                   label="$K_d$ red")

                    p1G, = ax.plot(wf_plot.data['KD_GREEN'], color="green", linestyle='-',
                                   label="$K_d$ green")

                    p1B, = ax.plot(wf_plot.data['KD_BLUE'], color="blue", linestyle='-',
                                   label="$K_d$ blue")

                    p2, = twin1.plot(wf_plot.data['R2_CLEAR'], color="peru", linestyle='--', label="$r^2$")

                    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

                    # Puts x-axis labels on an angle
                    ax.xaxis.set_tick_params(rotation=45)
                    ax.tick_params(axis='x', labelsize=8)
                    twin1.set_ylim([0, 1.05])

                    max_value = wf_plot.data[['KD_CLEAR', 'KD_RED', 'KD_GREEN', 'KD_BLUE']].max().max()
                    ax.set_ylim([0, max_value])

                    ax.legend(handles=[p1, p1R, p1G, p1B, p2],
                              bbox_to_anchor=(1.04, 1),
                              loc='upper left',
                              borderaxespad=1.,
                              ncol=1,
                              fontsize=10,
                              title_fontsize=10,
                              prop={'size': 10}
                              )
                    fig.tight_layout()
                    # plt.show()
                    plt.savefig(os.path.join(path, 'plot.png'), dpi=300)
                    #return path

                    """ for elem_plot in plot_list:
                        if elem_plot == 'timeseries_individual':
                            print(wf.parameters)
                            exit()
                            fig = wf.iplot_timeseries(parameters_to_plot="KD_CLEAR")
                            go.Figure(fig).show()
                            exit()
                            print("timeseries_individual")
                        if elem_plot == 'timeseries_buoy':
                            print("timeseries_buoy")
                        if elem_plot == 'histogram':
                            print("histogram")
                        if elem_plot == 'max_diff':
                            print("max_diff")
                        if elem_plot == 'scatter_matrix':
                            print("scatter_matrix")
                        if elem_plot == 'correlation_resample':
                            print("correlation_resample")
                        if elem_plot == 'kd':
                            print("kd") """

            if self.doc["device"] == "kdustick":
                # If we do cumulative analysis
                if self.doc['cumulative'] is True:
                    path = os.path.join(path, 'files', 'cumulative/')
                # If we don't do cumulative analysis
                else:
                    path = os.path.join(path, 'files', 'non_cumulative/')

                # Get data.pkl file
                pkl_files = [f for f in os.listdir(path) if (f.endswith('.pkl'))]

                for data_file in pkl_files:
                    # Load waterframe
                    wf = md.read_pkl(os.path.join(path, data_file))

                    wf_plot = md.WaterFrame()
                    wf_plot.metadata = wf.metadata
                    wf_plot.vocabulary = wf.vocabulary

                    wf_plot.data = wf.data

                    fig, ax = plt.subplots()
                    twin1 = ax.twinx()

                    twin1.set_ylabel('$r^2$')
                    ax.set_ylabel('$K_d$ ($m^{-1}$)')

                    ax.set_xlabel("Time (minutes)")

                    ax.tick_params(axis='x', labelsize=8)

                    p1, = ax.plot(wf_plot.data['kd_clear'], color="black", linestyle='-',
                                  label="$K_d$ PAR")

                    p1R, = ax.plot(wf_plot.data['kd_red'], color="red", linestyle='-',
                                   label="$K_d$ red")

                    p1G, = ax.plot(wf_plot.data['kd_green'], color="green", linestyle='-',
                                   label="$K_d$ green")

                    p1B, = ax.plot(wf_plot.data['kd_blue'], color="blue", linestyle='-',
                                   label="$K_d$ blue")

                    p2, = twin1.plot(wf_plot.data['r_squared_clear'], color="peru", linestyle='--', label="$r^2$")

                    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

                    # Puts x-axis labels on an angle
                    ax.xaxis.set_tick_params(rotation=45)
                    ax.tick_params(axis='x', labelsize=8)
                    twin1.set_ylim([0, 1.05])

                    max_value = wf_plot.data[['kd_clear', 'kd_red', 'kd_green', 'kd_blue']].max().max()
                    min_value = wf_plot.data[['kd_clear', 'kd_red', 'kd_green', 'kd_blue']].min().min()
                    ax.set_ylim([min_value, max_value])

                    ax.legend(handles=[p1, p1R, p1G, p1B, p2],
                              bbox_to_anchor=(1.04, 1),
                              loc='upper left',
                              borderaxespad=1.,
                              ncol=1,
                              fontsize=10,
                              title_fontsize=10,
                              prop={'size': 10}
                              )
                    fig.tight_layout()
                    # plt.show()
                    plt.savefig(os.path.join(path, 'plot.png'), dpi=300)
                    return plt

        else:
            print("Not plot analysis to do. Check your properties file")
            exit()

    def from_csv_to_wf(self):
        """

        """
        wf_all = md.WaterFrame()
        depths = []
        wf_all.data = pd.read_csv("data_buoy.csv", sep=";", index_col="TIME")

        # index to datetime
        wf_all.data.index = pd.to_datetime(wf_all.data.index)

        # insert depths manually
        depths = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0]
        depths = list(map(float, depths))

        # create QC param
        for param in wf_all.data:
            print(param)
            param_qc = param + "_QC"
            wf_all.data[param_qc] = 0

        # create lists with parameters name
        match_CLEAR = [s for s in wf_all.data if ("CLEAR" in s) and ("QC" not in s)]
        match_RED = [s for s in wf_all.data if ("RED" in s) and ("QC" not in s)]
        match_GREEN = [s for s in wf_all.data if ("GREEN" in s) and ("QC" not in s)]
        match_BLUE = [s for s in wf_all.data if ("BLUE" in s) and ("QC" not in s)]

        wf_all.data = np.log(wf_all.data)
        wf_all.data['KD_CLEAR'] = np.nan
        wf_all.data['KD_CLEAR_QC'] = 0
        wf_all.data['KD_RED'] = np.nan
        wf_all.data['KD_RED_QC'] = 0
        wf_all.data['KD_GREEN'] = np.nan
        wf_all.data['KD_GREEN_QC'] = 0
        wf_all.data['KD_BLUE'] = np.nan
        wf_all.data['KD_BLUE_QC'] = 0
        wf_all.data['R2_CLEAR'] = np.nan
        wf_all.data['R2_CLEAR_QC'] = 0
        wf_all.data['R2_RED'] = np.nan
        wf_all.data['R2_RED_QC'] = 0
        wf_all.data['R2_GREEN'] = np.nan
        wf_all.data['R2_GREEN_QC'] = 0
        wf_all.data['R2_BLUE'] = np.nan
        wf_all.data['R2_BLUE_QC'] = 0

        # resample
        wf_all.resample(self.doc["resample"])

        # slice time
        # mask = (wf_all.data.index >= start) & (wf_all.data.index <= end)
        # wf_all.data = wf_all.data.loc[mask]

        # shift time
        # wf_all.data.shift(7, freq='M')

        for index, _row in wf_all.data.iterrows():

            # CLEAR
            row_clear = wf_all.data.loc[index, match_CLEAR].values
            # get indices where element is Nan or Infinite
            indices = [i for i, s in enumerate(row_clear) if np.isnan(s) or np.isinf(s)]

            # delete null elements from lists
            row_clear = np.delete(row_clear, indices).tolist()
            depths_row_clear = np.delete(depths, indices).tolist()

            # calculate Kd from linear regression
            slope, intercept, r_value, _p_value, _std_err = stats.linregress(
                depths_row_clear, row_clear)

            if r_value**2 >= self.doc['r2']:
                wf_all.data.at[index, 'Kd_CLEAR'] = slope * (-1)
                wf_all.data.at[index, 'R2_CLEAR'] = r_value**2

                print(slope * (-1))
                print(r_value**2)
                print(index)

                depths_row_clear = np.array(depths_row_clear)
                row_clear = np.array(row_clear)

                # plot depths - values clear
                plt.plot(depths_row_clear, row_clear, marker='o', linestyle="")
                plt.plot(depths_row_clear, slope*depths_row_clear + intercept)

                plt.xlabel("Depth (m)")
                plt.ylabel("Light")

                # plt.show()
            else:
                wf_all.data.at[index, 'Kd_CLEAR'] = np.nan
                wf_all.data.at[index, 'R2_CLEAR'] = np.nan

            # RED
            row_red = wf_all.data.loc[index, match_RED].values
            # get indices where element is Nan or Infinite
            indices = [i for i, s in enumerate(row_red) if np.isnan(s) or np.isinf(s)]

            # delete null elements from lists
            row_red = np.delete(row_red, indices).tolist()
            depths_row_red = np.delete(depths, indices).tolist()

            # calculate Kd from linear regression
            slope, _intercept, r_value, _p_value, _std_err = stats.linregress(
                depths_row_red, row_red)
            wf_all.data.at[index, 'Kd_RED'] = slope * (-1)
            wf_all.data.at[index, 'R2_RED'] = r_value**2

            # GREEN
            row_green = wf_all.data.loc[index, match_GREEN].values
            # get indices where element is Nan or Infinite
            indices = [i for i, s in enumerate(row_green) if np.isnan(s) or np.isinf(s)]

            # delete null elements from lists
            row_green = np.delete(row_green, indices).tolist()
            depths_row_green = np.delete(depths, indices).tolist()

            # calculate Kd from linear regression
            slope, _intercept, r_value, _p_value, _std_err = stats.linregress(
                depths_row_green, row_green)
            wf_all.data.at[index, 'Kd_GREEN'] = slope * (-1)
            wf_all.data.at[index, 'R2_GREEN'] = r_value**2

            # BLUE
            row_blue = wf_all.data.loc[index, match_BLUE].values
            # get indices where element is Nan or Infinite
            indices = [i for i, s in enumerate(row_blue) if np.isnan(s) or np.isinf(s)]

            # delete null elements from lists
            row_blue = np.delete(row_blue, indices).tolist()
            depths_row_blue = np.delete(depths, indices).tolist()

            # calculate Kd from linear regression
            slope, _intercept, r_value, _p_value, _std_err = stats.linregress(
                depths_row_blue, row_blue)
            wf_all.data.at[index, 'Kd_BLUE'] = slope * (-1)
            wf_all.data.at[index, 'R2_BLUE'] = r_value**2

        wf_all.data.to_csv("data_loch_leven.csv", sep=';', float_format='%.4f')
        wf_all.to_nc("data_loch_leven.nc")
        wf_all.data.to_pickle("data_loch_leven.pkl")
