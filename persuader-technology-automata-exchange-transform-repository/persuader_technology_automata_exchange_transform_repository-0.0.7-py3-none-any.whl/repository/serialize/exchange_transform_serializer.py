from exchangetransformrepo.ExchangeTransform import ExchangeTransform


def serialize_exchange_transform(exchange_transform: ExchangeTransform) -> dict:
    serialized = {
        'instrument': exchange_transform.instrument
    }
    if exchange_transform.transform is not None:
        serialized['transform'] = exchange_transform.transform
    if exchange_transform.ignore:
        serialized['ignore'] = exchange_transform.ignore
    return serialized
