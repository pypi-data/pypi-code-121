# ----------------------------------------------------------------------------
# Description    : IEEE488.2 interface
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

from qblox_instruments.ieee488_2 import Transport


# -- class -------------------------------------------------------------------

class Ieee488_2:
    """
    Class that implements the IEEE488.2 interface.
    """

    # ------------------------------------------------------------------------
    def __init__(self, transport: Transport):
        """
        Creates IEEE488.2 interface object.

        Parameters
        ----------
        transport : Transport
            Transport class responsible for the lowest level of communication
            (e.g. ethernet).

        Returns
        ----------

        Raises
        ----------
        """

        self._transport = transport

    # ------------------------------------------------------------------------
    def _write(self, cmd_str: str) -> None:
        """
        Write command to instrument

        Parameters
        ----------
        cmd_str : str
            Command string.

        Returns
        ----------

        Raises
        ----------
        """

        self._transport.write(cmd_str + " ")

    # ------------------------------------------------------------------------
    def _write_bin(self, cmd_str: str, bin_block: bytes) -> None:
        """
        Write command and binary data block to instrument

        Parameters
        ----------
        cmd_str : str
            Command string.
        bin_block : bytes
            Binary data array to send.

        Returns
        ----------

        Raises
        ----------
        """

        self._bin_block_write(cmd_str + " ", bin_block)

    # ------------------------------------------------------------------------
    def _read(self, cmd_str: str) -> str:
        """
        Write command to instrument and read response. Using an empty command
        string will skip the write and only read.

        Parameters
        ----------
        cmd_str : str
            Command string.

        Returns
        ----------
        str
            Command response string.

        Raises
        ----------
        """

        self._transport.write(cmd_str)
        return (
            self._transport.readline().rstrip()
        )  # Remove trailing white space, CR, LF

    # ------------------------------------------------------------------------
    def _read_bin(self, cmd_str: str, flush_line_end: bool = True) -> bytes:
        """
        Write command to instrument and read binary data block. Using an empty
        command string will skip the write and only read to allow reading
        concatinated binary blocks.

        Parameters
        ----------
        cmd_str : str
            Command string.
        flush_line_end : bool
            Flush end of line characters.

        Returns
        ----------
        bytes
            Binary data array received.

        Raises
        ----------
        """

        if cmd_str != "":
            self._transport.write(cmd_str)
        return self._bin_block_read(flush_line_end)

    # ------------------------------------------------------------------------
    def _bin_block_write(self, cmd_str: str, bin_block: bytes) -> None:
        """
        Write IEEE488.2 binary data block to instrument.

        Parameters
        ----------
        cmd_str : str
            Command string.
        bin_block : bytes
            Binary data array to send.

        Returns
        ----------

        Raises
        ----------
        """

        header = cmd_str + Ieee488_2._build_header_string(len(bin_block))
        bin_msg = header.encode() + bin_block
        self._transport.write_binary(bin_msg)
        self._transport.write("")  # Add a Line Terminator

    # ------------------------------------------------------------------------
    def _bin_block_read(self, flush_line_end: bool = True) -> bytes:
        """
        Read IEEE488.2 binary data block from instrument.

        Parameters
        ----------
        flush_line_end : bool
            Flush end of line characters.

        Returns
        ----------
        bytes
            Binary data array received.

        Raises
        ----------
        RunTimeError
            Header error.
        """

        header_a = self._transport.read_binary(2)  # Read '#N'
        header_a_str = header_a.decode()
        if header_a_str[0] != "#":
            s = "Header error: received {}".format(header_a)
            raise RuntimeError(s)

        digit_cnt = int(header_a_str[1])
        header_b = self._transport.read_binary(digit_cnt)

        byte_cnt = int(header_b.decode())
        bin_block = self._transport.read_binary(byte_cnt)
        if flush_line_end:
            self._flush_line_end()

        return bin_block

    # ------------------------------------------------------------------------
    @staticmethod
    def _build_header_string(byte_cnt: int) -> str:
        """
        Generate IEEE488.2 binary data block header.

        Parameters
        ----------
        byte_cnt : int
            Size of the binary data block in bytes.

        Returns
        ----------
        str
            Header string.

        Raises
        ----------
        """

        byte_cnt_str = str(byte_cnt)
        digit_cnt_str = str(len(byte_cnt_str))
        bin_header_str = "#" + digit_cnt_str + byte_cnt_str

        return bin_header_str

    # ------------------------------------------------------------------------
    def _flush_line_end(self) -> None:
        """
        Flush end of line <CR><LF> characters.

        Parameters
        ----------

        Returns
        ----------

        Raises
        ----------
        """

        self._transport.read_binary(2)  # Consume <CR><LF>

    # ------------------------------------------------------------------------
    # IEEE488.2 constants
    # ------------------------------------------------------------------------
    # *ESR and *ESE bits
    _ESR_OPERATION_COMPLETE = 0x01
    _ESR_REQUEST_CONTROL = 0x02
    _ESR_QUERY_ERROR = 0x04
    _ESR_DEVICE_DEPENDENT_ERROR = 0x08
    _ESR_EXECUTION_ERROR = 0x10
    _ESR_COMMAND_ERROR = 0x20
    _ESR_USER_REQUEST = 0x40
    _ESR_POWER_ON = 0x80

    # STATus:OPERation bits
    _STAT_OPER_CALIBRATING = 0x0001   # The instrument is currently performing a calibration
    _STAT_OPER_SETTLING = 0x0002      # The instrument is waiting for signals it controls to stabilize enough to begin measurements
    _STAT_OPER_RANGING = 0x0004       # The instrument is currently changing its range
    _STAT_OPER_SWEEPING = 0x0008      # A sweep is in progress
    _STAT_OPER_MEASURING = 0x0010     # The instrument is actively measuring
    _STAT_OPER_WAIT_TRIG = 0x0020     # The instrument is in a “wait for trigger” state of the trigger model
    _STAT_OPER_WAIT_ARM = 0x0040      # The instrument is in a “wait for arm” state of the trigger model
    _STAT_OPER_CORRECTING = 0x0080    # The instrument is currently performing a correction
    _STAT_OPER_INST_SUMMARY = 0x2000  # One of n multiple logical instruments is reporting OPERational status
    _STAT_OPER_PROG_RUNNING = 0x4000  # A user-defined program is currently in the run state

    # STATus:QUEStionable bits
    _STAT_QUES_VOLTAGE = 0x0001
    _STAT_QUES_CURRENT = 0x0002
    _STAT_QUES_TIME = 0x0004
    _STAT_QUES_POWER = 0x0008
    _STAT_QUES_TEMPERATURE = 0x0010
    _STAT_QUES_FREQUENCY = 0x0020
    _STAT_QUES_PHASE = 0x0040
    _STAT_QUES_MODULATION = 0x0080
    _STAT_QUES_CALIBRATION = 0x0100
    _STAT_QUES_INST_SUMMARY = 0x2000
    _STAT_QUES_COMMAND_WARNING = 0x4000
