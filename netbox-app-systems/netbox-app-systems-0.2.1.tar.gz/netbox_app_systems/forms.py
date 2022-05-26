from attr import fields
from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import CommentField
from .models import AppSystem, AppSystemAssignment
from utilities.forms import (
    BootstrapMixin, DynamicModelChoiceField)


class AppSystemForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = AppSystem
        fields = ('name', 'slug', 'description', 'comments', 'tags')


class AppSystemAssignmentForm(BootstrapMixin, forms.ModelForm):
    app_system = DynamicModelChoiceField(queryset=AppSystem.objects.all())

    class Meta:
        model = AppSystemAssignment
        fields = ('app_system',)
