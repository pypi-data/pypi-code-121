"""Batch data processing tools"""

import logging
import tqdm
from typing import Union
from hein_utilities.files import Watcher
from hein_utilities.misc import find_nearest, pad_list

from .time_course import HPLCTarget
from .sample import DADSignalInfo, HPLCSample
from ..ingestion.text import pull_hplc_area_from_txt, report_text_to_xlsx


def pull_hplc_data_from_folder(folder, targets, wiggle=0.01, watchfor='Report.TXT'):
    """
    Pulls the HPLC integrations for all report files within the specified directory.
    This function was designed to pull all data from a given day. This method only pulls data which exists in the reports,
    which can result in asymmetric data for timepoint analysis (i.e. it assumes that subsequent runs are unrelated to
    others). If the data in a folder are for time-course analysis, use
    :func:`~aghplctools.hplc.pull_hplc_data_from_folder_timepoint`.


    :param folder: The folder to search for report files
    :param targets: target dictionary of the form {'name': [wavelength, retention time], ...}

    :param wiggle: the wiggle time around retention times
    :param watchfor: the name of the report file to watch
    :return: dictionary of HPLCTarget instances in the format {'name': HPLCTarget, ...}
    :rtype: dict
    """
    # todo fix to have similar functionality to v but not zero-pad
    raise NotImplementedError('This method has some fundamental flaws which need to be addressed. Please use '
                              'pull_hplc_data_from_folder_timepoint instead. ')
    targets = {  # store the targets in a vial attribute
        name: HPLCTarget(
            targets[name][0],  # wavelength
            targets[name][1],  # retention time
            name,
            wiggle=wiggle,
        ) for name in targets
    }

    files = Watcher(  # find all matching instances of the target file name
        folder,
        watchfor
    )

    for file in files:  # walk through specified path
        try:
            areas = pull_hplc_area_from_txt(file)  # pull the HPLC area
        except ValueError:  # no peaks defined, define empty
            areas = {}
        for target in targets:  # update each target
            targets[target].add_from_pulled(areas)

    return files.contents, targets


def pull_hplc_data_from_folder_timepoint(folder, wiggle=0.02, watchfor='Report.TXT'):
    """
    Pulls all HPLC data from a folder assuming that the contents of a folder are from an ordered, time-course run (i.e.
    the contents of one report are related to the others in the folder). The method will automatically watch for new
    retention times and will prepopulate appearing values with zeros. The resulting targets will have a consistent
    number of values across the folder.

    :param folder: The folder to search for report files
    :param wiggle: the wiggle time around retention times
    :param watchfor: the name of the report file to watch
    :return: dictionary of HPLCTarget instances in the format {wavelength: {retention_time: HPLCTarget, ...}, ...}
    :rtype: dict
    """

    files = Watcher(  # find all matching instances of the target file name
        folder,
        watchfor,
    )

    targets = {}  # target storage dictionary
    filenames = sorted(files.contents)
    for ind, file in enumerate(tqdm.tqdm(filenames)):  # walk across all matches
        try:
            areas = pull_hplc_area_from_txt(file)  # pull the HPLC area from file

        # special case for no data in file
        except ValueError:
            areas = {wavelength: {} for wavelength in targets}

        for wavelength in areas:  # for each wavelength
            selwl = find_nearest(  # find the appropriate wavelength in the dictionary
                targets,
                wavelength,
                1.,
            )
            if selwl is None:  # if the wavelength is not in the dictionary, create a key
                selwl = wavelength
                targets[selwl] = {}

            # currently defined targets
            current = [targets[selwl][target].retention_time for target in targets[selwl]]
            for ret in areas[selwl]:  # for each retention time in the wavelength
                selret = find_nearest(  # check for presence of retention time in targets
                    current,
                    ret,
                    wiggle,
                )
                if selret is None:  # if the retention time is not present in the targets, create target
                    targets[selwl][ret] = HPLCTarget(
                        wavelength,
                        ret,
                        wiggle=wiggle,
                        zero_pad=ind,  # pad with 0's for previously processed number of files
                    )

            for target in targets[selwl]:  # update each target
                targets[selwl][target].add_from_pulled(areas)

    return filenames, targets


def batch_convert_signals_to_csv(
        folder_path: str,
        *additional_signals: Union[str, DADSignalInfo, dict],
        verbose: Union[bool, int] = True,
):
    """
    Iterates through all .D files in the target directory and writes the signals of those files to csv.
    Additional signals may be specified to "reprocess" the data.

    :param folder_path: folder path to iterate through
    :param additional_signals: additional signals to process. Supported inputs are agilent specification strings
        (e.g. 'DAD1 A, Sig=210,4 Ref=360,100'), DADSignalInfo objects, or dictionaries of keyword arguments for
        instantiation of DADSignalInfo objects
    :param verbose: logging flag or level for function (prints progress info to console)
    """
    logging.basicConfig(format='.D batch conversion to csv - %(message)s')
    log = logging.getLogger()
    if verbose is not False:
        if verbose is True:
            verbose = 20
        log.setLevel(verbose)
    target_folders = Watcher(
        folder_path,
        watchfor='.D',
        watch_type='folder',
    )
    log.info(f'{len(target_folders)} .D folders discovered in target directory.')
    for folder in tqdm.tqdm(target_folders):
        sample = HPLCSample.create_from_D_file(folder)
        for signal in additional_signals:
            sample.add_signal(signal)
        log.info(f'Exporting {len(sample.signals)} signals for {sample.sample_file_name}')
        sample.write_signals_to_csv()


def batch_report_text_to_xlsx(folder: str, watchfor: str = 'Report.TXT'):
    """
    Batch converts all report text files in a directory to xlsx

    :param folder: directory to search
    :param watchfor: file name to watch for
    """
    files = Watcher(  # find all matching instances of the target file name
        folder,
        watchfor,
    )

    for file in tqdm.tqdm(files.contents):
        report_text_to_xlsx(file)
