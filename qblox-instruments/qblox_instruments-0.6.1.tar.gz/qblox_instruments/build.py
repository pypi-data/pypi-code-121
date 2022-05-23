# --------------------------------------------------------------------------
# Description    : Qblox instruments build information
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# --------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

import re
import functools

from datetime import datetime
from typing import Union, Optional, Tuple


# -- definitions -------------------------------------------------------------

# Wildcard import definition
__all__ = ["get_build_info", "BuildInfo", "DeviceInfo", "__version__"]


# -- classes -----------------------------------------------------------------

@functools.total_ordering
class BuildInfo:
    """
    Class representing build information for a particular component.
    """

    __slots__ = ["_version", "_build", "_hash", "_dirty"]

    # ------------------------------------------------------------------------
    def __init__(
        self,
        version: Union[str, Tuple[int, int, int]],
        build: Union[str, int, datetime],
        hash: Union[str, int],
        dirty: Union[str, bool],
    ):
        """
        Makes a build information object.

        Parameters
        ----------
        version: Union[str, Tuple[int, int, int]]
            Either a canonical version string or a three-tuple of integers.
        build: Union[str, int, datetime],
            The build timestamp, either as a string formatted like
            "17/11/2021-19:04:53" (as used in ``*IDN?``), a Unix timestamp in
            seconds, or a Python datetime object.
        hash: Union[str, int]
            The git hash of the repository that the build was run from,
            either as a hex string with at least 8 characters, or as an
            integer. If 0x is prefixed, the hash may have less than 8 digits,
            implying zeros in front.
        dirty: Union[str, bool]
            Whether the git repository was dirty at the time of the build,
            either as a ``0`` or ``1`` string (as in ``*IDN?``) or as the
            boolean itself.
        """

        # Convert and check version.
        if isinstance(version, str):
            version = map(int, version.split("."))
        version = tuple(version)
        if len(version) != 3:
            raise ValueError("invalid version specified")
        for comp in version:
            if not isinstance(comp, int):
                raise TypeError("unsupported type for version")
            if comp < 0:
                raise ValueError("invalid version specified")
        self._version = version

        # Convert and check build timestamp.
        if isinstance(build, str):
            build = datetime.strptime(build, "%d/%m/%Y-%H:%M:%S")
        elif isinstance(build, int):
            build = datetime.fromtimestamp(build)
        if not isinstance(build, datetime):
            raise TypeError("unsupported type for build")
        self._build = build

        # Convert and check git hash.
        if isinstance(hash, str):
            m = re.fullmatch("0x[0-9a-fA-F]{1,8}|[0-9a-fA-F]{8}", hash)
            if not m:
                raise ValueError("invalid or too short git hash specified: {!r}".format(hash))
            hash = int(m.group(0), 16)
        if not isinstance(hash, int):
            raise TypeError("unsupported type for hash")
        if hash < 0 or hash > 0xFFFFFFFF:
            raise ValueError("hash integer out of range")
        self._hash = hash

        # Convert and check dirty flag.
        if isinstance(dirty, str):
            if dirty == "0":
                dirty = False
            elif dirty == "1":
                dirty = True
            else:
                raise ValueError("invalid string specified for dirty")
        if not isinstance(dirty, bool):
            raise TypeError("unsupported type for dirty")
        self._dirty = dirty

    # ------------------------------------------------------------------------
    @property
    def version(self) -> Tuple[int, int, int]:
        """
        The version as a three-tuple.

        :type: Tuple[int, int, int]
        """
        return self._version

    # ------------------------------------------------------------------------
    @property
    def version_str(self) -> str:
        """
        The version as a string.

        :type: str
        """
        return ".".join(map(str, self._version))

    # ------------------------------------------------------------------------
    @property
    def build(self) -> datetime:
        """
        The build timestamp as a datetime object.

        :type: datetime
        """
        return self._build

    # ------------------------------------------------------------------------
    @property
    def build_str(self) -> str:
        """
        The build time as a string, as formatted for ``*IDN?``.

        :type: str
        """
        return self._build.strftime("%d/%m/%Y-%H:%M:%S")

    # ------------------------------------------------------------------------
    @property
    def build_iso(self) -> str:
        """
        The build time as a string, formatted using the ISO date format.

        :type: str
        """
        return self._build.isoformat()

    # ------------------------------------------------------------------------
    @property
    def build_unix(self) -> int:
        """
        The build time as a unix timestamp in seconds.

        :type: int
        """
        return int(self._build.timestamp())

    # ------------------------------------------------------------------------
    @property
    def hash(self) -> int:
        """
        The git hash as an integer.

        :type: int
        """
        return int(self._hash)

    # ------------------------------------------------------------------------
    @property
    def hash_str(self) -> str:
        """
        The git hash as a string.

        :type: str
        """
        return "{:08x}".format(self._hash)

    # ------------------------------------------------------------------------
    @property
    def dirty(self) -> bool:
        """
        Whether the repository was dirty during the build.

        :type: bool
        """
        return self._dirty

    # ------------------------------------------------------------------------
    @property
    def dirty_str(self) -> str:
        """
        The dirty flag as a ``0`` or ``1`` string (as used for ``*IDN?``).

        :type: str
        """
        return "1" if self._dirty else "0"

    # ------------------------------------------------------------------------
    @classmethod
    def from_idn(cls, idn: str, prefix: str = "") -> Optional["BuildInfo"]:
        """
        Constructs a build information structure from an ``*IDN?`` string.

        Parameters
        ----------
        idn: str
            The ``*IDN?`` string.
        prefix: str
            The prefix used for each key (currently ``fw``, ``kmod``, ``sw``,
            or ``cfgMan``).

        Returns
        -------
        Optional[BuildInfo]
            The build information structure if data is available for the given
            key, or None if not.
        """
        build_data = {
            x[0]: x[1] for x in (s.split("=", maxsplit=1) for s in idn.split(",")[-1].split())
        }
        try:
            return cls(
                build_data["{}Version".format(prefix)],
                build_data["{}Build".format(prefix)],
                build_data["{}Hash".format(prefix)],
                build_data["{}Dirty".format(prefix)],
            )
        except KeyError:
            return None

    # ------------------------------------------------------------------------
    def to_idn(self, prefix: str = "") -> str:
        """
        Formats this build information object in the same way ``*IDN?`` is
        formatted.

        Parameters
        ----------
        prefix: str
            The prefix used for each key (currently ``fw``, ``kmod``, ``sw``,
            or ``cfgMan``).

        Returns
        -------
        str
            The part of the ``*IDN?`` string for this build information object.
        """
        return "{4}Version={0} {4}Build={1} {4}Hash=0x{2:08X} {4}Dirty={3}".format(
            self.version_str, self.build_str, self.hash, self.dirty_str, prefix
        )

    # ------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, build_data: dict) -> "BuildInfo":
        """
        Constructs a build information structure from a JSON-capable dict,
        as used in ZeroMQ/CBOR descriptions, plug&play descriptions, update
        file metadata, and various other places.

        Parameters
        ----------
        build_data: dict
            Dictionary with (at least) the following keys:

             - ``"version"``: iterable of three integers representing the
               version;
             - ``"build"``: Unix timestamp in seconds representing the build
               timestamp;
             - ``"hash"``: the first 8 hex digits of the git hash as an
               integer; and
             - ``"dirty"``: boolean dirty flag.

        Returns
        -------
        BuildInfo
            The build information structure.
        """
        return cls(
            build_data["version"],
            build_data["build"],
            build_data["hash"],
            build_data["dirty"],
        )

    # ------------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Formats this build information object as a JSON-capable dict, as used
        in ZeroMQ/CBOR descriptions, plug&play descriptions, update file
        metadata, and various other places.

        Parameters
        ----------
        None

        Returns
        -------
        dict
            The generated dictionary, having the following keys:

             - ``"version"``: iterable of three integers representing the
               version;
             - ``"build"``: Unix timestamp in seconds representing the build
               timestamp;
             - ``"hash"``: the first 8 hex digits of the git hash as an
               integer; and
             - ``"dirty"``: boolean dirty flag.

        """
        return {
            "version": self.version,
            "build": self.build_unix,
            "hash": self.hash,
            "dirty": self.dirty,
        }

    # ------------------------------------------------------------------------
    def to_idn_dict(self) -> dict:
        """
        Formats this build information object as a human-readable JSON-capable dict,
        as used in get_idn.

        Parameters
        ----------

        Returns
        -------
        dict
            The generated dictionary, having the following keys:

             - ``"version"``: string representation of the version;
             - ``"build"``: string representation of timestamp in seconds representing the build
               timestamp;
             - ``"hash"``: string representation of the first 8 hex digits of the git hash; and
             - ``"dirty"``: boolean dirty flag.

        """
        return {
            "version": self.version_str,
            "build": self.build_str,
            "hash": self.hash_str,
            "dirty": self.dirty,
        }

    # ------------------------------------------------------------------------
    def to_tuple(self) -> tuple:
        """
        Formats this build information object as a tuple for ordering purposes.

        Parameters
        ----------
        None

        Returns
        -------
        tuple
            A tuple, containing all the information in this structure in a
            canonical format.
        """
        return (self.version, self.build_unix, self.hash, self.dirty)

    # ------------------------------------------------------------------------
    def __eq__(self, other) -> bool:
        if isinstance(other, BuildInfo):
            return self.to_tuple() == other.to_tuple()

        return NotImplemented

    # ------------------------------------------------------------------------
    def __lt__(self, other) -> bool:
        if isinstance(other, BuildInfo):
            return self.to_tuple() < other.to_tuple()

        return NotImplemented

    # ------------------------------------------------------------------------
    def __str__(self) -> str:
        return "{}, built on {} from git hash {}{}".format(
            self.version_str,
            self.build_iso,
            self.hash_str,
            " (dirty)" if self.dirty else "",
        )


# --------------------------------------------------------------------------
class DeviceInfo:
    """
    Class representing the build and model information of a device. Has the
    same information content as what ``*IDN?`` returns.
    """

    __slots__ = [
        "_manufacturer",
        "_model",
        "_serial",
        "_sw_build",
        "_fw_build",
        "_kmod_build",
        "_cfg_man_build",
    ]

    # ------------------------------------------------------------------------
    def __init__(
        self,
        manufacturer: str,
        model: str,
        serial: Optional[str] = None,
        sw_build: Optional[BuildInfo] = None,
        fw_build: Optional[BuildInfo] = None,
        kmod_build: Optional[BuildInfo] = None,
        cfg_man_build: Optional[BuildInfo] = None,
    ):
        if not isinstance(manufacturer, str):
            raise TypeError("invalid type specified for manufacturer")
        self._manufacturer = manufacturer.replace(" ", "_").lower()

        if not isinstance(model, str):
            raise TypeError("invalid type specified for model")
        self._model = model.replace(" ", "_").lower()

        if serial is not None and not isinstance(serial, str):
            raise TypeError("invalid type specified for serial")
        self._serial = serial

        if sw_build is not None and not isinstance(sw_build, BuildInfo):
            raise TypeError("invalid type specified for sw_build")
        self._sw_build = sw_build

        if fw_build is not None and not isinstance(fw_build, BuildInfo):
            raise TypeError("invalid type specified for fw_build")
        self._fw_build = fw_build

        if kmod_build is not None and not isinstance(kmod_build, BuildInfo):
            raise TypeError("invalid type specified for kmod_build")
        self._kmod_build = kmod_build

        if cfg_man_build is not None and not isinstance(cfg_man_build, BuildInfo):
            raise TypeError("invalid type specified for cfg_man_build")
        self._cfg_man_build = cfg_man_build

    # ------------------------------------------------------------------------
    @property
    def manufacturer(self) -> str:
        """
        The manufacturer name, in lowercase_with_underscores format.

        :type: str
        """
        return self._manufacturer

    # ------------------------------------------------------------------------
    @property
    def model(self) -> str:
        """
        The model name, in lowercase_with_underscores format.

        :type: str
        """
        return self._model

    device = model

    # ------------------------------------------------------------------------
    @property
    def serial(self) -> Optional[str]:
        """
        The serial number, if known.

        :type: Optional[str]
        """
        return self._serial

    # ------------------------------------------------------------------------
    @property
    def sw_build(self) -> Optional[BuildInfo]:
        """
        The software/application build information, if known.

        :type: Optional[BuildInfo]
        """
        return self._sw_build

    # ------------------------------------------------------------------------
    @property
    def fw_build(self) -> Optional[BuildInfo]:
        """
        The FPGA firmware build information, if known.

        :type: Optional[BuildInfo]
        """
        return self._fw_build

    # ------------------------------------------------------------------------
    @property
    def kmod_build(self) -> Optional[BuildInfo]:
        """
        The kernel module build information, if known.

        :type: Optional[BuildInfo]
        """
        return self._kmod_build

    # ------------------------------------------------------------------------
    @property
    def cfg_man_build(self) -> Optional[BuildInfo]:
        """
        The configuration management build information, if known.

        :type: Optional[BuildInfo]
        """
        return self._cfg_man_build

    # ------------------------------------------------------------------------
    def get_build_info(self, key: str) -> Optional[BuildInfo]:
        """
        Returns build information for the given key.

        Parameters
        ----------
        key: str
            The key. Must be one of:

             - ``"sw"``: returns the application build info;
             - ``"fw"``: returns the FPGA firmware build info;
             - ``"kmod"``: returns the kernel module build info; or
             - ``"cfg_man"`` or ``"cfgMan"``: returns the configuration manager
               build info.

        Returns
        -------
        Optional[BuildInfo]
            The build information structure, if known.

        Raises
        ------
        KeyError
            For unknown keys.
        """
        if key == "sw":
            return self._sw_build
        elif key == "fw":
            return self._fw_build
        elif key == "kmod":
            return self._kmod_build
        elif key in ("cfg_man", "cfgMan"):
            return self._cfg_man_build
        else:
            raise KeyError("unknown key {!r}".format(key))

    # ------------------------------------------------------------------------
    def __getitem__(self, key: str) -> BuildInfo:
        """
        Same as get_build_info(), but raises a KeyError if no data is known.

        Parameters
        ----------
        key: str
            The key. Must be one of:

             - ``"sw"``: returns the application build info;
             - ``"fw"``: returns the FPGA firmware build info;
             - ``"kmod"``: returns the kernel module build info; or
             - ``"cfg_man"`` or ``"cfgMan"``: returns the configuration
               manager build info.

        Returns
        -------
        BuildInfo
            The build information structure.

        Raises
        ------
        KeyError
            If no data is known for the given key or the key itself is unknown.
        """
        result = self.get_build_info(key)
        if result is None:
            raise KeyError("no data for key {!r}".format(key))
        return result

    # ------------------------------------------------------------------------
    def __contains__(self, key: str) -> bool:
        """
        Returns whether data is known for the given key.

        Parameters
        ----------
        key: str
            The key. Must be one of:

             - ``"sw"``: returns the application build info;
             - ``"fw"``: returns the FPGA firmware build info;
             - ``"kmod"``: returns the kernel module build info; or
             - ``"cfg_man"`` or ``"cfgMan"``: returns the configuration
               manager build info.

        Returns
        -------
        bool
            Whether data is known.
        """
        try:
            return self.get_build_info(key) is not None
        except KeyError:
            return False

    # ------------------------------------------------------------------------
    @classmethod
    def from_idn(cls, idn: str) -> "DeviceInfo":
        """
        Constructs a device information structure from an ``*IDN?`` string.

        Parameters
        ----------
        idn: str
            The ``*IDN?`` string.

        Returns
        -------
        DeviceInfo
            The parsed device information structure.
        """

        manufacturer, model, *serial, build_data = idn.split(",")
        if serial:
            serial = serial[0]
        else:
            serial = None

        return cls(
            manufacturer,
            model,
            serial,
            BuildInfo.from_idn(build_data, "sw"),
            BuildInfo.from_idn(build_data, "fw"),
            BuildInfo.from_idn(build_data, "kmod"),
            BuildInfo.from_idn(build_data, "cfgMan"),
        )

    # ------------------------------------------------------------------------
    def to_idn(self) -> str:
        """
        Formats this device information object in the same way ``*IDN?`` is
        formatted.

        Parameters
        ----------

        Returns
        -------
        str
            The ``*IDN?`` string.
        """
        idn = []
        for key in ("sw", "fw", "kmod", "cfgMan"):
            bi = self.get_build_info(key)
            if bi is not None:
                idn.append(bi.to_idn(key))
        idn = " ".join(idn)
        if self._serial is not None:
            idn = "{},{}".format(self._serial, idn)
        idn = "{},{},{}".format(self._manufacturer, self._model, idn)
        return idn

    # ------------------------------------------------------------------------
    @classmethod
    def from_dict(cls, description: dict) -> "DeviceInfo":
        """
        Constructs a device information structure from a JSON-capable dict,
        as used in ZeroMQ/CBOR descriptions, plug&play descriptions, update
        file metadata, and various other places.

        Parameters
        ----------
        description: dict
            Dictionary with the following keys:

             - ``"manufacturer"``: manufacturer name (string);
             - ``"model"``: model name (string);
             - ``"ser"``: serial number (string);
             - ``"sw"``: application build information (dict);
             - ``"fw"``: FPGA firmware build information (dict);
             - ``"kmod"``: kernel module build information (dict); and
             - ``"cfg_man"``: configuration management build information
               (dict);

        Returns
        -------
        DeviceInfo
            The build information structure.
        """
        return cls(
            description.get("manufacturer", "unknown"),
            description.get("model", "unknown"),
            description.get("ser", None),
            BuildInfo.from_dict(description["sw"]) if "sw" in description else None,
            BuildInfo.from_dict(description["fw"]) if "fw" in description else None,
            BuildInfo.from_dict(description["kmod"]) if "kmod" in description else None,
            BuildInfo.from_dict(description["cfg_man"]) if "cfg_man" in description else None,
        )

    # ------------------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Formats this device information object as a JSON-capable dict, as used
        in ZeroMQ/CBOR descriptions, plug&play descriptions, update file
        metadata, and various other places.

        Parameters
        ----------

        Returns
        -------
        dict
            The generated dictionary, having the following keys:

             - ``"manufacturer"``: manufacturer name (string);
             - ``"model"``: model name (string);
             - ``"ser"``: serial number (string);
             - ``"sw"``: application build information (dict);
             - ``"fw"``: FPGA firmware build information (dict);
             - ``"kmod"``: kernel module build information (dict); and/or
             - ``"cfg_man"``: configuration management build information
               (dict);

            Some keys may be omitted if the information is not available.
        """
        description = {}
        if self._manufacturer != "unknown":
            description["manufacturer"] = self._manufacturer
        if self._model != "unknown":
            description["model"] = self._model
        if self._serial is not None:
            description["ser"] = self._serial
        for key in ("sw", "fw", "kmod", "cfg_man"):
            bi = self.get_build_info(key)
            if bi is not None:
                description[key] = bi.to_dict()
        return description

    # ------------------------------------------------------------------------
    def to_idn_dict(self) -> dict:
        """
        Formats this device information object as a human-readable
        JSON-capable dict, as used get_idn.

        Parameters
        ----------

        Returns
        -------
        dict
            The generated dictionary, having the following keys:

             - ``"manufacturer"``: manufacturer name (string);
             - ``"model"``: model name (string);
             - ``"serial_number"``: serial number (string);
             - ``"firmware"``: build info (dict);
                - ``"fpga"``: FPGA firmware build information (dict);
                - ``"kernel_mod"``: kernel module build information (dict);
                - ``"application"``: application build information (dict); and
                - ``"driver"``: driver build information (dict);

            Some keys may be omitted if the information is not available.
        """
        description = {}
        if self._manufacturer != "unknown":
            description["manufacturer"] = self._manufacturer
        if self._model != "unknown":
            description["model"] = self._model
        if self._serial is not None:
            description["serial_number"] = self._serial
        description["firmware"] = {}
        for key, idn_key in zip(
            ["fw", "kmod", "sw"],
            ["fpga", "kernel_mod", "application"]
        ):
            bi = self.get_build_info(key)
            if bi is not None:
                description["firmware"][idn_key] = bi.to_idn_dict()
        description["firmware"]["driver"] = get_build_info().to_idn_dict()
        return description

    # ------------------------------------------------------------------------
    def to_tuple(self) -> tuple:
        """
        Formats this device information object as a tuple for ordering
        purposes.

        Parameters
        ----------

        Returns
        -------
        tuple
            A tuple, containing all the information in this structure in a
            canonical format.
        """
        return (
            self._manufacturer,
            self._model,
            self._serial,
            self._sw_build.to_tuple() if self._sw_build is not None else None,
            self._fw_build.to_tuple() if self._fw_build is not None else None,
            self._kmod_build.to_tuple() if self._kmod_build is not None else None,
            self._cfg_man_build.to_tuple() if self._cfg_man_build is not None else None,
        )

    # ------------------------------------------------------------------------
    def __eq__(self, other) -> bool:
        if isinstance(other, DeviceInfo):
            return self.to_tuple() == other.to_tuple()

        return NotImplemented

    # ------------------------------------------------------------------------
    def __ne__(self, other) -> bool:
        if isinstance(other, DeviceInfo):
            return self.to_tuple() != other.to_tuple()

        return NotImplemented

    # ------------------------------------------------------------------------
    def __str__(self) -> str:
        return "{} {}".format(self.manufacturer, self.model)


# -- functions -----------------------------------------------------------------

def get_build_info() -> BuildInfo:
    """
    Get build information for Qblox Instruments.

    Parameters
    ----------

    Returns
    -------
    BuildInfo
        Build information structure for Qblox Instruments.
    """

    return BuildInfo(
        version="0.6.1",
        build="20/05/2022-17:29:34",
        hash="0xEF57DA54",
        dirty=False
    )


# Set version.
__version__ = get_build_info().version_str
