
from django.shortcuts import get_object_or_404, HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.views.decorators import staff_member_required

from pagination import paginate

from cap.decorators import admin_render_view
from cap.views import render

from rest_framework.decorators import api_view
from rest_framework.response import Response

from djforms import get_clean_data
from invoice_products import forms

from apps.products.models import Product


def get_id_from_bar_code(request):
    product = get_object_or_404(Product, bar_code=request.GET.get('bar_code'))
    return HttpResponse(product.id)


@admin_render_view(template_name='invoice_products/print_name.html')
def print_product_name(request, product_id):
    return {'product': get_object_or_404(Product, pk=product_id)}


@admin_render_view(template_name='invoice_products/print_bar_code.html')
def print_product_bar_code(request, product_id):
    return {'product': get_object_or_404(Product, pk=product_id)}


@admin_render_view(template_name='invoice_products/history.html')
def get_product_history(request, product_id):

    product = get_object_or_404(Product, pk=product_id)

    form = forms.HistoryForm(request.GET)

    data = get_clean_data(form)

    date_from = data['date_from']
    date_to = data['date_to']

    sale_items = (
        product
        .saleitem_set
        .filter(invoice__created__date__range=[date_from, date_to])
        .select_related('invoice')
        .order_by('-invoice__created')
    )

    arrival_items = (
        product
        .arrivalitem_set
        .filter(invoice__created__date__range=[date_from, date_to])
        .select_related('invoice')
        .order_by('-invoice__created')
    )

    return {
        'product': product,
        'form': form,
        'sale_items': sale_items,
        'sale_totals': {
            'total': sum([s.subtotal_with_discount for s in sale_items]),
            'qty': sum([s.qty for s in sale_items])
        },
        'arrival_items': arrival_items,
        'arrival_totals': {
            'total': sum([s.subtotal_with_discount for s in arrival_items]),
            'qty': sum([s.qty for s in arrival_items])
        }
    }


@api_view(['GET'])
@staff_member_required
def get_products(request):

    form = forms.SearchProductForm(request.GET)

    page = paginate(
        request,
        Product.objects.active().search(**get_clean_data(form)),
        per_page=20)

    return Response({
        'items': render_to_string('invoices/product-items.html', {
            'request': request,
            'page_obj': page
        }),
        **page.serialize()
    })


@api_view(['GET', 'POST'])
@staff_member_required
def add_product(request):

    form = forms.AddProductForm(request.POST or None)

    status_code = 200

    if request.method == 'POST':

        if form.is_valid():

            product = form.save()

            return Response({
                'message': _('Product added'),
                'product_id': product.pk
            })
        else:
            status_code = 403

    return render(
        request,
        'invoice_products/add.html',
        {'form': form, 'status_code': status_code},
        status=status_code)
