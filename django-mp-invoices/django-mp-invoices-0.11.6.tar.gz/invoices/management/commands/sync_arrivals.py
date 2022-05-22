
from datetime import datetime, time

from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from invoices.models import Arrival, ArrivalItem, SaleItem

from apps.products.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):

        dev = User.objects.get(username='dev')

        for product in Product.objects.filter(stock__gt=0):

            arrival_sum = ArrivalItem.objects.filter(
                product=product
            ).aggregate(Sum('qty'))['qty__sum'] or 0

            sale_sum = SaleItem.objects.filter(
                product=product
            ).aggregate(Sum('qty'))['qty__sum'] or 0

            if sale_sum <= arrival_sum:
                continue

            params = {
                'creator': dev,
                'type': Arrival.TYPE_INCOME
            }

            created = product.created.date()

            created_min = timezone.make_aware(
                datetime.combine(created, time.min))
            created_max = timezone.make_aware(
                datetime.combine(created, time.max))

            try:
                arrival = Arrival.objects.filter(
                    created__range=(created_min, created_max), **params)[0]
            except IndexError:
                arrival = Arrival.objects.create(**params)

            arrival.add_item(
                product,
                qty=sale_sum - arrival_sum,
                update_product=False)

        print('Success')
