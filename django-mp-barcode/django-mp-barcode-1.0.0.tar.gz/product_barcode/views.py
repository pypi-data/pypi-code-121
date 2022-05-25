
from urllib.parse import urlencode

from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponse, HttpResponseBadRequest

from product_barcode.models import BarCode


@staff_member_required
def get_code(request, code):

    try:
        img = BarCode.get_image(code)
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponseBadRequest(str(e))

    response = HttpResponse(content_type='image/png')

    img.save(response, 'png')

    return response


@staff_member_required
def print_codes(request):
    extra_str = request.GET.get('extra', '')
    codes_str = request.GET.get('codes', '')
    codes = codes_str.split(',') if codes_str else ''
    return render(request, 'barcode/print.html', {
        'codes': codes,
        'extra_str': extra_str
    })


@staff_member_required
def generate_codes(request):

    context = admin.site.each_context(request)

    if request.method == 'POST':
        try:
            count = int(request.POST['count'])
            codes = BarCode.get_solo().get_next_codes(count)
            url = reverse_lazy('barcode:print')
            url += '?' + urlencode({'codes': ','.join(map(str, codes))})
        except Exception:
            messages.error(request, _('Incorrect number'))
            url = request.path

        return redirect(url)

    return render(request, 'barcode/generate.html', context)
