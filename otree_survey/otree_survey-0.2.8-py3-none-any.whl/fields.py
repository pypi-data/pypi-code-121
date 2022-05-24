import json
import ast

from otree.api import models
import django.db.models as django_models
import django.forms as django_forms
from django.utils.text import capfirst
from django.core import exceptions


class MultipleChoiceStringField(models.StringField):
    """Multiple choice field that saves the data to the database as a JSON string"""

    def formfield(self, **kwargs):
        assert self.choices, "MultipleChoiceStringField requires the choices argument"
        if self.default is not django_models.fields.NOT_PROVIDED:
            # TODO implement set_default
            raise NotImplementedError(
                "MultipleChoiceStringField does not yet support a default value"
            )

        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "widget": django_forms.widgets.CheckboxSelectMultiple,
            "choices": self.get_choices(include_blank=self.blank),
        }
        defaults.update(kwargs)
        return django_forms.MultipleChoiceField(**defaults)

    def validate(self, value, model_instance):
        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages["null"], code="null")

        selected = ast.literal_eval(value)  # convert str to list
        if selected:
            choices = [c[0] for c in self._get_flatchoices()]
            if all(s in choices for s in selected):
                return
            raise exceptions.ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )

        if not self.blank and not selected:
            raise exceptions.ValidationError(self.error_messages["blank"], code="blank")

    def save_form_data(self, instance, data):
        setattr(instance, self.name, json.dumps(data))

    def value_from_object(self, obj):
        value = getattr(obj, self.attname)
        if value is None:
            return None
        return json.loads(value)
