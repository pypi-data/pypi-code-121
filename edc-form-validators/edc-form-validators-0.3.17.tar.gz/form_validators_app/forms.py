from django import forms
from edc_constants.constants import YES

from edc_form_validators.form_validator import FormValidator
from edc_form_validators.form_validator_mixin import FormValidatorMixin

from .models import TestModel


class TestModelFormValidator(FormValidator):
    def clean(self):
        self.required_if(YES, field="f1", field_required="f2")


class TestModelForm(FormValidatorMixin, forms.ModelForm):

    form_validator = TestModelFormValidator

    class Meta:
        model = TestModel
        fields = "__all__"
