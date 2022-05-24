
from django.utils.translation import ugettext_lazy as _


DAYS_OF_WEEK = [
    _('Monday'),
    _('Tuesday'),
    _('Wednesday'),
    _('Thursday'),
    _('Friday'),
    _('Saturday'),
    _('Sunday')
]

ORDER_STATUS_NEW = 'new'
ORDER_STATUS_IN_PROGRESS = 'in_progress'
ORDER_STATUS_COMPLETED = 'completed'
ORDER_STATUS_CANCELLED = 'cancelled'

ORDER_STATUSES = (
    (ORDER_STATUS_NEW, _('New order')),
    (ORDER_STATUS_IN_PROGRESS, _('In progress')),
    (ORDER_STATUS_COMPLETED, _('Completed')),
    (ORDER_STATUS_CANCELLED, _('Cancelled')),
)

PAYMENT_METHOD_CASH = 'cash'
PAYMENT_METHOD_PRIVAT24 = 'privat24'
PAYMENT_METHOD_CASH_ON_DELIVERY = 'cash_on_delivery'
PAYMENT_METHOD_CASHLESS_PAYMENT = 'cashless_payment'

PAYMENT_METHODS = (
    (PAYMENT_METHOD_CASH, _('Cash payment')),
    (PAYMENT_METHOD_PRIVAT24, _('Online payment (Privat 24 / LiqPay)')),
    (PAYMENT_METHOD_CASH_ON_DELIVERY, _('Cash on delivery')),
    (
        PAYMENT_METHOD_CASHLESS_PAYMENT,
        _('Bank transfer (Transfer by details)')
    ),
)
