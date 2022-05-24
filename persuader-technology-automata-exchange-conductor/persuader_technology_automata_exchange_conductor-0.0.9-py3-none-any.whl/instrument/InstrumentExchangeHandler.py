from exchange.InstrumentExchangesHolder import InstrumentExchangesHolder
from exchangerepo.repository.InstrumentExchangeRepository import InstrumentExchangeRepository


class InstrumentExchangeHandler:

    def __init__(self, repository: InstrumentExchangeRepository):
        self.repository = repository

    def obtain_holder(self) -> InstrumentExchangesHolder:
        return self.repository.retrieve()

    def update_holder(self, holder: InstrumentExchangesHolder):
        self.repository.store(holder)
