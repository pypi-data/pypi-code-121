
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from services.models import Service, ServiceCategory


class ServicesService(object):

    def __init__(self, user):
        self._user = user
        self._check_access()

    def get_service(self, service_id):
        try:
            return Service.objects.get(pk=service_id)
        except ObjectDoesNotExist:
            raise Exception(_('Service not found'))

    def add_service(self, sale, service_item):

        try:
            service = Service.objects.get(
                sale=sale,
                item=service_item
            )
            service.qty += 1
        except Service.DoesNotExist:
            service = Service(
                customer=sale.customer,
                sale=sale,
                item=service_item,
                price=service_item.price
            )

        service.save()

        return service

    def get_categories(self):
        return (
            ServiceCategory
                .objects
                .all()
                .prefetch_related('items')
        )

    def _check_access(self):
        if not self._user.is_staff:
            raise Exception(_('Access denied'))
