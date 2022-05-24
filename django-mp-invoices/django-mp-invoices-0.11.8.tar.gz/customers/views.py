
import csv
from datetime import datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from invoices.models import SaleItem, ArrivalItem
from customers.models import Customer
from customers.forms import AddCustomerForm


@staff_member_required
def get_customer_detail(request, customer_id):

    customer = get_object_or_404(Customer, id=customer_id)

    return render(request, 'customers/detail.html', {
        'object': customer,
        'sale_items': (
            SaleItem
                .objects
                .filter(invoice__customer=customer)
                .select_related('invoice')
                .order_by('-invoice__created')
        ),
        'arrival_items': (
            ArrivalItem
                .objects
                .filter(invoice__customer=customer)
                .select_related('invoice')
                .order_by('-invoice__created')
        ),
        **admin.site.each_context(request)
    })


@staff_member_required
def export_customers(request):

    file_name = datetime.now().strftime('%d.%m.%Y')

    response = HttpResponse(content_type='text/csv')
    response["Content-Disposition"] = (
        'attachment; filename="customers_{}.csv"'.format(file_name))

    writer = csv.writer(response)

    writer.writerow([
        'Name',
        'Phone',
        'Vin',
        'Discount'
    ])

    for customer in Customer.objects.all():
        writer.writerow([
            customer.name,
            customer.phone,
            customer.vin,
            '{}%'.format(customer.discount) if customer.discount else ''
        ])

    return response


@staff_member_required
def add_customer(request):

    form = AddCustomerForm(request.POST or None)

    status_code = 200

    if request.method == 'POST':

        if form.is_valid():

            customer = form.save()

            return JsonResponse({
                'message': _('Customer added'),
                'customer': {
                    'id': customer.pk,
                    'name': str(customer)
                }
            })
        else:
            status_code = 403

    return render(
        request,
        'customers/add.html',
        {'form': form, 'status_code': status_code},
        status=status_code)
