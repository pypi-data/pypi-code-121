import csv
import re
import os


def pull_hplc_area_from_csv(folder, report_name='Report'):
    """
    Pulls HPLC area data from the specified Agilent HPLC CSV report files.
    Returns the data tables for each wavelength in dictionary format.
    Each wavelength table is a dictionary with retention time: peak area format.

    Due to the unconventional way Agilent structures its CSV files pulling the data is
    a bit awkward. In essence, the report consists of one CSV files containing all the metadata,
    and further CSV files (one per detector signal) containing the data, but without
    column headers or other metadata. Thus, this function extracts bot data and
    metadata and stores them in the same format as the text based data parsing.

    :param folder: The folder to search for report files
    :param report_name: File name (without number or extension) of the report file

    :return: dictionary
        `dict[wavelength][retention time (float)][width/area/height]`

    """

    hplc_data = {}

    number_of_signals = 0
    signal_wavelengths = {}

    number_of_columns = 0
    column_headers = []
    column_units = []

    wavelength_pattern = re.compile('Sig=(\d+),')  # literal 'Sig=' followed by one or more digits followed by a comma

    metadata_file = os.path.join(folder, f'{report_name}00.CSV')

    # extract the metadata
    with open(metadata_file, newline='', encoding='utf-16') as f:
        # read CSV file into a list so we can iterate over it multiple times
        report = list(csv.reader(f))

        # find the number of signals
        for line in report:
            if line[0] == 'Number of Signals':
                number_of_signals = int(line[1])
                break

        # find the signal wavelengths and the associated signal number
        for signal_no in range(number_of_signals):
            for line in report:
                if line[0] == f'Signal {signal_no + 1}':
                    # use the RegEx capture group to conveniently extract the wavelength
                    wavelength = float(re.search(wavelength_pattern, line[1]).group(1))
                    signal_wavelengths[wavelength] = signal_no + 1

        # find the number of columns in the data files
        for line in report:
            if line[0] == 'Number of Columns':
                number_of_columns = int(line[1])
                break

        # find the column headers and units, currently unused, for future reference
        for header in range(number_of_columns):
            for line in report:
                if line[0] == f'Column {header + 1}':
                    column_headers.append(line[1].strip())
                    column_units.append(line[2].strip())

    # now iterate over the individual data files and extract the data
    for wavelength, signal_no in signal_wavelengths.items():
        hplc_data[wavelength] = {}

        # the data files are numbered, hopefully corresponding to the signal numbers
        data_file = os.path.join(folder, f'{report_name}0{signal_no}.CSV')

        with open(data_file, newline='', encoding='utf-16') as f:
            # this time the iterator is fine since we only need to go through once
            report = csv.reader(f)

            # munch through the lines and get the relevant data
            for line in report:
                retention_time = float(line[1])
                peak_width = float(line[3])
                peak_area = float(line[4])
                peak_height = float(line[5])

                hplc_data[wavelength][retention_time] = {
                    'width': peak_width,
                    'area': peak_area,
                    'height': peak_height
                }

    return hplc_data


def pull_metadata_from_csv(folder, report_name='Report'):
    """
    Pulls run metadata from the specified Agilent HPLC CSV report files.
    Returns the metadata describing the sample in dictionary format.

    :param folder: The folder to search for report files
    :param report_name: File name (without number or extension) of the report file

    :return: dictionary containing the metadata
    """

    metadata = {}

    metadata_file = os.path.join(folder, f'{report_name}00.CSV')

    # extract the metadata
    with open(metadata_file, newline='', encoding='utf-16') as f:
        # read CSV file into a list so we can iterate over it multiple times
        report = list(csv.reader(f))

        # find the number of signals
        for line in report:
            metadata[line[0]] = line[1]

    return metadata

