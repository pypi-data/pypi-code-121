# ----------------------------------------------------------------------------
# Description    : SCPI-based cfg_man connection adapter class
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import time
from typing import BinaryIO, Any, Optional
from qblox_instruments.cfg_man.probe import ConnectionInfo
from qblox_instruments.scpi import CfgMan
from qblox_instruments.ieee488_2 import IpTransport
import qblox_instruments.cfg_man.log as log


# -- definitions -------------------------------------------------------------

# Transfer size from file to socket and vice versa for file transfers.
_BUF_SIZE = 256 * 1024


# -- functions ---------------------------------------------------------------

def _lerp(a: float, b: float, f: float) -> float:
    """
    Linear interpolation between a and b using fraction f.

    Parameters
    ----------
    a: float
        Value for f = 0.
    b: float
        Value for f = 1.
    f: float
        Interpolation fraction.

    Returns
    -------
    float
        The interpolated value.
    """
    return a * (1.0 - f) + b * f


# -- class -------------------------------------------------------------------

class ScpiConnection:
    """
    Connection class for connecting to SCPI-based configuration managers and
    supporting applications. Do not instantiate and use directly; leave this
    to the ConfigurationManager class in main.
    """

    # ------------------------------------------------------------------------
    def __init__(self, ci: ConnectionInfo):
        """
        Opens a SCPI-based configuration manager connection.

        Parameters
        ----------
        ci: ConnectionInfo
            Connection information.
        """
        super().__init__()
        assert ci.protocol == "scpi"
        self._transport = IpTransport(ci.address[0], ci.address[1])
        self._conn = CfgMan(self._transport)

    # ------------------------------------------------------------------------
    def close(self) -> None:
        """
        Closes the connection.

        Parameters
        ----------

        Returns
        -------
        """
        self._transport.close()

    # ------------------------------------------------------------------------
    def _task_wait(
        self,
        task_handle: int,
        progress_message: Optional[str] = None,
        progress_from: float = 0.0,
        progress_to: float = 1.0,
    ) -> Any:
        """
        Waits for an asynchronous task on the device to complete.

        Parameters
        ----------
        task_handle: str
            The file to upload.
        progress_message: Optional[str]
            If specified, log.progress() will be called to display a task
            progress bar. This is then the message shown.
        progress_from: float = 0.0
            If a progress bar is rendered, this is the value shown for 0%
            task progress.
        progress_to: float = 1.0
            If a progress bar is rendered, this is the value shown for 100%
            task progress.

        Returns
        -------
        int
            The file handle for use with the temp_file API.
        """

        # Initialize the progress bar.
        if progress_message is not None:
            log.progress(progress_from, progress_message)
        try:

            while True:

                # Poll for completion.
                progress = self._conn._task_poll(task_handle)
                if progress >= 1.0:
                    return self._conn._task_get_result(task_handle)

                # Update the progress bar.
                if progress_message is not None:
                    log.progress(
                        _lerp(progress_from, progress_to, progress),
                        progress_message
                    )

                # Delay.
                time.sleep(0.3)

        finally:

            # Clear the progress bar.
            if progress_message is not None:
                if progress_to >= 1.0:
                    log.clear_progress()
                else:
                    log.progress(progress_to, "")

    # ------------------------------------------------------------------------
    def _file_upload(
        self,
        file: BinaryIO,
        progress_message: Optional[str] = None,
        progress_from: float = 0.0,
        progress_to: float = 1.0,
    ) -> int:
        """
        Uploads a file to the device using the temp_file command set.

        Parameters
        ----------
        file: BinaryIO
            The file to upload.
        progress_message: Optional[str]
            If specified, log.progress() will be called to display an upload
            progress bar. This is then the message shown.
        progress_from: float = 0.0
            If a progress bar is rendered, this is the value shown for 0%
            upload progress.
        progress_to: float = 1.0
            If a progress bar is rendered, this is the value shown for 100%
            upload progress.

        Returns
        -------
        int
            The file handle for use with the temp_file API.
        """

        # Get the size of the to-be-uploaded file.
        file.seek(0, 2)
        size = file.tell()

        # Seek back to the start of the file.
        file.seek(0)

        # Create a temporary file on the device to write to.
        file_handle = self._conn._temp_file_new()
        try:

            # Initialize the progress bar.
            if progress_message is not None:
                log.progress(progress_from, progress_message)
            try:

                while True:

                    # Copy bytes from the input file to the file on the device
                    # until we reach EOF.
                    buf = file.read(_BUF_SIZE)
                    if not buf:
                        return file_handle
                    self._conn._temp_file_append(file_handle, buf)

                    # Update the progress bar.
                    if progress_message is not None:
                        log.progress(
                            _lerp(progress_from, progress_to, file.tell() / size),
                            progress_message,
                        )

            finally:

                # Clear the progress bar.
                if progress_message is not None:
                    if progress_to >= 1.0:
                        log.clear_progress()
                    else:
                        log.progress(progress_to, "")

        except:

            # If something breaks, clean up after ourselves on the device.
            self._conn._temp_file_delete(file_handle)
            raise

    # ------------------------------------------------------------------------
    def _file_download(
        self,
        file_handle: int,
        file: BinaryIO,
        progress_message: Optional[str] = None,
        progress_from: float = 0.0,
        progress_to: float = 1.0,
    ) -> None:
        """
        Downloads a file from the device using the temp_file command set.

        Parameters
        ----------
        file_handle: BinaryIO
            Handle to the temp_file to download.
        file: BinaryIO
            The file to save the download data to.
        progress_message: Optional[str]
            If specified, log.progress() will be called to display an download
            progress bar. This is then the message shown.
        progress_from: float = 0.0
            If a progress bar is rendered, this is the value shown for 0%
            download progress.
        progress_to: float = 1.0
            If a progress bar is rendered, this is the value shown for 100%
            download progress.

        Returns
        -------
        int
            The file handle for use with the temp_file API.
        """

        # Initialize the progress bar.
        if progress_message is not None:
            log.progress(progress_from, progress_message)
        try:

            # Figure out the number of blocks that the device will subdivide
            # the file into.
            num_blocks = self._conn._temp_file_block_count(file_handle)

            # Download the blocks.
            for block in range(num_blocks):
                file.write(self._conn._temp_file_block_read(file_handle, block))

                # Update the progress bar.
                if progress_message is not None:
                    log.progress(
                        _lerp(progress_from, progress_to, block / num_blocks),
                        progress_message,
                    )

        finally:

            # Clear the progress bar.
            if progress_message is not None:
                if progress_to >= 1.0:
                    log.clear_progress()
                else:
                    log.progress(progress_to, "")

    # ------------------------------------------------------------------------
    def set_name(self, name: str) -> None:
        """
        Renames the device. The name change will be processed immediately.

        Parameters
        ----------
        name: str
            The new name.

        Returns
        -------

        Raises
        ------
        Exception
            If the command failed.
        """
        self._conn.set_name(name)

    # ------------------------------------------------------------------------
    def set_ip_config(self, config: str) -> None:
        """
        Reconfigures the IP configuration of the device. Changes will only go
        into effect after the device is rebooted.

        Parameters
        ----------
        config: str
            The IP configuration.

        Returns
        -------

        Raises
        ------
        Exception
            If the command failed.
        """
        self._conn.set_ip_config(config)

    # ------------------------------------------------------------------------
    def download_log(self, source: str, fmt: int, file: BinaryIO) -> None:
        """
        Downloads log data from the device.

        Parameters
        ----------
        source: str
            The log source. Must be ``"app"``, ``"system"``, or ``"cfg_man"``.
        fmt: int
            Either:

             - positive: the given number of most recent messages will be
               downloaded in plaintext format.
             - zero: the current log file in rotation will be downloaded in
               plaintext format.
             - negative: all log files in rotation will be downloaded as a
               tar.gz archive.

        file: BinaryIO
            Destination file, open in write mode.

        Returns
        -------

        Raises
        ------
        Exception
            If the command failed.
        """

        # Prepare a temp_file on the device with the requested data.
        file_handle = self._task_wait(
            self._conn._download_log(source, fmt),
            "Preparing log download",
            0.0,
            0.5
        )

        try:

            # Write the file.
            self._file_download(
                file_handle,
                file,
                "Downloading log",
                0.5,
                1.0
            )

        finally:

            # Clean up after ourselves.
            self._conn._temp_file_delete(file_handle)

    # ------------------------------------------------------------------------
    def update(self, file: BinaryIO) -> None:
        """
        Sends an update package to the device.

        Parameters
        ----------
        file: BinaryIO
            File open in read mode representing the data to be sent.

        Returns
        -------
        """

        # Upload the update file.
        file_handle = self._file_upload(
            file,
            "Sending update",
            0.0,
            0.5
        )

        try:

            # Have the device prepare the update process (the actual update
            # will be carried out between two reboots).
            self._task_wait(
                self._conn._update(file_handle),
                "Preparing update",
                0.5,
                1.0
            )

        finally:

            # Clean up after ourselves.
            self._conn._temp_file_delete(file_handle)

    # ------------------------------------------------------------------------
    def rollback(self) -> None:
        """
        Sends a rollback request to the device.

        Parameters
        ----------

        Returns
        -------
        """
        self._task_wait(self._conn._rollback(), "Preparing rollback")

    # ------------------------------------------------------------------------
    def reboot(self) -> None:
        """
        Sends a reboot request to the device.

        Parameters
        ----------

        Returns
        -------
        """
        self._conn.reboot()
