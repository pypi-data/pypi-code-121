import re
import logging

from collections import OrderedDict
import dataclasses
from datetime import datetime

from zos_utilities.logical_cpu import Logical_CPU


@dataclasses.dataclass
class LPAR:
    """
    Represents an IBM z/OS LPAR
    """

    logical_processors: dict = dataclasses.field(default_factory=OrderedDict)
    physical_cpus: dict = dataclasses.field(default_factory=OrderedDict)
    hiperdispatch: bool = None
    mt_mode: bool = None
    cp_mt_mode: bool = None
    ziip_mt_mode: bool = None
    cpc_nd: str = None
    cpc_si: str = None
    cpc_model: str = None
    cpc_id: str = None
    cpc_name: str = None
    lpar_name: str = None
    lpar_id: str = None
    css_id: str = None
    mif_id: str = None

    name: str = None
    part_id: str = None
    partition_number: str = None
    CPC: str = None
    shared_processors: int = None
    active: bool = None
    IPL_volume: bool = None
    os: bool = None
    os_name: bool = None
    os_level: bool = None
    last_updated: datetime = None
    url: str = None
    start_update: datetime = None
    finish_update: datetime = None
    status: str = None

    number_general_cpus: int = None
    number_reserved_general_cpus: int = None
    number_general_cores: int = None
    number_reserved_general_cores: int = None

    number_ziip_cpus: int = None
    number_reserved_ziip_cpus: int = None
    number_ziip_cores: int = None
    number_reserved_ziip_cores: int = None

    number_ifl_cpus: int = None
    number_reserved_ifl_cpus: int = None
    number_ifl_cores: int = None
    number_reserved_ifl_cores: int = None

    number_icf_cpus: int = None
    number_reserved_icf_cpus: int = None
    number_icf_cores: int = None
    number_reserved_icf_cores: int = None

    general_cp_weight_initial: int = None
    general_cp_weight_current: int = None
    general_cp_weight_minimum: int = None
    general_cp_weight_maximum: int = None

    zaap_weight_initial: int = None
    zaap_weight_current: int = None
    zaap_weight_minimum: int = None
    zaap_weight_maximum: int = None

    ziip_weight_initial: int = None
    ziip_weight_current: int = None
    ziip_weight_minimum: int = None
    ziip_weight_maximum: int = None

    ifl_weight_initial: int = None
    ifl_weight_current: int = None
    ifl_weight_minimum: int = None
    ifl_weight_maximum: int = None

    icf_weight_initial: int = None
    icf_weight_current: int = None
    icf_weight_minimum: int = None
    icf_weight_maximum: int = None

    storage: int = None

    initial_central_storage: int = None
    current_central_storage: int = None
    maximum_central_storage: int = None

    def parse_d_m_core(self, iee174i_message):
        """
        Takes the output of the response to 'D M=CORE' and builds a representation of the
        system logical processor state at that time

        :param core_status_message: The output of the message you want parsed
        :return: Updates the internal state information of the lpar
        """

        logger = logging.getLogger(__name__)

        if iee174i_message[0].split()[0] != "IEE174I":
            message = str("Incorrect message passed in; expected IEE174I, got %s" %
                          iee174i_message[0].split()[0])
            logging.error(message)
            raise LPARException(message)

        split_line_1 = iee174i_message[1].split()

        logger.debug(split_line_1)

        hd_value = split_line_1[2][3]

        if hd_value == "Y":
            self.hiperdispatch = True
        elif hd_value == "N":
            self.hiperdispatch = False
        else:
            message = str("HD= should be Y or N; got %s" % hd_value)
            logging.error(message)
            raise LPARException(message)

        mt_value = split_line_1[3][3]

        if split_line_1[3][0:3] != "MT=":
            message = ("MT= was not in the correct place; got %s" % split_line_1[3][0:3])
            logging.error(message)
            raise LPARException(message)

        if mt_value.isdigit():
            self.mt_mode = int(mt_value)
        else:
            message = ("MT= should be a number; got %s" % mt_value)
            logging.error(message)
            raise LPARException(message)

        if self.mt_mode == 1:
            pass
        else:
            cp_mt_mode = split_line_1[5][3]

            if split_line_1[5][0:3] != "CP=":
                message = "CP= was not in the correct place"
                logging.error(message)
                raise LPARException(message)

            if split_line_1[5][3].isdigit():
                self.cp_mt_mode = int(cp_mt_mode)
            else:
                message = ("CP= should be a number; got %s" % cp_mt_mode)
                logging.error(message)
                raise LPARException(message)

            ziip_mt_mode = split_line_1[6][5]

            if split_line_1[6][0:5] != "zIIP=":
                message = ("zIIP= was not in the correct place; got %s" % split_line_1[6][0:5])
                logging.error(message)
                raise LPARException(message)

            if ziip_mt_mode.isdigit():
                self.ziip_mt_mode = int(ziip_mt_mode)
            else:
                message = ("zIIP= should be a number, got %s" % ziip_mt_mode)
                logging.error(message)
                raise LPARException(message)

        core_re = re.compile(
            '(?P<coreid>[0-9A-F]{4})  (?P<wlmmanaged>.)(?P<online>.)(?P<type>.)  '
            '(?P<lowid>[0-9A-F]{4})-(?P<highid>[0-9A-F]{4})(  (?P<polarity>.)(?P<parked>.)'
            '  (?P<subclassmask>[0-9A-F]{4})  (?P<state1>.)(?P<state2>.))?')

        linenum = 3

        for linenum, line in enumerate(iee174i_message[3:], start=3):

            core_info = core_re.search(line)

            if core_info is None:
                break
            else:
                core = Logical_CPU()

                core.coreid = core_info.group("coreid")

                if core_info.group("online") == "+":
                    core.online = True
                else:
                    core.online = False

                if core_info.group("type") == " ":
                    core.type = "CP"
                elif core_info.group("type") == "I":
                    core.type = "zIIP"

                core.lowid = core_info.group("lowid")
                core.highid = core_info.group("highid")

                core.polarity = core_info.group("polarity")

                if core_info.group("parked") == "P":
                    core.parked = True
                else:
                    core.parked = False

                core.subclassmask = core_info.group("subclassmask")

                if core_info.group("state1") == "+":
                    core.core_1_state = "online"
                elif core_info.group("state1") == "N":
                    core.core_1_state = "not_available"
                elif core_info.group("state1") == "-":
                    core.core_1_state = "offline"

                if core_info.group("state2") == "+":
                    core.core_2_state = "online"
                elif core_info.group("state2") == "N":
                    core.core_2_state = "not_available"
                elif core_info.group("state2") == "-":
                    core.core_2_state = "offline"

                self.logical_processors[core.coreid] = core

        linenum += 1

        if iee174i_message[linenum].lstrip().startswith("CPC ND = "):
            self.cpc_nd = iee174i_message[linenum].lstrip()[9:].rstrip()
        else:
            error = ("line didn't start with CPC ND =; got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)

        linenum += 1

        if iee174i_message[linenum].lstrip().startswith("CPC SI = "):
            self.cpc_si = iee174i_message[linenum].lstrip()[9:].rstrip()
        else:
            error = ("line didn't start with CPC SI =; got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)

        linenum += 1

        if iee174i_message[linenum].lstrip().startswith("Model: "):
            self.cpc_model = iee174i_message[linenum].lstrip()[7:].rstrip()
        else:
            error = ("line didn't start with Model =; got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)

        linenum += 1

        if iee174i_message[linenum].lstrip().startswith("CPC ID = "):
            self.cpc_id = iee174i_message[linenum].lstrip()[9:].rstrip()
        else:
            error = ("line didn't start with CPC ID = ;  got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)

        linenum += 1

        if iee174i_message[linenum].lstrip().startswith("CPC NAME = "):
            self.cpc_name = iee174i_message[linenum].lstrip()[11:].rstrip()
        else:
            error = ("line didn't start with CPC NAME = ;  got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)

        linenum += 1

        if iee174i_message[linenum].lstrip().startswith("LP NAME = "):
            self.lpar_name = iee174i_message[linenum].lstrip()[10:14].rstrip()
        else:
            error = ("line didn't start with LP NAME = ;  got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)

        if iee174i_message[linenum][21:].lstrip().startswith("LP ID = "):
            self.lpar_id = iee174i_message[linenum].lstrip()[29:].rstrip()
        else:
            error = ("LP ID not where I expected; got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)

        linenum += 1

        if iee174i_message[linenum].lstrip().startswith("CSS ID  = "):
            self.css_id = iee174i_message[linenum].lstrip()[10:].rstrip()
        else:
            error = ("line didn't start with CSS ID = ;  got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)

        linenum += 1

        if iee174i_message[linenum].lstrip().startswith("MIF ID  = "):
            self.mif_id = iee174i_message[linenum].lstrip()[10:].rstrip()
        else:
            error = ("line didn't start with MIF ID = ;  got %s" % iee174i_message[linenum])
            logger.error(error)
            raise LPARException(error)


class LPARException(Exception):
    pass
