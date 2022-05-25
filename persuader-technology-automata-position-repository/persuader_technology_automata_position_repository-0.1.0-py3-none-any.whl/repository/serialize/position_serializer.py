from core.position.Position import Position


def serialize(position: Position) -> dict:
    serialized = {
        'instrument': position.instrument,
        'quantity': str(position.quantity),
        'instant': position.instant
    }
    serialize_exchanged_from(serialized, position.exchanged_from)
    return serialized


def serialize_exchanged_from(serialized_position, value):
    if value is not None:
        serialized_position['exchanged_from'] = value
