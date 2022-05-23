from django.db import models

from django_drf_utils.exceptions import ConflictError


class RaiseConflictUniqueTogetherValidator:
    def __init__(self, model: models.Model, message: str):
        self.model = model
        self.message = message

    def __call__(self, attrs):
        for constraint in self.model._meta.constraints:
            if isinstance(constraint, models.UniqueConstraint):
                f = {
                    source: attrs[source]
                    for source in constraint.fields
                    if source in attrs
                }
                if f and self.model.objects.filter(**f).exists():
                    raise ConflictError(detail=self.message)
