from core.position.PositionSlip import PositionSlip


def serialize(position_slip: PositionSlip) -> dict:
    serialized = {
        'instrument': position_slip.instrument,
        'quantity': str(position_slip.quantity),
        'status': position_slip.status.value
    }
    return serialized
