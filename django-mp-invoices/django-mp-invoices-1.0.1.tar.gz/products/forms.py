
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.admin.sites import site

from product_barcode.utils import validate_barcode
from tecdoc.utils import clean_additional_codes

from products.models import Product


class ProductForm(forms.ModelForm):

    def clean_bar_code(self):

        bar_code = self.cleaned_data.get('bar_code')

        if bar_code:
            validate_barcode(bar_code, self.instance.pk)

        return bar_code

    def clean(self):

        data = self.cleaned_data

        try:
            data['additional_codes'] = clean_additional_codes(
                data.get('manufacturer').name,
                data.get('code'),
                data.get('additional_codes'))
        except Exception as e:
            print(e)

        if not data.get('price_wholesale') or not data.get('price_retail'):
            return data

        if data['price_wholesale'] > data['price_retail']:
            raise ValidationError(
                _('Wholesale price can`t be greater than retail price'))

        return data

    class Meta:
        widgets = {
            'manufacturer': AutocompleteSelect(
                Product._meta.get_field('manufacturer').remote_field,
                site,
                attrs={'style': 'width: 200px'}
            )
        }
        model = Product
        fields = '__all__'
