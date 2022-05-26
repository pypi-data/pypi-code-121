from core.number.BigFloat import BigFloat
from core.position.PositionSlip import PositionSlip, Status
from coreutility.collection.dictionary_utility import as_data


def deserialize(position_slip) -> PositionSlip:
    if position_slip is not None:
        instrument = as_data(position_slip, 'instrument')
        quantity = BigFloat(as_data(position_slip, 'quantity'))
        status = as_data(position_slip, 'status')
        deserialized_position_slip = PositionSlip(instrument, quantity)
        set_status_as_available(deserialized_position_slip, status)
        return deserialized_position_slip


def set_status_as_available(deserialized_position_slip, value):
    if value is not None:
        result = [member for name, member in Status.__members__.items() if member.value == value]
        deserialized_position_slip.status = result[0]
