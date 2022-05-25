import logging
from typing import Optional

from core.position.Position import Position
from core.position.PositionSlip import Status
from positionrepo.repository.PositionRepository import PositionRepository
from positionrepo.repository.PositionSlipRepository import PositionSlipRepository

from position.provider.supplier.PositionSupplier import PositionSupplier


class PositionProvider:

    def __init__(self, position_supplier: PositionSupplier, position_repository: PositionRepository, position_slip_repository: PositionSlipRepository):
        self.log = logging.getLogger(__name__)
        self.position_supplier = position_supplier
        self.position_repository = position_repository
        self.position_slip_repository = position_slip_repository

    def updating_position(self):
        position_slip = self.position_slip_repository.retrieve()
        self.log.debug(f'Position Slip:[{position_slip}]')
        if position_slip is not None and position_slip.status is not Status.USED:
            self.log.debug(f'USING the Position Slip:[{position_slip}]')
            self.obtain_position_based_on_non_used_slip(position_slip)

    def obtain_position_based_on_non_used_slip(self, position_slip):
        positions = self.position_supplier.get_positions()
        position = self.choose_position_based_on_slip(positions, position_slip)
        if position is not None:
            self.log.debug(f'Position which is initiated from slip is now:[{position}]')
            self.use_position_slip(position_slip)
            self.position_repository.store(position)

    @staticmethod
    def choose_position_based_on_slip(positions, position_slip) -> Optional[Position]:
        eligible_positions = [p for p in positions if p.instrument == position_slip.instrument]
        if len(eligible_positions) > 0:
            position = eligible_positions[0]
            position.quantity = position_slip.quantity
            return position
        return None

    def use_position_slip(self, position_slip):
        position_slip.status = Status.USED
        self.position_slip_repository.store(position_slip)
