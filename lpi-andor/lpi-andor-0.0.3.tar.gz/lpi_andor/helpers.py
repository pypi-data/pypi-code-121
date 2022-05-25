# helper functions

import os
import platform
import pkg_resources

from pyAndorSDK2 import atmcd_errors
from pyAndorSpectrograph.spectrograph import ATSpectrograph


def library_path(lib: str):
    """
    :param lib: The desired resource.
        Values: [`sdk`, `spectrometer`]
    :returns: Path to the desired library resource
        based off the machines operating system and architecture.
    """
    if lib not in ['sdk', 'spectrometer']:
        raise ValueError(f'`lib` must be in [`sdk`, `spectrometer`], received {lib}')

    plt = platform.system()
    if plt not in ['Linux', 'Windows']:
        raise RuntimeError('lpi_andor can only be run on Linux or Windows.') 

    (arch, _) = platform.architecture()
    arch = arch.replace('bit', '')

    res_path = os.path.normpath(os.path.join('package_data', lib, plt, arch))
    path = pkg_resources.resource_filename('lpi_andor', res_path)

    return path



def handle_atmcd_error(err: atmcd_errors.Error_Codes, message: str = None):
        """
        Raises an error if `err` is not a success status code.

        :param err: Error code.
        :param message: Message to display to user. [Default: None]
        :raises RuntimeError: If `err` is not atmcd_errors.Error_Codes.DRV_SUCCESS.
        """
        if err == atmcd_errors.Error_Codes.DRV_SUCCESS:
            # success
            return

        if err == atmcd_errors.Error_Codes.DRV_NOT_AVAILABLE:
            raise RuntimeError(f'[Error {err} | Camera restart required] {message}')

        raise RuntimeError(f'[Error {err}] {message}')


def handle_ats_error(err, message: str = None):
        """
        Raises an error if `err` is not a success status code.

        :param err: Error code.
        :param message: Message to display to user. [Default: None]
        :raises RuntimeError: If `err` is not atmcd_errors.Error_Codes.DRV_SUCCESS.
        """
        if err == ATSpectrograph.ATSPECTROGRAPH_SUCCESS:
            # success
            return

        raise RuntimeError(f'[Error {err}] {message}')
