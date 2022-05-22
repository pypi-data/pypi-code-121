
from django import forms
from django.utils.translation import ugettext_lazy as _

from django_select2.forms import Select2Widget

from customers.models import Customer


class CustomerChoiceWidget(Select2Widget):

    empty_label = _('Select customer')


class CustomerChoiceField(forms.ModelChoiceField):

    def __init__(
            self,
            queryset=Customer.objects.all(),
            required=False,
            widget=CustomerChoiceWidget(),
            *args, **kwargs):
        super().__init__(
            queryset=queryset,
            required=required,
            widget=widget,
            *args, **kwargs
        )


class AddCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
