
import logging

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class UniqueConstraint(models.UniqueConstraint):
    def __init__(self, *args, message=None, **kwargs):
        self.message = message or _(
            "%(model_name)s with this %(field_labels)s already exists.")
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs['message'] = self.message
        return path, args, kwargs


class JSONReprMixin():
    def json_repr(self, **values):
        res = dict(
            pk=self.pk,
            resource_name=str(self))
        if hasattr(self, 'slug'):
            res['resource_slug'] = self.slug
        if hasattr(self, 'reference'):
            res['resource_reference'] = self.reference
        res.update(**values)
        return res


class ErrorMessageMixin():
    def validate_unique(self, exclude=None):
        def objgetattr(obj, f):
            v = getattr(obj, f)
            if isinstance(v, models.Model) and v.pk:
                # Retrieve original instance to avoid having not stored
                # values used in instance repr().
                v = v.__class__._default_manager.get(pk=v.pk)
            return v

        try:
            return super().validate_unique(exclude=exclude)
        except ValidationError as e:
            errors = e.update_error_dict({})
            non_field_errors = []
            for error in errors.get(NON_FIELD_ERRORS, []):
                if isinstance(error, ValidationError):
                    if error.code in ('unique', 'unique_together'):
                        model = error.params['model_class']
                        unique_check = error.params['unique_check']
                        unique = next(filter(
                            lambda c: isinstance(c, UniqueConstraint) and
                            c.fields == unique_check, model._meta.constraints
                        ), None)
                        if unique:
                            params = dict(error.params)
                            params.update({
                                f: objgetattr(self, f) for f in unique_check})
                            non_field_errors.append(ValidationError(
                                message=unique.message,
                                code=error.code,
                                params=params))
                            continue
                non_field_errors.append(error)
            errors[NON_FIELD_ERRORS] = non_field_errors
            raise ValidationError(errors)


class PFXModelMixin(JSONReprMixin, ErrorMessageMixin):
    pass
