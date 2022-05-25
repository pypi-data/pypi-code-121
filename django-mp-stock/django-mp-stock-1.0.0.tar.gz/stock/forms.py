
from django import forms

from django_select2.forms import Select2MultipleWidget

from categories.models import Category


class StockReportForm(forms.Form):

    categories = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Category.objects.all(),
        widget=Select2MultipleWidget())

    ids = forms.CharField(required=False)
