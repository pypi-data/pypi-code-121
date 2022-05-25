"""card.py
"""

# Standard library imports

# Third party imports
from smartcard import CardType as _CardType
from smartcard.CardRequest import CardRequest as _CardRequest
from smartcard.Exceptions import CardRequestTimeoutException as _CardRequestTimeoutException
from smartcard.scard import \
    SCARD_SHARE_SHARED as _SCARD_SHARE_SHARED,\
    SCARD_SHARE_EXCLUSIVE as _SCARD_SHARE_EXCLUSIVE,\
    SCARD_SHARE_DIRECT as _SCARD_SHARE_DIRECT,\
    SCARD_LEAVE_CARD as _SCARD_LEAVE_CARD,\
    SCARD_RESET_CARD as _SCARD_RESET_CARD,\
    SCARD_UNPOWER_CARD as _SCARD_UNPOWER_CARD,\
    SCARD_EJECT_CARD as _SCARD_EJECT_CARD
from smartcard.CardConnection import CardConnection as _CardConnection
from smartcard.CardService import CardService as _CardService
from smartcard.CardMonitoring import \
    CardMonitor as _CardMonitor,\
    CardObserver as _CardObserver

# Local application imports
from common.intlist import to_hstr as _to_hstr
from common.hstr import \
    to_intlist as _to_intlist,\
    minimum as _min,\
    clean as _clean

def connect(atr=None,
            atr_mask=None,
            new_card_only=False,
            readers=None,
            timeout=None,
            protocol=None,
            mode='SCARD_SHARE_EXCLUSIVE',
            disposition='SCARD_LEAVE_CARD',
            trace=None) -> _CardService:
    """connect()
    """
    if atr is None:
        # Requesting any card
        _trace(trace, "Requesting any card")
        card_type = _CardType.AnyCardType()
    elif atr_mask is None:
        # Requesting a card with a specific ATR
        _trace(trace, "Requesting a card with a specific ATR")
        card_type = _CardType.ATRCardType(_to_intlist(atr))
    else:
        # Requesting a card with a masked ATR
        _trace(trace, "Requesting a card with a masked ATR")
        card_type = _CardType.ATRCardType(
            _to_intlist(atr, command_name='card.connect()', hstr_name='atr'),
            _to_intlist(atr_mask, command_name='card.connect()', hstr_name='atr_mask'))

    card_request = _CardRequest(
        newcardonly=new_card_only,
        readers=readers,
        cardType=card_type,
        timeout=timeout)

    if protocol is not None:
        _trace(trace, F"Requested protocol: {protocol}")
        protocol = {'SCARD_PROTOCOL_T0': _CardConnection.T0_protocol,
                    'SCARD_PROTOCOL_T1': _CardConnection.T1_protocol,
                    'SCARD_PROTOCOL_T0_OR_T1':
                    _CardConnection.T0_protocol |
                    _CardConnection.T1_protocol,
                    'SCARD_PROTOCOL_RAW': _CardConnection.RAW_protocol}[protocol]

    _trace(trace, F"Requested mode: {mode}")
    mode = {'SCARD_SHARE_SHARED': _SCARD_SHARE_SHARED,
            'SCARD_SHARE_EXCLUSIVE': _SCARD_SHARE_EXCLUSIVE,
            'SCARD_SHARE_DIRECT': _SCARD_SHARE_DIRECT}[mode]

    _trace(trace, F"Requested disposition: {disposition}")
    disposition = {'SCARD_LEAVE_CARD': _SCARD_LEAVE_CARD,
                   'SCARD_RESET_CARD': _SCARD_RESET_CARD,
                   'SCARD_UNPOWER_CARD': _SCARD_UNPOWER_CARD,
                   'SCARD_EJECT_CARD': _SCARD_EJECT_CARD}[disposition]

    try:
        _trace(trace, F"Card request will timeout after {timeout}s")
        card_service = card_request.waitforcard()
        card_service.connection.connect(
            protocol=protocol,
            mode=mode,
            disposition=disposition)
    except _CardRequestTimeoutException as err:
        return '', err
    else:
        _trace(trace, F"Card {get_atr(card_service)} detected on {get_reader(card_service)}")
        return card_service, ''


def get_reader(card_service: _CardService) -> str:
    """get_Reader()
    """
    return card_service.connection.getReader()


def get_atr(card_service: _CardService) -> str:
    """getATR()
    """
    return _to_hstr(card_service.connection.getATR())


def get_protocol(card_service: _CardService) -> str:
    """getProtocol()
    """
    return {_CardConnection.T0_protocol: 'T=0',
            _CardConnection.T1_protocol: 'T=1',
            _CardConnection.T0_protocol&_CardConnection.T1_protocol: 'T=0 and T=1',
            _CardConnection.RAW_protocol: 'RAW'}[card_service.connection.getProtocol()]


def transmit(card_service: _CardService, hstr: str, trace=None):
    """transmit()
    """
    _trace(trace, F"=>card: {hstr}")

    data, sw1, sw2 = card_service.connection.transmit(_to_intlist(hstr), card_service.connection.getProtocol())
    data, sw1, sw2 = _to_hstr(data), F"{sw1:02X}", F"{sw2:02X}"

    if data == '':
        _trace(trace, F"<=card: {sw1+sw2}")
    else:
        _trace(trace, F"<=card: {data} {sw1+sw2}")

    return [data, sw1, sw2], ''


def send_apdu(card_service: _CardService, apdu: dict, trace=None):
    """send_apdu()
    """
    # Extracting APDU header, data, length field from apdu dictionary
    if 'header' in apdu:
        header = _clean(apdu['header'])
    else:
        CLA = _clean(apdu['CLA'])
        INS = _clean(apdu['INS'])
        P1 = _clean(apdu['P1'])
        P2 = _clean(apdu['P2'])
        header = CLA + INS + P1 + P2
    
    data = apdu.get('data', None)
    Le = apdu.get('Le', None)
    
    protocol = get_protocol(card_service)
    if protocol not in ['T=0', 'T=1']:
        return ['', '', ''], 'Unsupported protocol: ' + protocol

    if data is None:
        # Case 1
        if Le is None:
            if protocol == 'T=0':
                return _send_apdu_T0_case_1(card_service, header, trace)
            if protocol == 'T=1':
                return transmit(card_service, header, trace)
        # Case 2S
        Le = _clean(Le, 'send_apdu()', 'Le')
        if len(Le) == 2:
            if protocol == 'T=0':
                return _send_apdu_T0_case_2s(card_service, header, Le, trace)
            if protocol == 'T=1':
                return transmit(card_service, header + Le, trace)
        # Case 2E
        if len(Le) == 6:
            if protocol == 'T=0':
                return ['', '', ''], 'Unsupported case 2E with protocol T=0'
            if protocol == 'T=1':
                return transmit(card_service, header + Le, trace)

    data = _clean(data, 'send_apdu()', 'data')
    Lc = len(data)//2
    if Le is None:
        # Case 3S
        if Lc < 256:
            Lc = F"{Lc:02X}"
            if protocol == 'T=0':
                return _send_apdu_T0_case_3s(card_service, header, Lc, data, trace)
            if protocol == 'T=1':
                return transmit(card_service, header + Lc + data, trace)
        # Case 3E
        if Lc < 65536:
            Lc = F"00{Lc:04X}"
            if protocol == 'T=0':
                return ['', '', ''], 'Unsupported case 3E with protocol T=0'
            if protocol == 'T=1':
                return transmit(card_service, header + Lc + data, trace)
        # Data field too long
        else:
            return ['', '', ''], F"Data field too long: {Lc:X}"

    # Case 4S
    if Lc < 256 and len(Le) == 2:
        if protocol == 'T=0':
            return _send_apdu_T0_case_4s(card_service, header, F"{Lc:02X}", data, Le, trace)
        if protocol == 'T=1':
            return transmit(card_service, header + F"{Lc:02X}" + data + Le, trace)
    # Case 4E
    if Lc < 65536 and len(Le) == 6:
        if protocol == 'T=0':
            return ['', '', ''], 'Unsupported case 4E with protocol T=0'
        if protocol == 'T=1':
            return transmit(card_service, header + F"00{Lc:04X}" + data + Le, trace)

    return ['', '', ''], F'Unsupported case with short and extended lengths: Lc = {Lc:X}, Le = {Le}'


def _send_apdu_T0_case_1(card_service: _CardService, header: str, trace=None):
    """send_apdu_T0_case_1():
    """
    _trace(trace, "Case 1 Command (T=0)")
    return transmit(card_service.connection, header, trace)


def _send_apdu_T0_case_2s(card_service: _CardService, header: str, Le: str, trace=None):
    """send_apdu_T0_case_2s():
    """
    # Short Le field
    if len(Le) == 2:
        pass
    # Wrong Le field
    else:
        return ['', '', ''], 'Wrong Le value' + Le

    _trace(trace, "Case 2 Command (T=0)")
    [data, SW1, SW2], _ = transmit(card_service, header + Le, trace)
    # Case 2S.1—Process completed: Ne accepted
    if SW1+SW2 == '9000':
        return [data, SW1, SW2], ''
    # Case 2S.2—Process aborted: Ne definitively not accepted
    if SW1+SW2 == '6700':
        return ['', SW1, SW2], 'Error—Process aborted: Ne definitively not accepted (6700)'
    # Case 2S.3—Process aborted; Ne not accepted, Na indicated
    if SW1 == '6C':
        return transmit(card_service, header + SW2, trace)
    # Case 2S.4—SW12 = '9XYZ', except for '9000'
    if SW1.startswith('9'):
        return [data, SW1, SW2], ''

    return [data, SW1, SW2], 'Unknown command case'


def _send_apdu_T0_case_3s(card_service: _CardService, header: str, Lc: str, data: str, trace=None):
    """send_apdu_T0_case_3s():
    """
    # Short Lc field
    if len(Lc) == 2:
        pass
    # Data field too long
    else:
        return ['', '', ''], "Data field too long: " + Lc

    _trace(trace, "Case 3 Command (T=0)")
    return transmit(card_service, header + Lc + data, trace)


def _send_apdu_T0_case_4s(card_service: _CardService, header: str, Lc: str, data: str, Le: str, trace=None):
    """send_apdu_T0_case_4s():
    """
    # Short Lc field
    if len(Lc) == 2:
        pass
    # Data field too long
    else:
        return ['', '', ''], "Data field too long: " + Lc

    # Short Le field
    if len(Le) == 2:
        pass
    # Wrong Le field
    else:
        return ['', '', ''], 'Wrong Le value' + Le

    _trace(trace, "Case 4 Command (T=0)")
    [data, SW1, SW2], _ = transmit(card_service, header + Lc + data + Le, trace)
    # Case 4S.1—Process aborted
    if SW1[0] == '6' and SW1[1] in '0456789ABCDEF':
        return [data, SW1, SW2], F'Error—Process aborted ({SW1+SW2})'
    # Case 4S.2—Process completed
    if SW1+SW2 == '9000':
        # Send GET RESPONSE
        return _send_apdu_T0_case_2s(card_service, header[0:2] + 'C00000', Le, trace)
    # Case 4S.3—Process completed with information added
    if SW1 == '61':
        if Le == '00':
            Ne = '100'
        else:
            Ne = Le
        return _send_apdu_T0_case_2s(card_service, header[0:2] + 'C00000', _min(Ne, SW2), trace)
    # Case 4S.4—SW12 = '62XY', or '63XY', or '9XYZ', except for '9000'
    if SW1.startswith('9') or SW1 in ['62', '63']:
        return [data, SW1, SW2], ''

    return [data, SW1, SW2], 'Unknown command case'


def disconnect(card_service: _CardService):
    """disconnect()
    """
    card_service.connection.disconnect()

#
# Helper functions
#

def _trace(trace, message:str):
    if trace is not None:
        trace(message)