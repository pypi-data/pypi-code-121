
from datetime import datetime

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from djforms.fields import DatePickerField

from services.models import ServiceCategory, ServiceItem, ServiceWorker


class ReportForm(forms.Form):

    date_from = DatePickerField(label=_('Date from'))

    date_to = DatePickerField(label=_('Date to'))

    worker = forms.ModelChoiceField(
        label=_("worker"),
        required=False,
        queryset=ServiceWorker.objects.all())

    def __init__(self, data):

        today = datetime.now().date().strftime(settings.DATE_INPUT_FORMATS[0])

        super().__init__(
            data={
                'date_from': data.get('date_from', today),
                'date_to': data.get('date_to', today),
                'worker': data.get('worker')
            }
        )

        self.is_valid()


class SearchServiceForm(forms.Form):

    code = forms.CharField(required=False)

    query = forms.CharField(required=False)

    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        required=False,
        widget=forms.HiddenInput)

    def clean(self):

        cleaned_data = {}

        for k, v in self.cleaned_data.items():
            if v:
                cleaned_data[k] = v

        return cleaned_data


class AddServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = [
            'category',
            'name',
            'code',
            'price'
        ]


class ManageServiceForm(forms.Form):

    qty = forms.FloatField()

    price = forms.FloatField()

    worker = forms.ModelChoiceField(queryset=ServiceWorker.objects.all())
