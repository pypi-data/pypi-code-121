
from datetime import datetime

from django import forms
from django.apps import apps
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from djforms.fields import DatePickerField
from categories.models import Category


class SearchProductForm(forms.Form):

    code = forms.CharField(required=False)

    bar_code = forms.CharField(required=False)

    query = forms.CharField(required=False)

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.HiddenInput)

    def clean(self):

        cleaned_data = {}

        for k, v in self.cleaned_data.items():
            if v:
                cleaned_data[k] = v

        return cleaned_data


class HistoryForm(forms.Form):

    date_from = DatePickerField(label=_('Date from'))

    date_to = DatePickerField(label=_('Date to'))

    def __init__(self, data):

        today = datetime.now().date().strftime(settings.DATE_INPUT_FORMATS[0])

        super().__init__(
            data={
                'date_from': data.get('date_from', today),
                'date_to': data.get('date_to', today)
            }
        )


class AddProductForm(forms.ModelForm):

    stock = forms.FloatField(label=_('Stock'), min_value=1)

    class Meta:
        model = apps.get_model('products', 'Product')
        fields = [
            'category',
            'name',
            'stock',
            'price_retail'
        ]
