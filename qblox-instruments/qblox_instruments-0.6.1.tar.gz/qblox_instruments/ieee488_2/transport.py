# ----------------------------------------------------------------------------
# Description    : Transport layer (abstract, IP, file, dummy)
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

from abc import ABCMeta, abstractmethod
from typing import Any


# -- class --------------------------------------------------------------------

class Transport(metaclass=ABCMeta):
    """
    Abstract base class for data transport to instruments.
    """

    # ------------------------------------------------------------------------
    @abstractmethod
    def close(self) -> None:
        """
        Abstract method to close instrument.

        Parameters
        ----------

        Returns
        ----------

        Raises
        ----------
        """

        pass

    # ------------------------------------------------------------------------
    @abstractmethod
    def write(self, cmd_str: str) -> None:
        """
        Abstract method to write command to instrument.

        Parameters
        ----------
        cmd_str : str
            Command

        Returns
        ----------

        Raises
        ----------
        """

        pass

    # ------------------------------------------------------------------------
    @abstractmethod
    def write_binary(self, data: bytes) -> None:
        """
        Abstract method to write binary data to instrument.

        Parameters
        ----------
        data : bytes
            Binary data

        Returns
        ----------

        Raises
        ----------
        """

        pass

    # ------------------------------------------------------------------------
    @abstractmethod
    def read_binary(self, size: int) -> bytes:
        """
        Abstract method to read binary data from instrument.

        Parameters
        ----------
        size : int
            Number of bytes

        Returns
        ----------
        bytes
            Binary data array of length "size".

        Raises
        ----------
        """

        pass

    # ------------------------------------------------------------------------
    @abstractmethod
    def readline(self) -> str:
        """
        Abstract method to read data from instrument.

        Parameters
        ----------

        Returns
        ----------
        str
            String with data.

        Raises
        ----------
        """

        pass

    # ------------------------------------------------------------------------
    def __enter__(self) -> Any:
        """
        Context manager entry.

        Parameters
        ----------

        Returns
        -------
        Any
            Returns self
        """

        return self

    # ------------------------------------------------------------------------
    def __exit__(self, type, value, traceback) -> None:
        """
        Context manager exit. Closes the transport.

        Parameters
        ----------

        Returns
        -------
        """

        self.close()
