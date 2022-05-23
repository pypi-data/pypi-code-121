# ----------------------------------------------------------------------------
# Description    : Plug&play-based cfg_man connection adapter class
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2021)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

from qblox_instruments.cfg_man.probe import ConnectionInfo
from qblox_instruments.pnp import PlugAndPlay


# -- class -------------------------------------------------------------------

class PnpConnection:
    """
    Connection class for performing some configuration manager tasks when only
    plug & play is available due to IP misconfiguration. Do not instantiate
    and use directly; leave this to the ConfigurationManager in main.
    """

    # ------------------------------------------------------------------------
    def __init__(self, ci: ConnectionInfo):
        """
        Opens a SCPI-based configuration mananger connection.

        Parameters
        ----------
        ci: ConnectionInfo
            Connection information.
        """
        super().__init__()
        assert ci.protocol == "pnp"
        self._serial = ci.device.serial
        self._conn = PlugAndPlay()

    # ------------------------------------------------------------------------
    def close(self) -> None:
        """
        Closes the connection.

        Parameters
        ----------

        Returns
        -------
        """
        self._conn.close()

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
        self._conn.set_name(self._serial, name)

    # ------------------------------------------------------------------------
    def set_ip_config(self, config: str) -> None:
        """
        Reconfigures the IP configuration of the device.

        .. note::
            Unlike for the other connection types, this will immediately
            reboot the device.

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
        self._conn.set_ip(self._serial, config)

    # ------------------------------------------------------------------------
    def reboot(self) -> None:
        """
        Sends a reboot request to the device.

        Parameters
        ----------

        Returns
        -------
        """
        self._conn.reboot(self._serial)
