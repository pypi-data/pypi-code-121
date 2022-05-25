import re
from openpyxl import Workbook
import warnings
from typing import Union
import pathlib

# separator line
_header_block_re = re.compile(
    '[=]+\n'  # ==== block followed by newline
)

# regex for finding area reports
_area_report_re = re.compile(
    '[ ]+Area Percent Report'
)

# regex for splitting into signal tables
_signal_table_re = re.compile(
    'Signal \d: '
)

# regex for signal information line
_signal_info_re = re.compile(
    '(?P<signal>[A-Z0-9 ]+ \w), '  # usually DAD #
    'Sig=(?P<wavelength>[\d]+),[\d]* '  # signal wavelength
    'Ref=(?P<reference>[\w]+),*[\d]*'  # reference information
    '(?P<error>[a-z]*)*\n\n'  # error message
)
_column_re_dictionary = {  # regex matches for column and unit combinations
    'Peak': {  # peak index
        '#': '[ ]+(?P<Peak>[\d]+)',  # number
    },
    'RetTime': {  # retention time
        '[min]': '(?P<RetTime>[\d]+.[\d]+)',  # minutes
    },
    'Type': {  # peak type
        '': '(?P<Type>[A-Z]{1,2}(?: [A-Z]{1,2})*)',
    },
    'Width': {  # peak width
        '[min]': '(?P<Width>[\d]+.[\d]+[e+-]*[\d]+)',
    },
    'Area': {  # peak area
        '[mAU*s]': '(?P<Area>[\d]+.[\d]+[e+-]*[\d]+)',  # area units
        '%': '(?P<percent>[\d]+.[\d]+[e+-]*[\d]+)',  # percent
    },
    'Height': {  # peak height
        '[mAU]': '(?P<Height>[\d]+.[\d]+[e+-]*[\d]+)',
    },
    'Name': {
        '': '(?P<Name>[^\s]+(?:\s[^\s]+)*)',  # peak name
    },
}

# regex for a value centered in spaces
_value_re = re.compile('[ ]*(?P<value>[^\s]+)[ ]*')

# regex for catching no peaks in a report file
_no_peaks_re = re.compile(r'No peaks found')


def chunk_string(string, n_chars_list):
    """
    Chunks a string by n_characters, returning the characters and the remaining string

    :param str string: string to chunk
    :param lst n_chars_list: list of number of characters to return
    :return: chunk, remaining string
    """
    for index in n_chars_list:
        if len(string) == 0:
            yield ''
        chunk = string[:index]
        string = string[index:]  # there's always a space
        # print(f'"{chunk}", {index}, "{string}"')
        test = _value_re.match(chunk)
        if test is not None:
            yield test.group("value")
        else:
            yield ''


def build_peak_regex(signal_table: str):
    """
    Builds a peak regex from a signal table

    :param signal_table: block of lines associated with an area table
    :return: peak line regex object (<=3.6 _sre.SRE_PATTERN, >=3.7 re.Pattern)
    """
    split_table = signal_table.split('\n')
    if len(split_table) <= 4:  # catch peak table with no values
        return None
    # todo verify that these indicies are always true
    column_line = split_table[2]  # table column line
    unit_line = split_table[3]  # column unit line
    length_line = [len(val) + 1 for val in split_table[4].split('|')]   # length line

    # iterate over header values and units to build peak table regex
    peak_re_string = []
    for header, unit in zip(
        chunk_string(column_line, length_line),
        chunk_string(unit_line, length_line)
    ):
        if header == '':  # todo create a better catch for an undefined header
            continue
        try:
            peak_re_string.append(
                    _column_re_dictionary[header][unit]  # append the appropriate regex
            )
        except KeyError:  # catch for undefined regexes (need to be built)
            raise KeyError(f'The header/unit combination "{header}" "{unit}" is not defined in the peak regex '
                           f'dictionary. Let Lars know.')
    return re.compile(
        '[ ]+'.join(peak_re_string)  # constructed string delimited by 1 or more spaces
        + '[\s]*'  # and any remaining white space
    )


def pull_hplc_area_from_txt(filename):
    """
    Pulls HPLC area data from the specified Agilent HPLC output file
    Returns the data tables for each wavelength in dictionary format.
    Each wavelength table is a dictionary with retention time: peak area format.

    :param str filename: path to file
    :return: dictionary
        dict[wavelength][retention time (float)][Width/Area/Height/etc.]
    """

    with open(filename, 'r', encoding='utf-16') as openfile:
        text = openfile.read()
    return parse_area_report(text)


def parse_area_report(report_text: str) -> dict:
    """
    Interprets report text and parses the area report section, converting it to dictionary.

    :param report_text: plain text version of the report.
    :raises ValueError: if there are no peaks defined in the report text file
    :return: dictionary of signals in the form
        dict[wavelength][retention time (float)][Width/Area/Height/etc.]
    """
    if re.search(_no_peaks_re, report_text):  # There are no peaks in Report.txt
        raise ValueError(f'No peaks found in Report.txt')
    blocks = _header_block_re.split(report_text)
    signals = {}  # output dictionary
    for ind, block in enumerate(blocks):
        # area report block
        if _area_report_re.match(block):  # match area report block
            # break into signal blocks
            signal_blocks = _signal_table_re.split(blocks[ind + 1])
            # iterate over signal blocks
            for table in signal_blocks:
                si = _signal_info_re.match(table)
                if si is not None:
                    # some error state (e.g. 'not found')
                    if si.group('error') != '':
                        continue
                    wavelength = float(si.group('wavelength'))
                    if wavelength in signals:
                        # placeholder error raise just in case (this probably won't happen)
                        raise KeyError(
                            f'The wavelength {float(si.group("wavelength"))} is already in the signals dictionary')
                    signals[wavelength] = {}
                    # build peak regex
                    peak_re = build_peak_regex(table)
                    if peak_re is None:  # if there are no columns (empty table), continue
                        continue
                    for line in table.split('\n'):
                        peak = peak_re.match(line)
                        if peak is not None:
                            signals[wavelength][float(peak.group('RetTime'))] = {}
                            current = signals[wavelength][float(peak.group('RetTime'))]
                            for key in _column_re_dictionary:
                                if key in peak.re.groupindex:
                                    try:  # try float conversion, otherwise continue
                                        value = float(peak.group(key))
                                    except ValueError:
                                        value = peak.group(key)
                                    current[key] = value
                                else:  # ensures defined
                                    current[key] = None
    return signals


def pull_hplc_area(filename):
    """
    Legacy name for pull_hplc_area_from_txt

    :return: dictionary
        dict[wavelength][retention time (float)][width/area/height]
    """
    warnings.warn('This method has been refactored to pull_hplc_area_from_txt', DeprecationWarning, stacklevel=2)
    return pull_hplc_area_from_txt(filename)


def report_text_to_xlsx(target_file: Union[str, pathlib.Path], output_file: Union[str, pathlib.Path] = None) -> str or None:
    """
    Ingests the specified report text and outputs it to an excel file.

    :param target_file: path to target report text file
    :param output_file: path to output to (if not provided, it will be saved to "Report.xlsx" in the same directory
        as the report text file
    :return: path to the XLSX file that was written
    """
    try:
        pulled_report = pull_hplc_area_from_txt(target_file)
    except ValueError:    # No peaks in Report.txt
        raise ValueError(f'There were no peaks found in the target file "{target_file}"')

    if isinstance(target_file, pathlib.Path) is False:
        target_file = pathlib.Path(target_file)
    if target_file.is_absolute() is False:
        target_file = target_file.absolute()

    if output_file is None:
        output_file = target_file.parent / 'Report.xlsx'

    excel = Workbook()
    # ordered list of keys to write
    ordered_keys = [
        'Peak',
        'RetTime',
        'Type',
        'Width',
        'Area',
        'Height',
        'Name',
    ]

    # iterate through wavelengths
    for wavelength in pulled_report:
        # create a new sheet
        sheetname = f'{wavelength} nm'
        excel.create_sheet(sheetname)
        ws = excel[sheetname]

        # add header line
        ws.append(ordered_keys)
        # append retrieved retention times
        for ret in pulled_report[wavelength]:
            ws.append(
                [pulled_report[wavelength][ret][key] for key in ordered_keys]
            )

    # get rid of the default sheet
    if 'Sheet' in excel:
        excel.remove(excel['Sheet'])

    excel.save(output_file)

    return output_file

