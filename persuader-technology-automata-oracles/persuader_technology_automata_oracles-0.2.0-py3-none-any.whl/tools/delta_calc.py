from typing import Optional

from core.exchange.InstrumentExchange import InstrumentExchange
from core.oracle.Prediction import Prediction
from coreutility.number.BigFloatSubtract import BigFloatSubtract
from exchange.rate.InstantRate import InstantRate


def calc_delta(instant_rate: InstantRate, other_instant_rate: InstantRate):
    return BigFloatSubtract(instant_rate.rate, other_instant_rate.rate).result()


def calc_delta_prediction(instant_rate: InstantRate, other_instant_rate: InstantRate, instrument_exchange: InstrumentExchange) -> Optional[Prediction]:
    if instant_rate is not None and other_instant_rate is not None:
        delta = calc_delta(instant_rate, other_instant_rate)
        (instrument, to_instrument) = instrument_exchange
        return Prediction(outcome=[instrument, to_instrument], percent=delta)
