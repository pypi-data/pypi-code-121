
from django import forms
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2Widget

from managers.models import Manager


class ManagerChoiceWidget(Select2Widget):
    empty_label = _('Select manager')


class ManagerChoiceField(forms.ModelChoiceField):

    def __init__(
            self,
            queryset=Manager.objects.all(),
            required=False,
            widget=ManagerChoiceWidget(),
            *args, **kwargs):
        super().__init__(
            queryset=queryset,
            required=required,
            widget=widget,
            *args, **kwargs
        )
