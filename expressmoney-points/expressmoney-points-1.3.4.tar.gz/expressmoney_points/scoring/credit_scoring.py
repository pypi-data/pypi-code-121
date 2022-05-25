__all__ = ('ProfileScoringPoint', 'OrderScoringPoint', 'NbkiDatasetPoint')

from expressmoney.api import *


SERVICE = 'scoring'
APP = 'credit_scoring'


class ProfileScoringCreateContract(Contract):
    pass


class ProfileScoringReadContract(Contract):
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    score = serializers.DecimalField(max_digits=3, decimal_places=2)
    credit_dataset = serializers.IntegerField(min_value=1)


class ProfileScoringResponseContract(ProfileScoringReadContract):
    pass


class OrderScoringCreateContract(Contract):
    order_id = serializers.IntegerField(min_value=1)


class OrderScoringResponseContract(Contract):
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    score = serializers.DecimalField(max_digits=3, decimal_places=2)
    order_id = serializers.IntegerField(min_value=1)


class OrderScoringReadContract(OrderScoringResponseContract):
    pass


class NbkiDatasetReadContract(Contract):
    id = serializers.IntegerField(min_value=1)
    updated = serializers.DateField()
    user_id = serializers.IntegerField(min_value=1)
    # System fields
    pdf = serializers.CharField(max_length=256, allow_blank=True)
    xml = serializers.CharField(max_length=256, allow_blank=True)
    # Expressmoney features
    loan_total = serializers.IntegerField()
    loan_first = serializers.IntegerField()
    loan_last = serializers.IntegerField()
    loan_between = serializers.IntegerField()
    loan_interests_sum = serializers.IntegerField()
    loan_interests_mean = serializers.IntegerField()
    loan_body_sum = serializers.IntegerField()
    loan_body_mean = serializers.IntegerField()
    # NBKI features
    total_accounts_mfo_new = serializers.IntegerField()
    total_accounts_mfo_old = serializers.IntegerField()
    total_accounts_bank_new = serializers.IntegerField()
    total_accounts_bank_old = serializers.IntegerField()
    total_accounts_other_new = serializers.IntegerField()
    total_accounts_other_old = serializers.IntegerField()
    total_accounts_active_balance_current_balance_more_0_mfo_new = serializers.IntegerField()
    total_accounts_active_balance_current_balance_more_0_mfo_old = serializers.IntegerField()
    total_accounts_active_balance_current_balance_more_0_bank_new = serializers.IntegerField()
    total_accounts_active_balance_current_balance_more_0_bank_old = serializers.IntegerField()
    total_accounts_active_balance_current_balance_more_0_other_new = serializers.IntegerField()
    total_accounts_active_balance_current_balance_more_0_other_old = serializers.IntegerField()
    total_accounts_active_balance_current_balance_0_mfo_new = serializers.IntegerField()
    total_accounts_active_balance_current_balance_0_mfo_old = serializers.IntegerField()
    total_accounts_active_balance_current_balance_0_bank_new = serializers.IntegerField()
    total_accounts_active_balance_current_balance_0_bank_old = serializers.IntegerField()
    total_accounts_active_balance_current_balance_0_other_new = serializers.IntegerField()
    total_accounts_active_balance_current_balance_0_other_old = serializers.IntegerField()
    total_accounts_negative_rating_mfo_new = serializers.IntegerField()
    total_accounts_negative_rating_mfo_old = serializers.IntegerField()
    total_accounts_negative_rating_bank_new = serializers.IntegerField()
    total_accounts_negative_rating_bank_old = serializers.IntegerField()
    total_accounts_negative_rating_other_new = serializers.IntegerField()
    total_accounts_negative_rating_other_old = serializers.IntegerField()
    total_accounts_positive_rating_mfo_new = serializers.IntegerField()
    total_accounts_positive_rating_mfo_old = serializers.IntegerField()
    total_accounts_positive_rating_bank_new = serializers.IntegerField()
    total_accounts_positive_rating_bank_old = serializers.IntegerField()
    total_accounts_positive_rating_other_new = serializers.IntegerField()
    total_accounts_positive_rating_other_old = serializers.IntegerField()
    total_accounts_past_due_current_balance_more_0_mfo_new = serializers.IntegerField()
    total_accounts_past_due_current_balance_more_0_mfo_old = serializers.IntegerField()
    total_accounts_past_due_current_balance_more_0_bank_new = serializers.IntegerField()
    total_accounts_past_due_current_balance_more_0_bank_old = serializers.IntegerField()
    total_accounts_past_due_current_balance_more_0_other_new = serializers.IntegerField()
    total_accounts_past_due_current_balance_more_0_other_old = serializers.IntegerField()
    total_accounts_past_due_current_balance_0_mfo_new = serializers.IntegerField()
    total_accounts_past_due_current_balance_0_mfo_old = serializers.IntegerField()
    total_accounts_past_due_current_balance_0_bank_new = serializers.IntegerField()
    total_accounts_past_due_current_balance_0_bank_old = serializers.IntegerField()
    total_accounts_past_due_current_balance_0_other_new = serializers.IntegerField()
    total_accounts_past_due_current_balance_0_other_old = serializers.IntegerField()
    total_accounts_closed_mfo_new = serializers.IntegerField()
    total_accounts_closed_mfo_old = serializers.IntegerField()
    total_accounts_closed_bank_new = serializers.IntegerField()
    total_accounts_closed_bank_old = serializers.IntegerField()
    total_accounts_closed_other_new = serializers.IntegerField()
    total_accounts_closed_other_old = serializers.IntegerField()
    date_last_account_mfo_new = serializers.IntegerField()
    date_last_account_mfo_old = serializers.IntegerField()
    date_last_account_bank_new = serializers.IntegerField()
    date_last_account_bank_old = serializers.IntegerField()
    date_last_account_other_new = serializers.IntegerField()
    date_last_account_other_old = serializers.IntegerField()
    date_first_account_mfo_new = serializers.IntegerField()
    date_first_account_mfo_old = serializers.IntegerField()
    date_first_account_bank_new = serializers.IntegerField()
    date_first_account_bank_old = serializers.IntegerField()
    date_first_account_other_new = serializers.IntegerField()
    date_first_account_other_old = serializers.IntegerField()
    total_amount_credit_limit_mfo_new = serializers.IntegerField()
    total_amount_credit_limit_mfo_old = serializers.IntegerField()
    total_amount_credit_limit_bank_new = serializers.IntegerField()
    total_amount_credit_limit_bank_old = serializers.IntegerField()
    total_amount_credit_limit_other_new = serializers.IntegerField()
    total_amount_credit_limit_other_old = serializers.IntegerField()
    total_amount_current_balance_mfo_new = serializers.IntegerField()
    total_amount_current_balance_mfo_old = serializers.IntegerField()
    total_amount_current_balance_bank_new = serializers.IntegerField()
    total_amount_current_balance_bank_old = serializers.IntegerField()
    total_amount_current_balance_other_new = serializers.IntegerField()
    total_amount_current_balance_other_old = serializers.IntegerField()
    total_amount_past_due_balance_mfo_new = serializers.IntegerField()
    total_amount_past_due_balance_mfo_old = serializers.IntegerField()
    total_amount_past_due_balance_bank_new = serializers.IntegerField()
    total_amount_past_due_balance_bank_old = serializers.IntegerField()
    total_amount_past_due_balance_other_new = serializers.IntegerField()
    total_amount_past_due_balance_other_old = serializers.IntegerField()
    total_amount_past_due_balance_active_mfo_new = serializers.IntegerField()
    total_amount_past_due_balance_active_mfo_old = serializers.IntegerField()
    total_amount_past_due_balance_active_bank_new = serializers.IntegerField()
    total_amount_past_due_balance_active_bank_old = serializers.IntegerField()
    total_amount_past_due_balance_active_other_new = serializers.IntegerField()
    total_amount_past_due_balance_active_other_old = serializers.IntegerField()
    total_amount_outstanding_balance_mfo_new = serializers.IntegerField()
    total_amount_outstanding_balance_mfo_old = serializers.IntegerField()
    total_amount_outstanding_balance_bank_new = serializers.IntegerField()
    total_amount_outstanding_balance_bank_old = serializers.IntegerField()
    total_amount_outstanding_balance_other_new = serializers.IntegerField()
    total_amount_outstanding_balance_other_old = serializers.IntegerField()
    total_amount_scheduled_monthly_pay_mfo_new = serializers.IntegerField()
    total_amount_scheduled_monthly_pay_mfo_old = serializers.IntegerField()
    total_amount_scheduled_monthly_pay_bank_new = serializers.IntegerField()
    total_amount_scheduled_monthly_pay_bank_old = serializers.IntegerField()
    total_amount_scheduled_monthly_pay_other_new = serializers.IntegerField()
    total_amount_scheduled_monthly_pay_other_old = serializers.IntegerField()
    total_num_days_30_mfo_new = serializers.IntegerField()
    total_num_days_30_mfo_old = serializers.IntegerField()
    total_num_days_30_bank_new = serializers.IntegerField()
    total_num_days_30_bank_old = serializers.IntegerField()
    total_num_days_30_other_new = serializers.IntegerField()
    total_num_days_30_other_old = serializers.IntegerField()
    total_num_days_60_mfo_new = serializers.IntegerField()
    total_num_days_60_mfo_old = serializers.IntegerField()
    total_num_days_60_bank_new = serializers.IntegerField()
    total_num_days_60_bank_old = serializers.IntegerField()
    total_num_days_60_other_new = serializers.IntegerField()
    total_num_days_60_other_old = serializers.IntegerField()
    total_num_days_90_mfo_new = serializers.IntegerField()
    total_num_days_90_mfo_old = serializers.IntegerField()
    total_num_days_90_bank_new = serializers.IntegerField()
    total_num_days_90_bank_old = serializers.IntegerField()
    total_num_days_90_other_new = serializers.IntegerField()
    total_num_days_90_other_old = serializers.IntegerField()
    total_pay_late_days_1_mfo_new = serializers.IntegerField()
    total_pay_late_days_1_mfo_old = serializers.IntegerField()
    total_pay_late_days_1_bank_new = serializers.IntegerField()
    total_pay_late_days_1_bank_old = serializers.IntegerField()
    total_pay_late_days_1_other_new = serializers.IntegerField()
    total_pay_late_days_1_other_old = serializers.IntegerField()
    total_pay_late_more_days_30_mfo_new = serializers.IntegerField()
    total_pay_late_more_days_30_mfo_old = serializers.IntegerField()
    total_pay_late_more_days_30_bank_new = serializers.IntegerField()
    total_pay_late_more_days_30_bank_old = serializers.IntegerField()
    total_pay_late_more_days_30_other_new = serializers.IntegerField()
    total_pay_late_more_days_30_other_old = serializers.IntegerField()
    total_pay_by_agreement_mfo_new = serializers.IntegerField()
    total_pay_by_agreement_mfo_old = serializers.IntegerField()
    total_pay_by_agreement_bank_new = serializers.IntegerField()
    total_pay_by_agreement_bank_old = serializers.IntegerField()
    total_pay_by_agreement_other_new = serializers.IntegerField()
    total_pay_by_agreement_other_old = serializers.IntegerField()
    average_time_obtaining_loan_mfo_new = serializers.IntegerField()
    average_time_obtaining_loan_mfo_old = serializers.IntegerField()
    average_time_obtaining_loan_bank_new = serializers.IntegerField()
    average_time_obtaining_loan_bank_old = serializers.IntegerField()
    average_time_obtaining_loan_other_new = serializers.IntegerField()
    average_time_obtaining_loan_other_old = serializers.IntegerField()
    total_inquiries_mfo = serializers.IntegerField()
    total_recent_inquiries_days_30_mfo = serializers.IntegerField()
    total_recent_inquiries_days_365_mfo = serializers.IntegerField()


class ProfileScoringID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'profile_scoring'


class OrderScoringID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'order_scoring'


class NbkiDatasetID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'nbki_dataset'


class ProfileScoringPoint(ListPointMixin, ResponseMixin, CreatePointMixin, ContractPoint):
    _point_id = ProfileScoringID()
    _create_contract = ProfileScoringCreateContract
    _response_contract = ProfileScoringResponseContract
    _read_contract = ProfileScoringReadContract


class OrderScoringPoint(ListPointMixin, ResponseMixin, CreatePointMixin, ContractPoint):
    _point_id = OrderScoringID()
    _read_contract = OrderScoringReadContract
    _create_contract = OrderScoringCreateContract
    _response_contract = OrderScoringResponseContract


class NbkiDatasetPoint(ListPointMixin, ContractPoint):
    _point_id = NbkiDatasetID()
    _read_contract = NbkiDatasetReadContract
