from enum import Enum


class InvalidInitializationInformation(Exception):
    pass


class InvalidCarrierName(Exception):
    pass


class CellPhone:
    """
    This class defines a cell phone (which can be texted to)
    """
    class Carrier(Enum):
        """
        This class defines a cell phone carrier
        """
        T_MOBILE = 'tmomail.net'
        ATT = 'txt.att.net'

        @staticmethod
        def from_string(name):
            """
            Converts a string to a Carrier
            :param name: the name for the Carrier (i.e. T_MOBILE)
            :return a Carrier object
            """
            if name == CellPhone.Carrier.ATT.name:
                return CellPhone.Carrier.ATT
            elif name == CellPhone.Carrier.T_MOBILE.name:
                return CellPhone.Carrier.T_MOBILE
            else:
                raise InvalidCarrierName(name)

    def __init__(self, carrier=None, number=None,
                 cfg_mgr=None,
                 section_heading='cell number',
                 phone_number_tag='phone_number',
                 carrier_tag='carrier'):
        """
        This constructor creates a CellPhone from either a number and Carrier, or a config file
        You must provide carrier and number together OR cfg_mgr
        :param carrier: the carrier of the CellPhone
        :param number: the number of the CellPhone
        :param cfg_mgr: the configuration manager for this file
        :param section_heading: specialized heading of the CellPhone (for deprecated configuration files)
        :param phone_number_tag: specialized phone number tag (for deprecated configuration files)
        :param carrier_tag: specialized carrier number tag (for deprecated configuration files)
        """
        self.carrier = carrier
        self.number = number
        self.cfg_mgr = cfg_mgr

        if cfg_mgr is None:
            if carrier is None or number is None:
                raise InvalidInitializationInformation('Both carrier and number must be provided if cfg_mgr is not')
        else:
            if carrier is not None or number is not None:
                raise InvalidInitializationInformation('Carrier and number may not be provided if cfg_mgr is')

        if cfg_mgr is not None:
            self.number = cfg_mgr.read_entry(section=section_heading,
                                             entry=phone_number_tag, default_value=1234567890)
            self.carrier = CellPhone.Carrier.from_string(cfg_mgr.read_entry(section=section_heading,
                                                         entry=carrier_tag, default_value=CellPhone.Carrier.ATT.value))

    def as_email(self):
        """
        :return this object as an email-able string
        """
        return '{}@{}'.format(self.number, self.carrier.value)
