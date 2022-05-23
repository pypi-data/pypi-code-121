__all__ = ('LoanIssuePoint', 'LoanPaymentBodyPoint', 'LoanInterestsChargePoint', 'LoanPaymentInterestsPoint',
           'RewardChargePoint',
           )

from expressmoney.api import *
from .balances import *

SERVICE = 'accounting'
APP = 'operations'


class OperationContract(Contract):
    amount = serializers.DecimalField(max_digits=16, decimal_places=0, min_value=1, max_value=1000000000)
    is_reverse = serializers.BooleanField(default=False)
    department = serializers.IntegerField(min_value=1)
    analytical = serializers.IntegerField(min_value=1)


class LoanIssueCreateContract(OperationContract):
    pass


class LoanPaymentBodyCreateContract(OperationContract):
    pass


class LoanInterestsChargeCreateContract(OperationContract):
    pass


class LoanPaymentInterestsCreateContract(OperationContract):
    pass


class RewardChargeCreateContract(OperationContract):
    amount = serializers.DecimalField(max_digits=16, decimal_places=0, min_value=1, max_value=1000000000)
    is_reverse = serializers.BooleanField()


class LoanIssueID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'loan_issue'


class LoanPaymentBodyID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'loan_payment_body'


class LoanInterestsChargeID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'loan_interests_charge'


class LoanPaymentInterestsID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'loan_payment_interests'


class RewardChargeID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'reward_charge'


class LoanIssuePoint(CreatePointMixin, ContractPoint):
    _point_id = LoanIssueID()
    _create_contract = LoanIssueCreateContract

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        loan = self._payload.get('analytical')
        related_points.append(A48801BalanceAnalyticalPoint(self._user, loan))
        return related_points


class LoanPaymentBodyPoint(CreatePointMixin, ContractPoint):
    _point_id = LoanPaymentBodyID()
    _create_contract = LoanPaymentBodyCreateContract

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        loan = self._payload.get('analytical')
        related_points.append(A48801BalanceAnalyticalPoint(self._user, loan))
        return related_points


class LoanInterestsChargePoint(CreatePointMixin, ContractPoint):
    _point_id = LoanInterestsChargeID()
    _create_contract = LoanInterestsChargeCreateContract

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        loan = self._payload.get('analytical')
        related_points.append(A48802BalanceAnalyticalPoint(self._user, loan))
        return related_points


class LoanPaymentInterestsPoint(CreatePointMixin, ContractPoint):
    _point_id = LoanPaymentInterestsID()
    _create_contract = LoanPaymentInterestsCreateContract

    def _get_related_points(self) -> list:
        related_points = super()._get_related_points()
        loan = self._payload.get('analytical')
        related_points.append(P48809BalanceAnalyticalPoint(self._user, loan))
        return related_points


class RewardChargePoint(CreatePointMixin, ContractPoint):
    _point_id = RewardChargeID()
    _create_contract = RewardChargeCreateContract
