# ----------------------------------------------------------------------------
# Description    : Qblox instruments instrument and module types
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import re

from enum import Enum
from typing import Any, Union


# -- definitions -------------------------------------------------------------

class TypeEnum(Enum):
    """
    Type base class that arranges child enum string representations.
    """

    def __repr__(self) -> str:
        return "<{}.{}>".format(str(type(self)).split("'")[1], self.name)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: Any) -> bool:
        if type(self) == type(other):
            return str(self) == str(other)
        elif other in [str(val) for val in type(self)]:
            return str(self) == other
        else:
            raise KeyError("{} is not of type {}".format(other, type(self)))

    def __key__(self):
        return str(self)

    def __hash__(self):
        return hash(self.__key__())


class InstrumentClass(TypeEnum):
    """
    Instrument class enum.
    """

    PULSAR = "Pulsar"
    CLUSTER = "Cluster"


class InstrumentType(TypeEnum):
    """
    Instrument/module type enum.
    """

    MM = "MM"
    QCM = "QCM"
    QRM = "QRM"
    _RF = "RF"


class PulsarType(TypeEnum):
    """
    Pulsar module type enum.
    """

    PULSAR_QCM = "Pulsar QCM"
    _PULSAR_QCM_RF = "Pulsar QCM-RF"
    PULSAR_QRM = "Pulsar QRM"
    _PULSAR_QRM_RF = "Pulsar QRM-RF"


class ClusterType(TypeEnum):
    """
    Cluster module type enum.
    """

    _CLUSTER_MM = "Cluster MM"
    CLUSTER_QCM = "Cluster QCM"
    CLUSTER_QCM_RF = "Cluster QCM-RF"
    CLUSTER_QRM = "Cluster QRM"
    CLUSTER_QRM_RF = "Cluster QRM-RF"


# -- class -------------------------------------------------------------------
class TypeHandle:
    """
    Instrument type handler class.
    """

    # ------------------------------------------------------------------------
    def __init__(self, instrument: Union[PulsarType, ClusterType, str]):
        """
        Create instrument type handler object.

        Parameters
        ----------
        instrument : Union[PulsarType, ClusterType, str]
            Instrument/module type specification.

        Returns
        ----------

        Raises
        ----------
        """

        # Set instrument type specification
        try:
            instrument = re.split(" |_|-", str(instrument).upper())

            self._instrument_class = InstrumentClass[instrument[0]]
            self._instrument_type = InstrumentType[instrument[1]]

            self._is_mm_type = self._instrument_type == InstrumentType.MM
            self._is_qrm_type = self._instrument_type == InstrumentType.QRM
            self._is_qcm_type = self._instrument_type == InstrumentType.QCM
        except Exception:
            raise RuntimeError("Invalid instrument type.")

        self._is_rf_type = False
        if len(instrument) > 2:
            self._is_rf_type = instrument[2] == str(InstrumentType._RF)
            if not self._is_rf_type:
                raise RuntimeError("Invalid instrument type.")

    # ------------------------------------------------------------------------
    @property
    def instrument_class(self) -> InstrumentClass:
        """
        Get instrument class (e.g. Pulsar, Cluster).

        Parameters
        ----------

        Returns
        ----------
        InstrumentClass
            Instrument class

        Raises
        ----------
        """

        return self._instrument_class

    # ------------------------------------------------------------------------
    @property
    def instrument_type(self) -> InstrumentType:
        """
        Get instrument type (e.g. MM, QRM, QCM).

        Parameters
        ----------

        Returns
        ----------
        InstrumentType
            Instrument type

        Raises
        ----------
        """

        return self._instrument_type

    # ------------------------------------------------------------------------
    @property
    def is_mm_type(self) -> bool:
        """
        Return if module is of type MM.

        Parameters
        ----------

        Returns
        ----------
        bool
            True if module is of type MM.

        Raises
        ----------
        """

        return self._is_mm_type

    # ------------------------------------------------------------------------
    @property
    def is_qcm_type(self) -> bool:
        """
        Return if module is of type QCM.

        Parameters
        ----------

        Returns
        ----------
        bool
            True if module is of type QCM.

        Raises
        ----------
        """

        return self._is_qcm_type

    # ------------------------------------------------------------------------
    @property
    def is_qrm_type(self) -> bool:
        """
        Return if module is of type QRM.

        Parameters
        ----------

        Returns
        ----------
        bool
            True if module is of type QRM.

        Raises
        ----------
        """

        return self._is_qrm_type

    # ------------------------------------------------------------------------
    @property
    def is_rf_type(self) -> bool:
        """
        Return if module is of type QCM-RF or QRM-RF.

        Parameters
        ----------

        Returns
        ----------
        bool
            True if module is of type QCM-RF or QRM-RF.

        Raises
        ----------
        """

        return self._is_rf_type
